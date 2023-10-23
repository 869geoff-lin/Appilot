from fastapi import FastAPI
from command import cli

# Run websocket serve.
app = FastAPI()
app.websocket("/ws/{client_id}")(cli.websocket_endpoint)
# cli.run()
