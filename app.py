import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

import api
from common.config import GlobalConfig
from services import authentication

app = FastAPI()
app.mount("/api/v1", api.router)
app.mount("/", StaticFiles(directory="./client/build", html=True), name="static")

if __name__ == "__main__":
    authentication.start_daemon()
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=GlobalConfig().server.port,
        reload=True,
        ssl_keyfile="./key.pem",
        ssl_certfile="cert.pem",
    )
