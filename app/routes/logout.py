from flask import Blueprint, request, make_response
from flask_login import current_user

from flask_login import login_required, logout_user
from app.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST

logout_blueprint = Blueprint("logout", __name__)

@logout_blueprint.post('/')
@login_required
def logout():
    logout_user()
    return {"success": "User logged out successfully!", "user id": f"{current_user.get_id()}"}
    
