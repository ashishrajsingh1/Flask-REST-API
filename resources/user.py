import logging
from flask import jsonify, render_template, flash
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from flask_login import login_user, logout_user
from passlib.hash import pbkdf2_sha256
from sqlalchemy import or_

from db import db
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST
from flask_cors import CORS

logger = logging.getLogger(__name__)

blp = Blueprint("Users", "users", description="Operations on users")

CORS(blp)

logger.setLevel(logging.INFO)

handler = logging.FileHandler("User.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)


@blp.route("/register")
def register():
    return render_template("Users.html")


@blp.route("/login")
def login():
    return render_template("Login.html")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        try:
            if UserModel.query.filter(
                    or_(
                        UserModel.username == user_data["username"],
                    )
            ).first():
                abort(409, message="A user with that username or email already exists.")

            if len(user_data["password"]) < 8:
                abort(400, message="Password must be at least 8 characters long.")

            user = UserModel(
                username=user_data["username"],
                password=pbkdf2_sha256.hash(user_data["password"]),
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash(f'Account created successfully! You are logged in as {user.username}')
            logger.info(f"User registered successfully: {user_data['username']}")

            return {"message": "User created successfully."}, 201

        except Exception as e:
            logger.error(f"Error during user registration: {str(e)}")
            return {"message": "Internal Server Error"}, 500


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        try:
            user = UserModel.query.filter(
                UserModel.username == user_data["username"]
            ).first()

            if user and pbkdf2_sha256.verify(user_data["password"], user.password):
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                login_user(user)
                flash(f'Success! You are logged in as: {user.username}', category='success')
                logger.info(f"User logged in successfully: {user_data['username']}")
                return {"access_token": access_token, "refresh_token": refresh_token}, 200

            abort(401, message="Invalid credentials.")

        except Exception as e:
            logger.error(f"Error during user login: {str(e)}")
            return {"message": "Internal Server Error"}, 500


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            logout_user()
            flash('You have been successfully logout, Thank You', category='info')
            logger.info(f"User logged out successfully")
            return {"message": "Successfully logged out"}, 200

        except Exception as e:
            logger.error(f"Error during user logout: {str(e)}")
            return {"message": "Internal Server Error"}, 500


def success_response(data, message="Operation successful"):
    return jsonify({"status": "success", "data": {"message": message, "result": data}})


@blp.route("/user/<user_id>")
class User(MethodView):
    def get(self, user_id):
        try:
            user = UserModel.query.get_or_404(user_id)
            data = {"id": user.id, "username": user.username}
            logger.info(f"User information retrieved successfully: {user.username}")
            return success_response(data, "Retrieved successfully")

        except Exception as e:
            logger.error(f"Error while retrieving user information: {str(e)}")
            return {"message": "Internal Server Error"}, 500

    def delete(self, user_id):
        try:
            user = UserModel.query.get_or_404(user_id)
            user.delete()
            logger.info(f"User deleted successfully: {user_id}")
            return success_response({}, "User deleted.")

        except Exception as e:
            logger.error(f"Error during user deletion: {str(e)}")
            return {"message": "Internal Server Error"}, 500


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        try:
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user, fresh=False)
            jti = get_jwt()["jti"]
            BLOCKLIST.add(jti)
            logger.info(f"Token refreshed successfully for user: {current_user}")
            return {"access_token": new_token}, 200

        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            return {"message": "Internal Server Error"}, 500
