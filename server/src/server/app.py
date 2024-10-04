import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket
import logging
from langchain_openai_voice import OpenAIVoiceReactAgent
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

from server.utils import websocket_stream
from server.prompt import INSTRUCTIONS
from server.tools import TOOLS
import os
# openai = os.getenv('OPENAI_API_KEY')
# os.environ['OPENAI_API_KEY']= openai
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
os.environ['USER_AGENT'] = 'myagent'


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    browser_receive_stream = websocket_stream(websocket)
    logger.info(f"browser stream {browser_receive_stream}")

    agent = OpenAIVoiceReactAgent(
        model="gpt-4o-realtime-preview",
        tools=TOOLS,
        instructions=INSTRUCTIONS,
    )
    logger.info(f"agent info {agent}")

    await agent.aconnect(browser_receive_stream, websocket.send_text)


async def homepage(request):
    with open("src/server/static/index.html") as f:
        html = f.read()
        return HTMLResponse(html)


# catchall route to load files from src/server/static


routes = [Route("/", homepage), WebSocketRoute("/ws", websocket_endpoint)]

app = Starlette(debug=True, routes=routes)

app.mount("/", StaticFiles(directory="src/server/static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
