import logging
import sys

from flask import Flask, Response, request, send_from_directory

from api import blueprint
from common.constants import APP_NAME
from common.enums import BrokerageId
from config import GlobalConfig
from services.authentication import AuthenticationService

app = Flask(APP_NAME, static_url_path="", static_folder="client/build")
app.register_blueprint(blueprint)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


@app.route("/", defaults={"path": ""})
def serve(path: str) -> Response:
    access_code = request.args.get("code")
    if access_code:
        auth_service = AuthenticationService()
        auth_service.sign_in(BrokerageId.TD, access_code, request.host_url)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(port=GlobalConfig().server.port, ssl_context="adhoc")
