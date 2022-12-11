import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

# from api import blueprint
# from common.constants import APP_NAME
# from common.enums import BrokerageId
import api
from common.config import GlobalConfig

# from services import authentication
# from services.authentication import AuthenticationService

# app = Flask(APP_NAME, static_url_path="", static_folder="client/build")
app = FastAPI()
app.mount("/api/v1", api.router)
app.mount("/", StaticFiles(directory="./client/build", html=True), name="static")

# app.register_blueprint(blueprint)
# handler = logging.StreamHandler(sys.stdout)
# handler.setFormatter(
#     logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# )
# app.logger.addHandler(handler)
# app.logger.setLevel(logging.INFO)


# @app.route("/", defaults={"path": ""})
# def serve(path: str) -> Response:
#     access_code = request.args.get("code")
#     if access_code:
#         auth_service = AuthenticationService()
#         auth_service.sign_in(BrokerageId.TD, access_code)
#     return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    # authentication.start_daemon()
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=GlobalConfig().server.port,
        reload=True,
        ssl_keyfile="./key.pem",
        ssl_certfile="cert.pem",
    )
