from typing import Any, Dict, Optional

from langchain.tools import BaseTool
from langchain.agents.agent import AgentExecutor
from langchain.agents.conversational.base import ConversationalAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.memory import ReadOnlySharedMemory
from langchain.schema.language_model import BaseLanguageModel

from config import config
from tools.human.tool import HumanTool
from tools.reasoning.tool import ShowReasoningTool, HideReasoningTool
from agent.output_parser import OutputParser
from agent.prompt import (
    AGENT_PROMPT_PREFIX,
    FORMAT_INSTRUCTIONS_TEMPLATE,
)


def create_agent(
    llm: BaseLanguageModel,
    shared_memory: Optional[ReadOnlySharedMemory] = None,
    tools: list[BaseTool] = [],
    callback_manager: Optional[BaseCallbackManager] = None,
    verbose: bool = True,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Dict[str, Any],
) -> AgentExecutor:
    """Instantiate planner for a given task."""

    system_tools = [
        HumanTool(),
        ShowReasoningTool(),
        HideReasoningTool(),
    ]

    tools.extend(system_tools)

    format_instructions = FORMAT_INSTRUCTIONS_TEMPLATE.format(
        natural_language=config.APPILOT_CONFIG.natural_language
    )
    prompt = ConversationalAgent.create_prompt(
        tools,
        prefix=AGENT_PROMPT_PREFIX,
        format_instructions=format_instructions,
    )

    agent = ConversationalAgent(
        llm_chain=LLMChain(
            llm=llm, prompt=prompt, verbose=config.APPILOT_CONFIG.verbose
        ),
        output_parser=OutputParser(),
        allowed_tools=[tool.name for tool in tools],
        **kwargs,
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=shared_memory,
        callback_manager=callback_manager,
        verbose=verbose,
        **(agent_executor_kwargs or {}),
    )
