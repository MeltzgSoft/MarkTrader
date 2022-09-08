from flask import send_from_directory, Flask, Response

app = Flask(__name__, static_url_path="", static_folder="client/build")


@app.route("/", defaults={"path": ""})
def serve(path: str) -> Response:
    return send_from_directory(app.static_folder, "index.html")
