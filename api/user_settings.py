import typing as t

from flask_restx import Namespace, Resource, fields, inputs, reqparse
from werkzeug.exceptions import UnprocessableEntity

from config import UserSettings
from services.authentication import AuthenticationService

api = Namespace("userSettings", description="Access and update user settings")

user_settings_response = api.model(
    "User settings",
    {
        "symbols": fields.List(
            fields.String(),
            required=True,
            description="List of Stock Symbols to use in the application",
        ),
        "endOfDayExit": fields.Boolean(
            required=True,
            attribute="end_of_day_exit",
            description="Whether or not to exit all positions at the end of the day",
        ),
        "enableAutomatedTrading": fields.Boolean(
            required=True,
            attribute="enable_automated_trading",
            description="Whether or not the application should run automated trades",
        ),
        "tradingFrequencySeconds": fields.Integer(
            min=1,
            required=True,
            attribute="trading_frequency_seconds",
            description="How frequently to run the automated trading loop",
        ),
        "positionSize": fields.Float(
            exclusiveMin=0,
            required=True,
            attribute="position_size",
            description="Size of order to buy",
        ),
    },
)

user_settings_request = reqparse.RequestParser()
user_settings_request.add_argument(
    "symbols",
    type=list,
    location="json",
    help="Stock symbols the application should access. If supplied, this list "
    "will replace the existing symbols. An empty list will remove all symbols.",
)
user_settings_request.add_argument(
    "endOfDayExit",
    type=inputs.boolean,
    location="json",
    dest="end_of_day_exit",
    help="If supplied, updates whether or not to exit positions at the end of the day",
)
user_settings_request.add_argument(
    "enableAutomatedTrading",
    type=inputs.boolean,
    location="json",
    dest="enable_automated_trading",
    help="If supplied, updates whether or not automated trading should be enabled",
)
user_settings_request.add_argument(
    "tradingFrequencySeconds",
    type=int,
    location="json",
    dest="trading_frequency_seconds",
    help="If supplied, updates the automated trader's frequency",
)
user_settings_request.add_argument(
    "positionSize",
    type=float,
    location="json",
    dest="position_size",
    help="If supplied, updates the dollar value to buy an option",
)


@api.route("/")
class UserSettingsResource(Resource):
    @api.doc("Get User Settings")
    @api.marshal_with(user_settings_response)
    def get(self) -> t.Dict[str, t.Union[int, float, bool, t.List[str]]]:
        return UserSettings()

    @api.doc("Update User Settings")
    def patch(self) -> None:
        args = user_settings_request.parse_args()
        auth_service = AuthenticationService()
        user_settings = UserSettings()

        symbols = args.get("symbols")
        end_of_day_exit = args.get("end_of_day_exit")
        enable_automated_trading = args.get("enable_automated_trading")
        trading_frequency_seconds = args.get("trading_frequency_seconds")
        position_size = args.get("position_size")

        if symbols is not None:
            user_settings.symbols = [s.upper() for s in symbols]
        if end_of_day_exit is not None:
            user_settings.end_of_day_exit = end_of_day_exit
        if enable_automated_trading is not None:
            if enable_automated_trading and not auth_service.active_tokens:
                raise UnprocessableEntity(
                    "Cannot enable automated trading. Application does not have an active brokerage"
                )
            user_settings.enable_automated_trading = enable_automated_trading
        if trading_frequency_seconds is not None:
            if trading_frequency_seconds < 1:
                raise UnprocessableEntity(
                    "tradingFrequencySeconds must be greater than or equal to 1"
                )
            user_settings.trading_frequency_seconds = trading_frequency_seconds
        if position_size is not None:
            if position_size <= 0:
                raise UnprocessableEntity("positionSize must be greater than 0")
            user_settings.position_size = position_size

        user_settings.save()
