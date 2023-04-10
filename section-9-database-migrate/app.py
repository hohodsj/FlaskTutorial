import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBluePrint
from resources.user import blp as UserBluePrint

from blocklist import BLOCKLIST

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()
    
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL" ,"sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app) # sql alchemy creates connection with the flask app
    migrate = Migrate(app, db)

    with app.app_context():
        # create table if they don't exists
        db.create_all()

    api = Api(app)

    # app.config["JWT_SECRET_KEY"] = 'secret_key' # <-- Not very safe but secrets.SystemRandom().getrandbits(128) changes everytime
    app.config["JWT_SECRET_KEY"] = '56354190815095628503634199202001002652'
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        # if in blocklist request will be terminated
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_headerm, jwt_payload):
        # message send back to client when check_if_token_in_blocklist returns true
        return (jsonify({"description":"The token has been revoked.", "error":"token_revoked"}), 401)

    @jwt.needs_fresh_token_loader
    def token_not_refresh_callback(jwt_header, jwt_payload):
        return (
            jsonify (
                {
                    "description": "THe token is not fresh.",
                    "error": "fresh_token_required"
                }
            )
        )


    @jwt.additional_claims_loader
    # identity from resource.user /login
    def add_claim_tojwt(identity):
        # Look in the database and see whether the user is an admin
        if identity == 1:
            return {"is_admin" : True}
        return {"is_admin" : False}

    # Error handling
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jet_payload):
        return (jsonify({"message" : "The token has expired.", "error" : "token_expired"}), 401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (jsonify({"message" : "Signature verification failed.", "error" : "invalid_token"}), 401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (jsonify({"description" : "Request does not contain an access token.", "error" : "authorization_required"}), 401)

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBluePrint)
    api.register_blueprint(UserBluePrint)

    return app