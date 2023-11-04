from flask import Blueprint, request, jsonify
from app import db
from app.databaseModel import User, StudentWeeklySummary, StudentActivity, StudentProfile
from app.status_codes import  HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED_ACCESS,\
    HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT
from functools import wraps
from datetime import datetime
from markupsafe import Markup
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity

# Create the blueprint instance
student_profile_blueprint = Blueprint('students_profile', __name__)

# create a student only decorator to limit access to students only
def student_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
     #    user_id = current_user.get_id()

          user_id = get_jwt_identity()
          user = User.query.filter_by(id=user_id).first()
          user_role = user.role.lower()
          if user and user_role == 'student':
               return func(*args, **kwargs)
          else:
               return jsonify({"error": "You don't have permission to access this page."}), HTTP_401_UNAUTHORIZED_ACCESS
    return wrapper

@student_profile_blueprint.get('/')
@jwt_required()
@student_only
def get_student_profile():
     user_id = get_jwt_identity()
     student_profile = StudentProfile.query.filter_by(student_id=user_id).first()

     if student_profile is None:
          return {"error":"No record found kindly complete your profile"}, HTTP_400_BAD_REQUEST

     if student_profile:
          student_profile_data = { 
               "firstName":student_profile.firstName, 
               "middleName":student_profile.middleName,
               "lastName":student_profile.lastName,
               "startDate":student_profile.startDate.strftime("%Y-%m-%d"), 
               "endDate":student_profile.endDate.strftime("%Y-%m-%d"), 
               "supervisorName": student_profile.supervisorName, 
               "gender":student_profile.gender, 
               "matricNo":student_profile.matricNo, 
               "department":student_profile.department, 
               "course":student_profile.course, 
               "level":student_profile.level, 
               "ppa":student_profile.ppa
          }
          return {"data": student_profile_data}, HTTP_200_OK
     return {"error":"No record found, kindly complete your profile", "nill":True}, HTTP_204_NO_CONTENT
     
@student_profile_blueprint.post('/')
# @login_required
@jwt_required()
@student_only
def student_profile():
    firstName = request.json['firstname'];
    middleName = request.json['middlename']
    lastName = request.json['lastname']
    startDate = request.json['startdate']
    endDate  = request.json['enddate']  
    supervisorName = request.json['supervisorname'] 
    gender  = request.json['gender']   
    matricNo = request.json['matricno']
    department = request.json['department']
    course = request.json['course']
    level = request.json['level']
    ppa = request.json['ppa']

    # clean input
    firstName = Markup.escape(firstName)
    middleName = Markup.escape(middleName)
    lastName = Markup.escape(lastName)
    matricNo =  Markup.escape(matricNo)
    startDate  =  Markup.escape(startDate)
    endDate =  Markup.escape(endDate)
    supervisorName = Markup.escape(supervisorName)
    gender =  Markup.escape(gender)
    department =  Markup.escape(department)
    course = Markup.escape(course)
    level = Markup.escape(level)
    ppa =  Markup.escape(ppa)
   
    if not firstName:
         return{"error": "Firstname is required"}, HTTP_400_BAD_REQUEST
    if not middleName:
         return{"error":"Middlename is required"}, HTTP_400_BAD_REQUEST
    if not lastName:
         return{"error": "Lastname is required"}, HTTP_400_BAD_REQUEST
    if not startDate:
         return{"error": "Start date is required"}, HTTP_400_BAD_REQUEST
    if not endDate:
         return{"error": "End date is required"}, HTTP_400_BAD_REQUEST
    if not supervisorName:
         return{"error": "Supervisor name is required"}, HTTP_400_BAD_REQUEST
    if not gender:
         return{"error": "Gender is required"}, HTTP_400_BAD_REQUEST
    if not matricNo:
         return{"error": "Matriculation is required"}, HTTP_400_BAD_REQUEST
    if not department:
         return{"error": "Department is required"}, HTTP_400_BAD_REQUEST
    if not level:
         return{"error": "Level is required"}, HTTP_400_BAD_REQUEST
    if not ppa:
         return{"error": "Place of Attachment is required"}, HTTP_400_BAD_REQUEST
    
    # Convert the string to a datetime object
    startDate = datetime.strptime(startDate, "%Y-%m-%d")
    endDate = datetime.strptime(endDate, "%Y-%m-%d")

    user_id = get_jwt_identity()
    #     user_id = current_user.get_id()

    try:
          # add user to database
          student_profile = StudentProfile(
               firstName=firstName, middleName=middleName, lastName=lastName,
               startDate=startDate, endDate=endDate, supervisorName= supervisorName, 
               gender=gender, matricNo=matricNo, department=department, 
               course=course, level=level, ppa=ppa, student_id=user_id)
          db.session.add(student_profile)
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