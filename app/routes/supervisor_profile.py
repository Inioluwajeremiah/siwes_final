from flask import Blueprint, request, jsonify
from app import db
from app.databaseModel import User, SupervisorActivity, SupervisorProfile
from app.status_codes import  HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED_ACCESS,\
    HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT
from functools import wraps
from datetime import datetime
from markupsafe import Markup
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create the blueprint instance
supervisor_profile_blueprint = Blueprint('supervisors_profile', __name__)

# create a supervisor only decorator to limit access to supervisors only
def supervisor_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
     #    user_id = current_user.get_id()

          user_id = get_jwt_identity()
          user = User.query.filter_by(id=user_id).first()
          user_role = user.role.lower()
          if user and user_role == 'supervisor':
               return func(*args, **kwargs)
          else:
               return jsonify({"error": "You don't have permission to access this page."}), HTTP_401_UNAUTHORIZED_ACCESS
    return wrapper

@supervisor_profile_blueprint.get('/')
@jwt_required()
@supervisor_only
def get_supervisor_profile():
     user_id = get_jwt_identity()
     supervisor_profile = SupervisorProfile.query.filter_by(supervisor_id=user_id).first()

     if supervisor_profile:
          supervisor_profile_data = { 
               "firstName":supervisor_profile.firstName, 
               "middleName":supervisor_profile.middleName,
               "lastName":supervisor_profile.lastName,
               "gender":supervisor_profile.gender, 
               "salutation":supervisor_profile.salutation,
               "department":supervisor_profile.department 
          }
          return {"data": supervisor_profile_data}, HTTP_200_OK
     return {"message":"No record found, kindly complete your profile", "nill":True}, HTTP_204_NO_CONTENT
     
@supervisor_profile_blueprint.post('/')
# @login_required
@jwt_required()
@supervisor_only
def supervisor_profile():
    salutation = request.json['salutation']
    firstName = request.json['firstname'];
    middleName = request.json['middlename']
    lastName = request.json['lastname']
    gender  = request.json['gender']   
    department = request.json['department']

    # clean input
    salutation =  Markup.escape(salutation)
    firstName = Markup.escape(firstName)
    middleName = Markup.escape(middleName)
    lastName = Markup.escape(lastName)
    gender =  Markup.escape(gender)
    department =  Markup.escape(department)
   

    if not salutation:
        return{"error": "Salitation is required"}, HTTP_400_BAD_REQUEST
    if not firstName:
         return{"error": "Firstname is required"}, HTTP_400_BAD_REQUEST
    if not middleName:
         return{"error":"Middlename is required"}, HTTP_400_BAD_REQUEST
    if not lastName:
         return{"error": "Lastname is required"}, HTTP_400_BAD_REQUEST
    if not gender:
         return{"error": "Gender is required"}, HTTP_400_BAD_REQUEST
    if not department:
         return{"error": "Department is required"}, HTTP_400_BAD_REQUEST

    user_id = get_jwt_identity()
    #     user_id = current_user.get_id()

    try:
          # add user to database
          supervisor_profile = SupervisorProfile(
               salutation=salutation,
               firstName=firstName, middleName=middleName, lastName=lastName,
               gender=gender,department=department,  supervisor_id=user_id)
          db.session.add(supervisor_profile)
          db.session.commit()
          return {"success": "Profile setup complete"}, HTTP_200_OK
    except Exception as e:
               return {"error": f"Error setting up profile: {e}"}, HTTP_500_INTERNAL_SERVER_ERROR


# register supervisor

   
#    { 
#         "firstName:" "firstname",
#         "middleName": "middlename",
#         "lastName": "lastname",
#         "startDate": "startdate",
#         "endDate": "enddate",  
#         "supervisorName": "supervisorname", 
#         "gender": "gender",   
#         "matricNo": "matricno",
#         "department": "department",
#         "course": "course",
#         "level": "level",
#         "ppa": "ppa"
#     }