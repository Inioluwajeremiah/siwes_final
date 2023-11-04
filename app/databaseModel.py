from app import db
from flask_login import UserMixin

class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False) 
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    student_profile = db.relationship("StudentProfile", backref="user")
    supervisor_profile = db.relationship("SupervisorProfile", backref="user")
    student_activities = db.relationship("StudentActivity", backref="user")
    student_weekly_summary = db.relationship("StudentWeeklySummary", backref="user")
    supervisor_activities = db.relationship("SupervisorActivity", backref="user")


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    middleName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    startDate = db.Column(db.DateTime, nullable=False)
    endDate   =  db.Column(db.DateTime, nullable=False)
    supervisorName = db.Column(db.String(500), nullable=False)
    gender  = db.Column(db.String(100), nullable=False) 
    matricNo = db.Column(db.String(300), unique=True, nullable=False)
    department = db.Column(db.String(300), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    ppa = db.Column(db.String(300), nullable=False)

    student_id =db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)

    def __repr__(self):
        return f'User: \n{self.id} \n{self.firstName}'
    

class StudentActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actvity = db.Column(db.String(500), nullable=False)
    weekNo = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    

    # Foreign key to link with StudentProfile (based on id)
    student_id =db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    
    def __repr__(self):
        return f'Student activities: \n{self.id} \n{self.activity} \n{self.weekNo} \n{self.date}'
    
# let summary = job for the week
class StudentWeeklySummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(300), nullable=False)
    departmentAttached = db.Column(db.String(70), nullable=False)
    studentComment = db.Column(db.String(200), nullable=False)
    weekNo = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    # relationship
    student_id =db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Weekly summary: \n{self.id} \n{self.summary} \n{self.departmentAttached} \n{self.studentComment}'


class SupervisorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    salutation = db.Column(db.String(50), nullable=False)
    firstName = db.Column(db.String(100), nullable=False)
    middleName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    gender  = db.Column(db.String(100), nullable=False) 
    department = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f'Supervisor Profile: \n{self.id} \n{self.name} \n{self.department}'

    supervisor_id =db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)

class SupervisorActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weekNo = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable = False)
    student_email =  db.Column(db.String(100), nullable=False) 
    remark = db.Column(db.String(200), nullable = False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f'Supervisor Activity: \n{self.id} \n{self.remark} \n{self.date}'
