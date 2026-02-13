"""
Database initialization script
Run this to create all tables and migrate data from JSON files to PostgreSQL
"""

import json
from datetime import datetime
from app import app, db
from models import Member, Session, Attendance, Assignment, Seva, SevaMember

def init_database():
    """Create all tables in the database"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")

def migrate_members_from_json():
    """Migrate members from members.json to database"""
    with app.app_context():
        try:
            with open('data/members.json', 'r', encoding='utf-8') as f:
                members_data = json.load(f)
            
            count = 0
            for name, member_info in members_data.items():
                # Check if member already exists
                existing = Member.query.filter_by(name=name).first()
                if existing:
                    continue
                
                # Parse DOB
                dob = None
                if member_info.get('DOB'):
                    try:
                        dob = datetime.fromisoformat(str(member_info.get('DOB')).replace(' ', 'T'))
                    except:
                        pass
                
                member = Member(
                    name=name,
                    number=member_info.get('No'),
                    category=member_info.get('Category'),
                    member_type=member_info.get('Type'),
                    phone=str(member_info.get('Yuvak Phone No.', '')) if member_info.get('Yuvak Phone No.') else None,
                    family_phone=str(member_info.get('Family Phone No.', '')) if member_info.get('Family Phone No.') else None,
                    address=member_info.get('Yuvak Address'),
                    dob=dob,
                    status=member_info.get('Status'),
                    study=member_info.get('Study'),
                    college_timing=member_info.get('College Timing'),
                    college_holiday=member_info.get('College Holiday'),
                    job=member_info.get('Job'),
                    job_timing=member_info.get('Job Timing'),
                    job_holiday=member_info.get('Job Holiday'),
                    remark=member_info.get('Remark')
                )
                db.session.add(member)
                count += 1
            
            db.session.commit()
            print(f"✅ Migrated {count} members from JSON to database")
        except FileNotFoundError:
            print("⚠️  members.json not found, skipping migration")
        except Exception as e:
            print(f"❌ Error migrating members: {e}")
            db.session.rollback()

def migrate_assignments_from_json():
    """Migrate assignments from assignments.json to database"""
    with app.app_context():
        try:
            with open('data/assignments.json', 'r', encoding='utf-8') as f:
                assignments_data = json.load(f)
            
            count = 0
            for member_name, assignment_info in assignments_data.items():
                member = Member.query.filter_by(name=member_name).first()
                if not member:
                    continue
                
                sampark_name = assignment_info.get('sampark')
                if not sampark_name:
                    continue
                
                # Check if assignment already exists
                existing = Assignment.query.filter_by(member_id=member.id, sampark_name=sampark_name).first()
                if existing:
                    continue
                
                assignment = Assignment(
                    member_id=member.id,
                    sampark_name=sampark_name
                )
                db.session.add(assignment)
                count += 1
            
            db.session.commit()
            print(f"✅ Migrated {count} assignments from JSON to database")
        except FileNotFoundError:
            print("⚠️  assignments.json not found, skipping migration")
        except Exception as e:
            print(f"❌ Error migrating assignments: {e}")
            db.session.rollback()

def migrate_sessions_from_json():
    """Migrate sessions from sessions.json to database"""
    with app.app_context():
        try:
            with open('data/sessions.json', 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            count = 0
            for session_id, session_info in sessions_data.items():
                # Check if session already exists
                existing = Session.query.filter_by(id=session_id).first()
                if existing:
                    continue
                
                session = Session(
                    id=session_id,
                    date=session_info.get('date'),
                    start_time=session_info.get('start_time'),
                    end_time=session_info.get('end_time'),
                    status=session_info.get('status', 'ACTIVE')
                )
                db.session.add(session)
                count += 1
            
            db.session.commit()
            print(f"✅ Migrated {count} sessions from JSON to database")
        except FileNotFoundError:
            print("⚠️  sessions.json not found, skipping migration")
        except Exception as e:
            print(f"❌ Error migrating sessions: {e}")
            db.session.rollback()

def migrate_attendance_from_json():
    """Migrate attendance from attendance.json and sessions.json to database"""
    with app.app_context():
        try:
            with open('data/sessions.json', 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
            
            count = 0
            for session_id, session_info in sessions_data.items():
                attendance_data = session_info.get('attendance', {})
                
                for member_name, status in attendance_data.items():
                    member = Member.query.filter_by(name=member_name).first()
                    if not member:
                        continue
                    
                    # Check if attendance already exists
                    existing = Attendance.query.filter_by(
                        session_id=session_id,
                        member_id=member.id
                    ).first()
                    if existing:
                        continue
                    
                    attendance = Attendance(
                        session_id=session_id,
                        member_id=member.id,
                        status=status
                    )
                    db.session.add(attendance)
                    count += 1
            
            db.session.commit()
            print(f"✅ Migrated {count} attendance records from JSON to database")
        except FileNotFoundError:
            print("⚠️  sessions.json not found, skipping attendance migration")
        except Exception as e:
            print(f"❌ Error migrating attendance: {e}")
            db.session.rollback()

def migrate_seva_from_json():
    """Migrate seva from seva.json to database"""
    with app.app_context():
        try:
            with open('data/seva.json', 'r', encoding='utf-8') as f:
                seva_data = json.load(f)
            
            count = 0
            for seva_id, seva_info in seva_data.items():
                # Check if seva already exists
                existing = Seva.query.filter_by(id=seva_id).first()
                if existing:
                    continue
                
                seva = Seva(
                    id=seva_id,
                    name=seva_info.get('name'),
                    seva_type=seva_info.get('type')
                )
                db.session.add(seva)
                
                # Add members to seva
                for member_name in seva_info.get('members', []):
                    member = Member.query.filter_by(name=member_name).first()
                    if member:
                        seva_member = SevaMember(seva_id=seva_id, member_id=member.id)
                        db.session.add(seva_member)
                
                count += 1
            
            db.session.commit()
            print(f"✅ Migrated {count} sevas from JSON to database")
        except FileNotFoundError:
            print("⚠️  seva.json not found, skipping migration")
        except Exception as e:
            print(f"❌ Error migrating seva: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("BAPS Attendance System - Database Initialization")
    print("="*60 + "\n")
    
    print("Step 1: Creating database tables...")
    init_database()
    
    print("\nStep 2: Migrating members from JSON...")
    migrate_members_from_json()
    
    print("\nStep 3: Migrating sessions from JSON...")
    migrate_sessions_from_json()
    
    print("\nStep 4: Migrating attendance from JSON...")
    migrate_attendance_from_json()
    
    print("\nStep 5: Migrating assignments from JSON...")
    migrate_assignments_from_json()
    
    print("\nStep 6: Migrating seva from JSON...")
    migrate_seva_from_json()
    
    print("\n" + "="*60)
    print("✅ Database initialization completed!")
    print("="*60 + "\n")
