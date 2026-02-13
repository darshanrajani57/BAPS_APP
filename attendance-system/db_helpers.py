"""
Database helper functions for seamless JSON to Database migration
"""

from models import db, Member, Session, Attendance, Assignment, Seva, SevaMember
from datetime import datetime

def get_member_dict(member):
    """Convert Member object to dictionary format matching JSON structure"""
    if not member:
        return None
    return {
        "No": member.number,
        "Category": member.category,
        "Type": member.member_type,
        "Yuvak Name": member.name,
        "Yuvak Phone No.": member.phone,
        "Family Phone No.": member.family_phone,
        "Yuvak Address": member.address,
        "DOB": member.dob.isoformat() if member.dob else None,
        "Status": member.status,
        "Study": member.study,
        "College Timing": member.college_timing,
        "College Holiday": member.college_holiday,
        "Job": member.job,
        "Job Timing": member.job_timing,
        "Job Holiday": member.job_holiday,
        "Last Updated": member.last_updated.isoformat() if member.last_updated else None,
        "Remark": member.remark
    }

def get_all_members():
    """Get all members from database as dictionary"""
    members = Member.query.all()
    return {m.name: get_member_dict(m) for m in members}

def get_member_by_name(name):
    """Get single member by name"""
    return Member.query.filter_by(name=name).first()

def update_member(name, data):
    """Update member in database"""
    member = Member.query.filter_by(name=name).first()
    if not member:
        return False
    
    member.category = data.get('Category', member.category)
    member.member_type = data.get('Type', member.member_type)
    member.phone = data.get('Yuvak Phone No.', member.phone)
    member.family_phone = data.get('Family Phone No.', member.family_phone)
    member.address = data.get('Yuvak Address', member.address)
    
    if data.get('DOB'):
        try:
            member.dob = datetime.fromisoformat(str(data.get('DOB')).replace(' ', 'T'))
        except:
            pass
    
    member.status = data.get('Status', member.status)
    member.study = data.get('Study', member.study)
    member.college_timing = data.get('College Timing', member.college_timing)
    member.college_holiday = data.get('College Holiday', member.college_holiday)
    member.job = data.get('Job', member.job)
    member.job_timing = data.get('Job Timing', member.job_timing)
    member.job_holiday = data.get('Job Holiday', member.job_holiday)
    member.remark = data.get('Remark', member.remark)
    member.last_updated = datetime.utcnow()
    
    db.session.commit()
    return True

def get_assignments_dict():
    """Get all assignments as dictionary"""
    assignments = Assignment.query.all()
    result = {}
    for a in assignments:
        member = Member.query.get(a.member_id)
        if member:
            result[member.name] = {"sampark": a.sampark_name}
    return result

def get_assignment_for_member(member_id):
    """Get assignment for a member"""
    assignment = Assignment.query.filter_by(member_id=member_id).first()
    return assignment.sampark_name if assignment else None

def set_assignment(member_id, sampark_name):
    """Set or update assignment for a member"""
    assignment = Assignment.query.filter_by(member_id=member_id).first()
    if assignment:
        if sampark_name:
            assignment.sampark_name = sampark_name
        else:
            db.session.delete(assignment)
    elif sampark_name:
        assignment = Assignment(member_id=member_id, sampark_name=sampark_name)
        db.session.add(assignment)
    
    db.session.commit()

def get_session_dict(session):
    """Convert Session object to dictionary"""
    if not session:
        return None
    
    attendance = {}
    for att in session.attendance_records:
        member = Member.query.get(att.member_id)
        if member:
            attendance[member.name] = {
                "status": att.status,
                "time": att.arrival_time
            }
    
    return {
        "id": session.id,
        "date": session.date.isoformat() if session.date else None,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "status": session.status,
        "attendance": attendance
    }

def create_session(date, start_time, end_time):
    """Create new session in database"""
    session = Session(
        id=str(__import__('uuid').uuid4()),
        date=datetime.strptime(date, "%Y-%m-%d").date() if isinstance(date, str) else date,
        start_time=start_time,
        end_time=end_time,
        status="ACTIVE"
    )
    db.session.add(session)
    db.session.commit()
    return session.id

def get_session(session_id):
    """Get session by ID"""
    return Session.query.filter_by(id=session_id).first()

def update_attendance(session_id, member_name, status, arrival_time=None):
    """Update attendance record"""
    session = Session.query.filter_by(id=session_id).first()
    member = Member.query.filter_by(name=member_name).first()
    
    if not session or not member:
        return False
    
    attendance = Attendance.query.filter_by(
        session_id=session_id,
        member_id=member.id
    ).first()
    
    if attendance:
        attendance.status = status
        attendance.arrival_time = arrival_time
    else:
        attendance = Attendance(
            session_id=session_id,
            member_id=member.id,
            status=status,
            arrival_time=arrival_time
        )
        db.session.add(attendance)
    
    db.session.commit()
    return True

def end_session(session_id):
    """Mark session as ended"""
    session = Session.query.filter_by(id=session_id).first()
    if session:
        session.status = "ENDED"
        db.session.commit()
        return True
    return False

def get_seva_dict():
    """Get all seva as dictionary"""
    sevas = Seva.query.all()
    result = {}
    for seva in sevas:
        members = [Member.query.get(sm.member_id).name for sm in seva.members]
        result[seva.id] = {
            "name": seva.name,
            "type": seva.seva_type,
            "members": members,
            "created_date": seva.created_date.isoformat() if seva.created_date else None
        }
    return result

def create_seva(seva_id, name, seva_type, member_names):
    """Create new seva"""
    seva = Seva(id=seva_id, name=name, seva_type=seva_type)
    db.session.add(seva)
    
    for member_name in member_names:
        member = Member.query.filter_by(name=member_name).first()
        if member:
            seva_member = SevaMember(seva_id=seva_id, member_id=member.id)
            db.session.add(seva_member)
    
    db.session.commit()

def update_seva(seva_id, name, seva_type, member_names):
    """Update existing seva"""
    seva = Seva.query.filter_by(id=seva_id).first()
    if not seva:
        return False
    
    seva.name = name
    seva.seva_type = seva_type
    
    # Remove old members
    SevaMember.query.filter_by(seva_id=seva_id).delete()
    
    # Add new members
    for member_name in member_names:
        member = Member.query.filter_by(name=member_name).first()
        if member:
            seva_member = SevaMember(seva_id=seva_id, member_id=member.id)
            db.session.add(seva_member)
    
    db.session.commit()
    return True

def delete_seva(seva_id):
    """Delete seva"""
    seva = Seva.query.filter_by(id=seva_id).first()
    if seva:
        db.session.delete(seva)
        db.session.commit()
        return True
    return False
