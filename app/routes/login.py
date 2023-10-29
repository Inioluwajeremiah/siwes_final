from flask import Blueprint, request, make_response, jsonify
from markupsafe import Markup
from app.databaseModel import User
from app import db
from werkzeug.security import   check_password_hash
from flask_login import login_user
from app.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from flask_jwt_extended import set_access_cookies, create_access_token

login_blueprint = Blueprint("login", __name__)

@login_blueprint.post('/')
def login():
    email = request.json['email']
    password = request.json['password']
    rememberme = request.json['rememberme']

    email = Markup.escape(email)
    password = Markup.escape(password)
    rememberme = Markup.escape(rememberme)

    if not email:
        return make_response({"error":"Email field required"}), HTTP_400_BAD_REQUEST
    if not password:
        return make_response({"error":"Password field required"}), HTTP_400_BAD_REQUEST

    try:
        email = email.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            password = check_password_hash(user.password, password)
            if password: 
                # login_user(user)
                response = jsonify({"success": "login successful jwt"})
                access_token = create_access_token(identity=user.id)
                set_access_cookies(response, access_token)
                return response
                # return {"success": "login successfull!"}, HTTP_200_OK
            return {"error":"Password incorrect"}, HTTP_400_BAD_REQUEST
        return {"error": f"{email} not registered!"}, HTTP_400_BAD_REQUEST
    except Exception as e:
        return {"error": f"{e}"}, HTTP_400_BAD_REQUEST
