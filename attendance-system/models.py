from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    number = db.Column(db.Integer)
    category = db.Column(db.String(100))
    member_type = db.Column(db.String(100))  # Yuvak, Sampark Karyakar, etc.
    phone = db.Column(db.String(20))
    family_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    dob = db.Column(db.DateTime)
    status = db.Column(db.String(50))  # Job or College
    study = db.Column(db.String(255))
    college_timing = db.Column(db.String(100))
    college_holiday = db.Column(db.String(50))
    job = db.Column(db.String(255))
    job_timing = db.Column(db.String(100))
    job_holiday = db.Column(db.String(50))
    remark = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assignments = db.relationship('Assignment', backref='member', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='member', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Member {self.name}>'

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(50), primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE or ENDED
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendance_records = db.relationship('Attendance', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Session {self.id}>'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), db.ForeignKey('sessions.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    status = db.Column(db.String(20), default='Absent')  # Present or Absent
    arrival_time = db.Column(db.String(20))
    sampark_name = db.Column(db.String(255))
    recorded_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance {self.session_id} - {self.member_id}>'

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    sampark_name = db.Column(db.String(255), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Assignment {self.member_id} -> {self.sampark_name}>'

class Seva(db.Model):
    __tablename__ = 'seva'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    seva_type = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    members = db.relationship('SevaMember', backref='seva', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Seva {self.name}>'

class SevaMember(db.Model):
    __tablename__ = 'seva_members'
    
    id = db.Column(db.Integer, primary_key=True)
    seva_id = db.Column(db.String(50), db.ForeignKey('seva.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    
    member = db.relationship('Member')
    
    def __repr__(self):
        return f'<SevaMember {self.seva_id} - {self.member_id}>'
