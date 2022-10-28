import re
import typing as t

from flask import request
from flask_restx import Namespace, Resource, fields
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorList
from werkzeug.exceptions import UnprocessableEntity

from config import UserSettings
from services.authentication import AuthenticationService

api = Namespace("userSettings", description="Access and update user settings")

user_settings_response = api.model(
    "UserSettings",
    {
        "symbols": fields.List(
            fields.String(),
            description="List of Stock Symbols to use in the application",
        ),
        "endOfDayExit": fields.Boolean(
            attribute="end_of_day_exit",
            description="Whether or not to exit all positions at the end of the day",
        ),
        "enableAutomatedTrading": fields.Boolean(
            attribute="enable_automated_trading",
            description="Whether or not the application should run automated trades",
        ),
        "tradingFrequencySeconds": fields.Integer(
            min=1,
            attribute="trading_frequency_seconds",
            description="How frequently to run the automated trading loop",
        ),
        "positionSize": fields.Float(
            exclusiveMin=0,
            attribute="position_size",
            description="Size of order to buy",
        ),
    },
)


@api.route("/")
class UserSettingsResource(Resource):
    @api.doc("Get User Settings")
    @api.marshal_with(user_settings_response)
    def get(self) -> t.Dict[str, t.Union[int, float, bool, t.List[str]]]:
        return t.cast(
            t.Dict[str, t.Union[int, float, bool, t.List[str]]], UserSettings().dict()
        )

    @api.doc("Update User Settings")
    @api.expect(user_settings_response)
    @api.marshal_with(user_settings_response)
    def patch(
        self,
    ) -> tuple[int, dict[str, ErrorList]] | dict[str, int | float | bool | list[str]]:
        args = request.get_json()
        auth_service = AuthenticationService()
        user_settings = UserSettings()

        # convert camel to snake
        args = {
            re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower(): val
            for key, val in args.items()
        }

        enable_automated_trading = args.get("enable_automated_trading")

        if enable_automated_trading is not None:
            if enable_automated_trading and not auth_service.active_tokens:
                raise UnprocessableEntity(
                    "Cannot enable automated trading. Application does not have an active brokerage"
                )

        try:
            user_settings.update(args)
        except ValidationError as e:
            raise UnprocessableEntity(e.errors())
        return t.cast(
            t.Dict[str, t.Union[int, float, bool, t.List[str]]], UserSettings().dict()
        )
