from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from api.endpoints import router as api_router
from api.websocket import socket_manager
from common.settings import settings


app = FastAPI(docs_url='/')
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        socket_manager.disconnect(websocket)

app.include_router(api_router)

if __name__ == '__main__':  # pragma: no cover
    uvicorn.run(
        "app:app",
        host='localhost',
        port=settings.PORT,
    )
