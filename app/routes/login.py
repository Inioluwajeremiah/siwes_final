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
    role = request.json['role']

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
        # check if user exists
        if user is None:
            return {"error": f"{email} not registered!"}, HTTP_400_BAD_REQUEST
        
        # check if role selected matches user role
        if user.role != role:
            return {"error": f"{email} is not a registered {role}!"}, HTTP_400_BAD_REQUEST
        
        if user and user.role == role:
            password = check_password_hash(user.password, password)
            if password: 
                # login_user(user)
                access_token = create_access_token(identity=user.id)
                return jsonify({"success": "login successful", "access_token": access_token})
                # return {"success": "login successfull!"}, HTTP_200_OK
            return {"error":"Password incorrect"}, HTTP_400_BAD_REQUEST
    except Exception as e:
        return {"error": f"{e}"}, HTTP_400_BAD_REQUEST
