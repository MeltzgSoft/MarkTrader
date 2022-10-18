import typing

from flask_restx import Namespace, Resource, fields
from werkzeug.exceptions import NotFound, UnprocessableEntity

from common.enums import BrokerageId
from config import GlobalConfig

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
        try:
            brokerage_id = BrokerageId(id)
        except ValueError:
            raise UnprocessableEntity(f"Brokerage ID {id} is not recognized")

        brokerage = GlobalConfig().brokerage_map.get(brokerage_id)
        if not brokerage:
            raise NotFound(f"Brokerage auth URI not found for brokerage {id}")

        return {
            "id": brokerage.id.value,
            "name": brokerage.name,
            "uri": brokerage.materialized_auth_url,
        }
