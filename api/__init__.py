from flask import Blueprint
from flask_restx import Api

from api.authentication import api as auth
from api.user_settings import api as user_settings

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(blueprint, title="MarkTrader API", version="1.0", doc="/doc/", validate=True)

api.add_namespace(auth)
api.add_namespace(user_settings)
