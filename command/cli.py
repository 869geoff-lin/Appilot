import sys
from typing import Any
import readline


from langchain.chat_models import ChatOpenAI,AzureChatOpenAI
from langchain.memory import ConversationBufferMemory
import colorama

from callbacks import handlers
from config import config
from i18n import text
from utils import utils
from agent.agent import create_agent
from walrus.toolkit import WalrusToolKit
from k8s.toolkit import KubernetesToolKit
from fastapi import WebSocket

last_error = None

def setup_agent() -> Any:
    config.init()
    colorama.init()

    llm = AzureChatOpenAI(
        deployment_name="gpt-4",
        openai_api_version="2023-03-15-preview",
        verbose=True,
        temperature=0,
        callbacks=[handlers.PrintReasoningCallbackHandler()],
    )

    text.init_system_messages(llm)

    memory = ConversationBufferMemory(memory_key="chat_history")

    enabled_toolkits = [
        toolkit.lower() for toolkit in config.APPILOT_CONFIG.toolkits
    ]

    tools = []
    if "kubernetes" in enabled_toolkits:
        kubernetes_toolkit = KubernetesToolKit(llm=llm)
        tools.extend(kubernetes_toolkit.get_tools())
    elif "walrus" in enabled_toolkits:
        walrus_toolkit = WalrusToolKit(llm=llm)
        tools.extend(walrus_toolkit.get_tools())
    else:
        print(text.get("enable_no_toolkit"))
        sys.exit(1)

    return create_agent(
        llm,
        shared_memory=memory,
        tools=tools,
        verbose=config.APPILOT_CONFIG.verbose,
    )


# def run():
#     global appilot_agent
#     appilot_agent = setup_agent()

#     print(text.get("welcome"))
#     user_query = None
#     while True:
#         user_query = input(">")
#         if utils.is_inform_sent():
#             continue
#         elif user_query == "exit":
#             break
#         elif user_query == "appilot_log":
#             print_last_error()
#             continue
#         elif user_query.startswith("#"):
#             continue
#         elif not user_query.strip():
#             continue

#         try:
#             result = appilot_agent.run(user_query)
#         except handlers.HumanRejectedException as he:
#             utils.print_rejected_message()
#             continue
#         except Exception as e:
#             handle_exception(e)
#             continue

#         utils.print_ai_response(result)


# @app.websocket("/ask/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    appilot_agent = setup_agent()
    await websocket.accept()
    await websocket.send_text(text.get("welcome"))
    while True:
        data = await websocket.receive_text()
        print("query context is:",data)
        user_query = data
        if utils.is_inform_sent():
            continue
        elif user_query == "exit":
            break
        elif user_query == "appilot_log":
            print_last_error()
            res= get_last_error()
            await websocket.send_text(resp(client_id,res))
            continue
        elif user_query.startswith("#"):
            continue
        elif not user_query.strip():
            continue

        try:
            result = appilot_agent.run(user_query)
        except handlers.HumanRejectedException as he:
            utils.print_rejected_message()
            await websocket.send_text(resp(client_id,utils.get_rejected_message()))
            continue
        except Exception as e:
            res=handle_exception2(e)
            await websocket.send_text(resp(client_id,res))
            continue

        utils.print_ai_response(result)
        res = utils.get_ai_response(result)
        await websocket.send_text(resp(client_id,res))


def resp(client_id,msg):
    return f"Client id {client_id}: {msg}"


def handle_exception(e):
    global last_error
    print(text.get("response_prefix"), end="")
    print(text.get("error_occur_message"))
    last_error = e

def handle_exception2(e):
    global last_error
    last_error = e
    print(text.get("response_prefix"), end="")
    print(text.get("error_occur_message"))
    result = text.get("response_prefix")
    result += text.get("error_occur_message")
    return result

def print_last_error():
    if last_error is None:
        print(text.get("response_prefix"), end="")
        print(text.get("no_error_message"))
    else:
        print(last_error)

def get_last_error():
    if last_error is None:
        result = text.get("response_prefix")
        result += text.get("no_error_message")
        return result
    else:
        return last_error
