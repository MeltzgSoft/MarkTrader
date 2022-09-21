from flask import send_from_directory, Flask, Response

from api import blueprint
from config.app_config import load_config

app = Flask(__name__, static_url_path="", static_folder="client/build")
app.register_blueprint(blueprint)


@app.route("/", defaults={"path": ""})
def serve(path: str) -> Response:
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    config = load_config()
    app.run(port=config.server.port, ssl_context="adhoc")
