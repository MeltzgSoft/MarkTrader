import typing

from flask_restx import Namespace, fields, Resource

from config.app_config import load_config

api = Namespace("auth", description="Brokerage authentication related operations")

auth_uri_response = api.model(
    "Authorization URI Info",
    {
        "id": fields.String(required=True, description="Brokerage ID"),
        "name": fields.String(required=True, description="Brokerage Name"),
        "uri": fields.String(
            required=True, description="URI to navigate to log into Brokerage"
        ),
    },
)


@api.route("/<id>")
@api.param("id", "The Brokerage ID")
@api.response(404, "Brokerage auth URI not found")
class AuthorizationURI(Resource):
    @api.doc("get auth URI")
    @api.marshal_with(auth_uri_response)
    def get(self, id: str) -> typing.Dict[str, str]:
        config = load_config()
        if config.brokerage.id != id:
            api.abort(404)
        return {
            "id": config.brokerage.id,
            "name": config.brokerage.name,
            "uri": config.brokerage.materialized_auth_url,
        }
