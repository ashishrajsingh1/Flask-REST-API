from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_login import LoginManager
from config.config import Config
from db import db
from blocklist import BLOCKLIST
from dotenv import load_dotenv

from resources.user import blp as UserBlueprint
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user_input import blp as DocumentBlueprint
from resources.home import blp as HomeBlueprint
from resources.plotlygraph import blp as GraphBlueprint
from resources.chatjsgraph import blp as ChartjsBlueprint
from resources.Graph import blp as MaingraphBlueprint

login_manager = LoginManager()
login_manager.login_view = 'Users.login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from models import UserModel
    return UserModel.query.get(user_id)


def create_app():
    app = Flask(__name__)
    login_manager.init_app(app)
    load_dotenv()
    app.config.from_object(Config)
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )

    with app.app_context():
        import models  # noqa: F401

        db.create_all()

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(DocumentBlueprint)
    api.register_blueprint(HomeBlueprint)
    api.register_blueprint(GraphBlueprint)
    api.register_blueprint(ChartjsBlueprint)
    api.register_blueprint(MaingraphBlueprint)

    return app
