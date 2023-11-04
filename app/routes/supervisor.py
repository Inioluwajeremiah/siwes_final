from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps
from markupsafe import Markup
from app import db
from datetime import datetime
from app.databaseModel import User, SupervisorProfile, SupervisorActivity, StudentWeeklySummary, StudentActivity, StudentProfile
from app.status_codes import  HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED_ACCESS, HTTP_404_NOT_FOUND, \
    HTTP_204_NO_CONTENT
from datetime import datetime

supervisor_blueprint = Blueprint('supervisor', __name__)

# create a student only decorator to limit access to students only
def supervisor_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # user_id = get_jwt_identity()
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        user_role = user.role.lower()
        if user and user_role == 'supervisor':
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "You don't have permission to access this page."}), HTTP_401_UNAUTHORIZED_ACCESS
    return wrapper

# decorator to check if profile is complete
def complete_supervisor_profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()

        supervisor_profile = SupervisorProfile.query.filter_by(supervisor_id=user_id).first()

        if supervisor_profile is None:
            return jsonify({"error": "Complete your profile to continue"}), HTTP_400_BAD_REQUEST
        if supervisor_profile.firstName and supervisor_profile.salutation and supervisor_profile.middleName and \
            supervisor_profile.lastName and supervisor_profile.gender and supervisor_profile.department:

            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Complete your profile to continue"}), HTTP_400_BAD_REQUEST

    return wrapper

@supervisor_blueprint.get('/weekly-remarks')
@jwt_required()
@supervisor_only
@complete_supervisor_profile
def get_summary():
    user_id = get_jwt_identity()
    weekly_activities = SupervisorActivity.query.filter_by(supervisor_id=user_id).all()
    if weekly_activities:
        # Query weekly activities per student
        supervisor_weekly_data = [
                {
                "activity_id": supervisor_weekly_activity.id, 
                "weekNo": supervisor_weekly_activity.weekNo,
                "date": supervisor_weekly_activity.date.strftime("%Y-%m-%d"),
                "student_email": supervisor_weekly_activity.student_email,
                "remark": supervisor_weekly_activity.remark
            } 
            for supervisor_weekly_activity in weekly_activities
        ]
            
        # Create a response JSON object
        response_data = {
            "data": supervisor_weekly_data
        }

        # Return the response as JSON
        return jsonify(response_data), HTTP_200_OK
    return {"error": "No data found"}, HTTP_404_NOT_FOUND

@supervisor_blueprint.post('/add-weekly-remark')
@jwt_required()
@supervisor_only
@complete_supervisor_profile
def post_summary():
    weekno = request.json['weekno']
    date = request.json['date']
    student_email = request.json['student_email']
    remark = request.json['remark']

    weekno = Markup.escape(weekno)
    date = Markup.escape(date)
    student_email = Markup.escape(student_email)
    remark = Markup.escape(remark)

    if not weekno:
        return {"error": "Insert week number"}, HTTP_400_BAD_REQUEST
    if not date:
        return {"error": "Insert date"}, HTTP_400_BAD_REQUEST
    if not student_email:
        return {"error": "Insert student_email"}, HTTP_400_BAD_REQUEST
    if not remark:
        return {"error": "Insert remark"}, HTTP_400_BAD_REQUEST
    
    # check if student email exist
    student = User.query.filter_by(email = student_email, role='student').first()

    if student is None:
        return {"error": f"{student_email} does not exist. Student should register first"}

    user_id = get_jwt_identity()
    date = datetime.strptime(date, "%Y-%m-%d")

    if user_id:
        supervisor =  SupervisorActivity(weekNo = weekno, date=date, student_email=student_email, remark=remark, supervisor_id= user_id)
        db.session.add(supervisor)
        db.session.commit()

        return jsonify({'success': 'Record added successfully!'}), HTTP_201_CREATED
  
    return jsonify({'error': 'User not found'}), HTTP_404_NOT_FOUND


# @supervisor_blueprint.get('/get_students')
# @jwt_required()
# @supervisor_only
# @complete_supervisor_profile




