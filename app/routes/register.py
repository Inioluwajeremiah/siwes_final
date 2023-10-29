from flask import Blueprint, request, make_response
from werkzeug.security import generate_password_hash
from markupsafe import Markup
from app import db
from app.databaseModel import User
from app.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST

register_blueprint = Blueprint("register", __name__)

@register_blueprint.post('/')
def register():
    email = request.json['email']
    password = request.json['password']
    role = request.json['role']

    email = Markup.escape(email)
    password = Markup.escape(password)
    role = Markup.escape(role)

    user = User.query.filter_by(email=email).first()

    if user:
        return{"message": f"{email} already registered"}

    if not email:
        return make_response({"message":"Email field required"}), HTTP_400_BAD_REQUEST
    if not password:
        return make_response({"message":"Password field required"}), HTTP_400_BAD_REQUEST
    if not role:
        return make_response({"message":"Role field required"}), HTTP_400_BAD_REQUEST

    password = generate_password_hash(password)

    try:
        email = email.lower()
        user = User(email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return {"message": f"{role} registration successfull!"}
    except Exception as e:
        return {"message": f"{e}"}

@register_blueprint.get('/')
def t():
    return {"message":"home"}



