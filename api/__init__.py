from flask import Blueprint
from flask_restx import Api

from api.authentication import api as auth

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint, title="MarkTrader API", version="1.0", doc="/doc/")

api.add_namespace(auth)
