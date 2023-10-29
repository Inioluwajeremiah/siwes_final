from flask import Blueprint, request, jsonify
from app import db
from app.databaseModel import User, StudentWeeklySummary, StudentActivity, StudentProfile
from app.status_codes import  HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED_ACCESS, HTTP_404_NOT_FOUND, \
    HTTP_204_NO_CONTENT
from functools import wraps
from datetime import datetime
from markupsafe import Markup
from flask_login import login_required, current_user

# Create the blueprint instance
student_blueprint = Blueprint('students', __name__)

# create a student only decorator to limit access to students only
def student_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = current_user.get_id()
        user = User.query.filter_by(id=user_id).first()
        user_role = user.role.lower()
        if user and user_role == 'student':
            return func(*args, **kwargs)
        else:
            return jsonify({"message": "You don't have permission to access this page."}), HTTP_401_UNAUTHORIZED_ACCESS
    return wrapper

# decorator to check if profile is complete
def complete_student_profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = current_user.get_id()
        student_profile = StudentProfile.query.filter_by(student_id=user_id).first()
        
        # if student_profile.firstName is None or student_profile.middmiddleName is None or \
        #     student_profile.lastName is None or student_profile.startDate is None or \
        #     student_profile.endDate is None or student_profile.supervisorName is None or \
        #     student_profile.gender is None or student_profile.matricNo is None or \
        #     student_profile.department is None or student_profile.course is None or \
        #     student_profile.level is None or student_profile.ppa is None:

        if student_profile is None:
            return jsonify({"message": "Complete your profile to continue"}), HTTP_400_BAD_REQUEST
        if student_profile.firstName and student_profile.middleName and \
            student_profile.lastName and student_profile.startDate and \
            student_profile.endDate and student_profile.supervisorName and \
            student_profile.gender and student_profile.matricNo and \
            student_profile.department and student_profile.course and \
            student_profile.level and student_profile.ppa:

            return func(*args, **kwargs)
        else:
            return jsonify({"message": "Complete your profile"}), HTTP_400_BAD_REQUEST

    return wrapper

@student_blueprint.get('/test')
@login_required
@student_only
@complete_student_profile
def getf():
    try:
        return {"message": "test"}
    except Exception as e:
        print(e)
        return {"error": {e}}
    

# get students daily activities
@student_blueprint.route('/daily-activities', methods=['GET'])
@login_required
@student_only
@complete_student_profile
def get_daily_activities(): 
    user_id = current_user.get_id()
    student_activities = StudentActivity.query.filter_by(student_id= user_id).all()

    if student_activities:
        student_daily_activity_data = [ 
           {
               "id": student_activity.id,
                "activity": student_activity.actvity,
                "weekno": student_activity.weekNo,
                "date": student_activity.date.strftime("%Y-%m-%d"),
                # %a, %d %b %Y
                "student_id": student_activity.student_id
            }
            for student_activity in student_activities
        ]
        return{"success": student_daily_activity_data}, HTTP_200_OK
    return {"error": f"No activity found"}, HTTP_404_NOT_FOUND

# get a particular student daily activity
@student_blueprint.route('/daily-activities/<int:id>', methods=['GET'])
@login_required
@student_only
@complete_student_profile
def get_daily_activity(id): 
    user_id = current_user.get_id()
    student_activity = StudentActivity.query.filter_by(id=id, student_id= user_id).first()

    if student_activity:
        student_daily_activity_data = {
            "id": student_activity.id,
            "activity": student_activity.actvity,
            "weekno": student_activity.weekNo,
            "date": student_activity.date.strftime("%Y-%m-%d"),
            # %a, %d %b %Y
            "student_id": student_activity.student_id
        }
           
        return{"success": student_daily_activity_data}, HTTP_200_OK
    return {"error": f"No activity found"}, HTTP_404_NOT_FOUND

# get students weekly activities
@student_blueprint.route('/weekly-activities', methods=['GET'])
@login_required
@student_only
@complete_student_profile
def get_weekly_activities():

    user_id = current_user.get_id()
    
    weekly_activities = StudentWeeklySummary.query.filter_by(student_id=user_id).all()


    if weekly_activities:

        # Query weekly activities per student
        student_weekly_data = [
                {
                "activity_id": student_weekly_activity.id, 
                "summary": student_weekly_activity.summary,
                "departmentAttached": student_weekly_activity.departmentAttached,
                "studentComment": student_weekly_activity.studentComment,
                "weekNo": student_weekly_activity.weekNo,
                "date": student_weekly_activity.date,
            } 
            for student_weekly_activity in weekly_activities
        ]
            
        # Create a response JSON object
        response_data = {
            "data": student_weekly_data
        }

        # Return the response as JSON
        return jsonify(response_data), HTTP_200_OK
    return {"error_message": "No data found"}, HTTP_404_NOT_FOUND

# get a particular student weekly summary
@student_blueprint.route('/weekly-activities/<int:id>', methods=['GET'])
@login_required
@student_only
@complete_student_profile
def get_weekly_activity(id):

    user_id = current_user.get_id()
    
    student_weekly_activity = StudentWeeklySummary.query.filter_by(id=id, student_id=user_id).first()

    if student_weekly_activity:

        # Query weekly activities per student
        student_weekly_data =  {
                "activity_id": student_weekly_activity.id, 
                "summary": student_weekly_activity.summary,
                "department": student_weekly_activity.departmentAttached,
                "comment": student_weekly_activity.studentComment,
                "weekNo": student_weekly_activity.weekNo,
                "date": student_weekly_activity.date.strftime("%Y-%m-%d"),
            } 
        # Create a response JSON object
        response_data = {
            "data": student_weekly_data
        }

        # Return the response as JSON
        return jsonify(response_data), HTTP_200_OK
    return {"error_message": "No data found"}, HTTP_404_NOT_FOUND


# Add daily activity
@student_blueprint.route('/add-daily-activity', methods=['POST'])
@login_required
@student_only
@complete_student_profile
def add_daily_activities():

    activity = request.json.get('activity')
    weekno = request.json.get('weekno')
    date = request.json.get('date')

    activity = Markup.escape(activity)
    weekno = Markup.escape(weekno)
    date = Markup.escape(date)

    if not activity:
        return {"error": "Insert activity"}, HTTP_400_BAD_REQUEST
    if not weekno:
        return {"error": "Insert week number"}, HTTP_400_BAD_REQUEST
    if not date:
        return {"error": "Insert date"}, HTTP_400_BAD_REQUEST

    # import pdb
    # pdb.set_trace()

    user_id = current_user.get_id()

    if user_id:
        date = datetime.strptime(date, '%Y-%m-%d')
        student =  StudentActivity(actvity=activity, weekNo = weekno, date=date, student_id= user_id)
        db.session.add(student)
        db.session.commit()

        return jsonify({'message': 'Record added successfully!'}), HTTP_201_CREATED
  
    return jsonify({'error': 'User not found'}), HTTP_404_NOT_FOUND

# Add weekly activity
@student_blueprint.route('/add-weekly-summary', methods=['POST'])
@login_required
@student_only
@complete_student_profile
def add_weekly_activities():
    user_id = current_user.get_id()
    summary = request.json.get("summary")
    department = request.json["department"]
    comment = request.json["comment"]
    weekNo = request.json.get("weekNo")
    date = request.json.get('date')

    summary = Markup.escape(summary)
    department = Markup.escape(department)
    comment = Markup.escape(comment)
    weekNo = Markup.escape(weekNo)
    date = Markup.escape(date)

    if not summary:
        return {"error": "Insert summary"}, HTTP_400_BAD_REQUEST
    if not department:
        return {"error": "Insert department"}, HTTP_400_BAD_REQUEST
    if not comment:
        return {"error": "Insert comment"}, HTTP_400_BAD_REQUEST
    if not weekNo:
        return {"error": "Insert week number"}, HTTP_400_BAD_REQUEST
    if not date:
        return {"error": "Insert date"}, HTTP_400_BAD_REQUEST
    
    if user_id:
        date = datetime.strptime(date, '%Y-%m-%d')
        user = StudentWeeklySummary(summary=summary, departmentAttached = department, studentComment=comment, weekNo=weekNo, date=date,  student_id=user_id)
        db.session.add(user)
        db.session.commit()
        return {"success": "Weekly summary added successfully"}, HTTP_201_CREATED
    else:
        return {'error': 'Unauthorized access'}, HTTP_401_UNAUTHORIZED_ACCESS
    

# update student daily activity
@student_blueprint.post('update-activity/<int:id>')
@login_required
@student_only
@complete_student_profile
def edit_activity(id):
    user_id = current_user.get_id()
    activity = request.json.get('activity', '')
    weekNo = request.json.get('weekno', '')
    date = request.json.get('date','')

    activity = Markup.escape(activity)
    weekNo = Markup.escape(weekNo)
    date = Markup.escape(date)

    if not activity:
        return {"error": "Insert activity"}, HTTP_400_BAD_REQUEST
    if not weekNo:
        return {"error": "Insert week number"}, HTTP_400_BAD_REQUEST
    if not date:
        return {"error": "Insert date"},  HTTP_400_BAD_REQUEST

    record = StudentActivity.query.filter_by(id=id, student_id=user_id).first()
    date = datetime.strptime(date, "%Y-%m-%d")

    if record:
        record.activity = activity
        record.weekNo = weekNo
        record.date = date
        db.session.commit()

        return {"succcess": "Record updated successfully!"}, HTTP_200_OK
    return {'error': 'Record not found'}, HTTP_404_NOT_FOUND

# update student weekly summary
@student_blueprint.post('update-summary/<int:id>')
@login_required
@student_only
@complete_student_profile
def edit_summary(id):
    user_id = current_user.get_id()
    summary = request.json['summary']
    department = request.json['department']
    comment = request.json['comment']
    weekNo = request.json['weekno']
    date = request.json['date']

    summary = Markup.escape(summary)
    department = Markup.escape(department)
    comment = Markup.escape(comment)
    weekNo = Markup.escape(weekNo)
    date = Markup.escape(date)

    if not summary:
        return {"error": "Insert summary"}, HTTP_400_BAD_REQUEST
    if not department:
        return {"error": "Insert department"}, HTTP_400_BAD_REQUEST
    if not comment:
        return {"error": "Insert comment"}, HTTP_400_BAD_REQUEST
    if not weekNo:
        return {"error": "Insert week number"}, HTTP_400_BAD_REQUEST
    if not date:
        return {"error": "Insert date"}, HTTP_400_BAD_REQUEST

    if user_id:
        date = datetime.strptime(date, '%Y-%m-%d')
        record = StudentWeeklySummary.query.filter_by(id=id, student_id=user_id).first()
        
        if record:
        
            record.summary = summary
            record.departmentAttached = department
            record.studentComment = comment
            record.weekNo = weekNo
            record.date = date
            db.session.commit()

            return {
            "summary": record.summary, "department": record.departmentAttached,
            "comment": record.studentComment, "weekNo":record.weekNo, "date":record.date.strftime("%Y-%m-%d")}, HTTP_200_OK
        return {'error': 'Record not found'}, HTTP_404_NOT_FOUND


# delete daily activity
@student_blueprint.delete('/delete-activity/<int:id>')
@login_required
@student_only
@complete_student_profile
def delete_daily_record(id):
    user_id = current_user.get_id()
    record = StudentActivity.query.filter_by(id=id, student_id=user_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"success": "Record deleted successfully"}), HTTP_200_OK
    return jsonify({
            'error': 'Record not found'
        }), HTTP_404_NOT_FOUND


# delete weekly activity
@student_blueprint.delete('/delete-summary/<int:id>')
@login_required
@student_only
@complete_student_profile
def delete_weekly_record(id):
    user_id = current_user.get_id()
    record = StudentWeeklySummary.query.filter_by(id=id, student_id=user_id).first()

    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"success": "Record deleted successfully"}), HTTP_200_OK
    return jsonify({'error': 'Record not found'}), HTTP_404_NOT_FOUND




# add daily activity schema
# {
#     "activity": "activity 1",
#     "weekno": 1,
#     "date": "2023-11-03"
# }

# add weekly summary
# {
#     "summary": "summary",
#     "department": "departmentAttached",
#     "comment": "studentComment",
#     "weekNo": "weekNo",
#     "date": 'date',
# }