from flask import Blueprint, request, make_response, jsonify
from flask_login import current_user

from flask_login import login_required, logout_user
from app.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST
from flask_jwt_extended import unset_jwt_cookies, jwt_required

logout_blueprint = Blueprint("logout", __name__)

@logout_blueprint.post('/')
# @login_required
@jwt_required()
def logout():
    # logout_user()
    response = jsonify({"msg": "logout successful jwt"})
    unset_jwt_cookies(response)
    return response, HTTP_200_OK
    # return {"success": "User logged out successfully!", "user id": f"{current_user.get_id()}"}
    
