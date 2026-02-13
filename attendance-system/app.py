from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from flask_cors import CORS
from config import Config
from models import db, Member, Session, Attendance, Assignment, Seva, SevaMember
from db_helpers import *
from datetime import datetime, timedelta
import json
import uuid
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)
CORS(app)

# Create tables
with app.app_context():
    db.create_all()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_lower(v):
    """Safely convert value to lowercase string"""
    return str(v).strip().lower() if v else ""

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

# MEMBERS API
@app.route('/api/members', methods=['GET'])
def api_get_members():
    """Get all members"""
    try:
        members = db.session.query(Member).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': m.id,
                    'name': m.name,
                    'number': m.number,
                    'phone': m.phone,
                    'family_phone': m.family_phone,
                    'address': m.address,
                    'dob': m.dob,
                    'category': m.category,
                    'member_type': m.member_type,
                    'status': m.status,
                    'study': m.study,
                    'college_timing': m.college_timing,
                    'college_holiday': m.college_holiday,
                    'job': m.job,
                    'job_timing': m.job_timing,
                    'job_holiday': m.job_holiday,
                    'remark': m.remark,
                    'last_updated': m.last_updated.isoformat() if m.last_updated else None
                }
                for m in members
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/members', methods=['POST'])
def api_create_member():
    """Create a new member"""
    try:
        data = request.json
        member = Member(
            name=data.get('name'),
            number=data.get('number'),
            phone=data.get('phone'),
            family_phone=data.get('family_phone'),
            address=data.get('address'),
            dob=data.get('dob'),
            category=data.get('category'),
            member_type=data.get('member_type'),
            status=data.get('status'),
            study=data.get('study'),
            college_timing=data.get('college_timing'),
            college_holiday=data.get('college_holiday'),
            job=data.get('job'),
            job_timing=data.get('job_timing'),
            job_holiday=data.get('job_holiday'),
            remark=data.get('remark')
        )
        db.session.add(member)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Member created successfully',
            'id': member.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/members/<member_id>', methods=['GET'])
def api_get_member(member_id):
    """Get a specific member"""
    try:
        member = db.session.query(Member).filter_by(id=member_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'}), 404
        return jsonify({
            'status': 'success',
            'data': {
                'id': member.id,
                'name': member.name,
                'number': member.number,
                'phone': member.phone,
                'family_phone': member.family_phone,
                'address': member.address,
                'dob': member.dob,
                'category': member.category,
                'member_type': member.member_type,
                'status': member.status,
                'study': member.study,
                'college_timing': member.college_timing,
                'college_holiday': member.college_holiday,
                'job': member.job,
                'job_timing': member.job_timing,
                'job_holiday': member.job_holiday,
                'remark': member.remark,
                'last_updated': member.last_updated.isoformat() if member.last_updated else None
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/members/<member_id>', methods=['PUT'])
def api_update_member(member_id):
    """Update a member"""
    try:
        member = db.session.query(Member).filter_by(id=member_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'}), 404
        
        data = request.json
        for key, value in data.items():
            if hasattr(member, key):
                setattr(member, key, value)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Member updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/members/<member_id>', methods=['DELETE'])
def api_delete_member(member_id):
    """Delete a member and related records (assignments, seva memberships)"""
    try:
        member = db.session.query(Member).filter_by(id=member_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'}), 404

        # Remove any assignments that point to this member as the sampark (other members assigned to them)
        db.session.query(Assignment).filter_by(sampark_name=member.name).delete()
        # Remove Seva membership rows for this member (foreign keys exist)
        db.session.query(SevaMember).filter_by(member_id=member.id).delete()

        # Deleting the member will cascade-delete their own assignments and attendance (models define cascade)
        db.session.delete(member)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Member deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ------------------------
# Suggestions & Relationships
# ------------------------

@app.route('/api/members/<member_id>/suggestions', methods=['GET'])
def api_get_suggestions(member_id):
    """Return suggested sampark karyakar candidates for a yuvak based on address similarity"""
    try:
        member = db.session.query(Member).filter_by(id=member_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'}), 404

        suggestions = []

        # Only generate suggestions for yuvaks
        if safe_lower(getattr(member, 'member_type', '')) == 'yuvak':
            all_members = db.session.query(Member).all()
            for m in all_members:
                role = (m.member_type or "").lower()
                if role in ['sampark karyakar', 'karyakar', 'sanchalak', 'sampark']:
                    score = 0
                    if member.address and m.address:
                        a1 = (member.address or '').lower()
                        a2 = (m.address or '').lower()
                        if a1 in a2 or a2 in a1:
                            score = 1
                    suggestions.append({'name': m.name, 'score': score, 'id': m.id})

            suggestions = sorted(suggestions, key=lambda x: x['score'], reverse=True)

        return jsonify({'status': 'success', 'data': suggestions})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/members/<member_id>/assigned', methods=['GET'])
def api_get_assigned(member_id):
    """Return assigned yuvaks if this member is a sampark/karyakar"""
    try:
        member = db.session.query(Member).filter_by(id=member_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'}), 404

        role_lower = safe_lower(member.member_type or '')
        assigned_list = []
        if role_lower in ['sampark karyakar', 'karyakar', 'sanchalak', 'sampark']:
            assignments = db.session.query(Assignment).filter_by(sampark_name=member.name).all()
            for a in assignments:
                m = db.session.query(Member).get(a.member_id)
                if m:
                    assigned_list.append({'id': m.id, 'name': m.name})

        return jsonify({'status': 'success', 'data': assigned_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/members/assigned_counts', methods=['GET'])
def api_get_assigned_counts():
    """Return assigned counts for sampark-like members"""
    try:
        members = db.session.query(Member).all()
        result = []
        for m in members:
            role_lower = safe_lower(m.member_type or '')
            if role_lower in ['sampark karyakar', 'karyakar', 'sanchalak', 'sampark']:
                count = db.session.query(Assignment).filter_by(sampark_name=m.name).count()
                result.append({'id': m.id, 'name': m.name, 'count': count})
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# SESSIONS API
@app.route('/api/sessions', methods=['GET'])
def api_get_sessions():
    """Get all sessions"""
    try:
        sessions = db.session.query(Session).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': s.id,
                    'date': s.date.isoformat() if s.date else None,
                    'start_time': s.start_time,
                    'end_time': s.end_time,
                    'status': s.status,
                    'created_date': s.created_date.isoformat() if s.created_date else None
                }
                for s in sessions
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def api_create_session():
    """Create a new session"""
    try:
        from datetime import datetime
        import time
        data = request.json
        
        # Generate session ID from date and time with microseconds for uniqueness
        session_date = data.get('date')
        if not session_date:
            return jsonify({'status': 'error', 'message': 'Date is required'}), 400
        
        timestamp = int(time.time() * 1000)  # milliseconds
        session_id = f"S-{session_date.replace('-', '')}-{timestamp}"
        
        # Parse date string to date object
        session_date_obj = datetime.strptime(session_date, '%Y-%m-%d').date()
        
        session = Session(
            id=session_id,
            date=session_date_obj,
            start_time=data.get('start_time'),
            end_time=data.get('end_time'),
            status=data.get('status', 'ACTIVE')
        )
        db.session.add(session)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Session created successfully',
            'id': session.id
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating session: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sessions/<session_id>', methods=['GET'])
def api_get_session(session_id):
    """Get a specific session"""
    try:
        session = db.session.query(Session).filter_by(id=session_id).first()
        if not session:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        return jsonify({
            'status': 'success',
            'data': {
                'id': session.id,
                'date': session.date.isoformat() if session.date else None,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'status': session.status,
                'created_date': session.created_date.isoformat() if session.created_date else None
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sessions/<session_id>/end', methods=['PUT'])
def api_end_session(session_id):
    """End a session"""
    try:
        session = db.session.query(Session).filter_by(id=session_id).first()
        if not session:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        session.status = 'ENDED'
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Session ended successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ATTENDANCE API
@app.route('/api/sessions/<session_id>/attendance', methods=['GET'])
def api_get_attendance(session_id):
    """Get attendance for a session"""
    try:
        attendances = db.session.query(Attendance).filter_by(session_id=session_id).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': a.id,
                    'session_id': a.session_id,
                    'member_id': a.member_id,
                    'member_name': a.member.name if a.member else None,
                    'status': a.status,
                    'sampark_name': a.sampark_name,
                    'recorded_date': a.recorded_date.isoformat() if a.recorded_date else None
                }
                for a in attendances
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sessions/<session_id>/attendance', methods=['POST'])
def api_update_attendance(session_id):
    """Update attendance for a session"""
    try:
        data = request.json
        member_id = data.get('member_id')
        status = data.get('status')
        sampark_name = data.get('sampark_name')
        arrival_time = data.get('arrival_time')
        
        attendance = db.session.query(Attendance).filter_by(
            session_id=session_id,
            member_id=member_id
        ).first()
        
        if not attendance:
            # If arrival_time not provided and status is Present, set current time
            if not arrival_time and status == 'Present':
                arrival_time = datetime.now().strftime('%H:%M')
            attendance = Attendance(
                session_id=session_id,
                member_id=member_id,
                status=status,
                arrival_time=arrival_time,
                sampark_name=sampark_name
            )
            db.session.add(attendance)
        else:
            attendance.status = status
            if sampark_name:
                attendance.sampark_name = sampark_name
            # If arrival_time provided, update it; otherwise if marking Present and no existing time, set current time
            if arrival_time:
                attendance.arrival_time = arrival_time
            elif status == 'Present' and not attendance.arrival_time:
                attendance.arrival_time = datetime.now().strftime('%H:%M')
        
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Attendance updated successfully',
            'id': attendance.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ASSIGNMENTS API
@app.route('/api/assignments', methods=['GET'])
def api_get_assignments():
    """Get all assignments"""
    try:
        assignments = db.session.query(Assignment).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': a.id,
                    'member_id': a.member_id,
                    'member_name': a.member.name if a.member else None,
                    'sampark_name': a.sampark_name,
                    'assigned_date': a.assigned_date.isoformat() if a.assigned_date else None
                }
                for a in assignments
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/assignments', methods=['POST'])
def api_create_assignment():
    """Create an assignment"""
    try:
        data = request.json
        member_id = data.get('member_id')
        sampark_name = data.get('sampark_name')
        
        # Delete existing assignment if any
        db.session.query(Assignment).filter_by(member_id=member_id).delete()
        
        assignment = Assignment(
            member_id=member_id,
            sampark_name=sampark_name
        )
        db.session.add(assignment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Assignment created successfully',
            'id': assignment.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# SEVAS API
@app.route('/api/sevas', methods=['GET'])
def api_get_sevas():
    """Get all sevas"""
    try:
        sevas = db.session.query(Seva).all()
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': s.id,
                    'name': s.name,
                    'seva_type': s.seva_type,
                    'created_date': s.created_date.isoformat() if s.created_date else None,
                    'member_count': len(s.members) if s.members else 0
                }
                for s in sevas
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sevas', methods=['POST'])
def api_create_seva():
    """Create a new seva"""
    try:
        import uuid
        data = request.json
        # generate an id if not provided
        seva_id = str(uuid.uuid4())
        seva = Seva(
            id=seva_id,
            name=data.get('name'),
            seva_type=data.get('seva_type')
        )
        db.session.add(seva)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Seva created successfully',
            'id': seva.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sevas/<seva_id>', methods=['PUT'])
def api_update_seva(seva_id):
    """Update a seva"""
    try:
        seva = db.session.query(Seva).filter_by(id=seva_id).first()
        if not seva:
            return jsonify({'status': 'error', 'message': 'Seva not found'}), 404
        
        data = request.json
        if 'name' in data:
            seva.name = data['name']
        if 'seva_type' in data:
            seva.seva_type = data['seva_type']
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Seva updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sevas/<seva_id>', methods=['DELETE'])
def api_delete_seva(seva_id):
    """Delete a seva"""
    try:
        seva = db.session.query(Seva).filter_by(id=seva_id).first()
        if not seva:
            return jsonify({'status': 'error', 'message': 'Seva not found'}), 404
        
        db.session.delete(seva)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Seva deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Seva members endpoints
@app.route('/api/sevas/<seva_id>/members', methods=['GET'])
def api_get_seva_members(seva_id):
    """Get members assigned to a seva"""
    try:
        seva = db.session.query(Seva).filter_by(id=seva_id).first()
        if not seva:
            return jsonify({'status': 'error', 'message': 'Seva not found'}), 404
        members = []
        for sm in seva.members:
            m = db.session.query(Member).filter_by(id=sm.member_id).first()
            if m:
                members.append({'id': m.id, 'name': m.name})
        return jsonify({'status': 'success', 'data': members})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sevas/<seva_id>/members', methods=['POST'])
def api_add_seva_member(seva_id):
    """Add a member to a seva"""
    try:
        seva = db.session.query(Seva).filter_by(id=seva_id).first()
        if not seva:
            return jsonify({'status': 'error', 'message': 'Seva not found'}), 404
        data = request.json
        member_id = data.get('member_id')
        if member_id is None:
            return jsonify({'status': 'error', 'message': 'member_id is required'}), 400
        member = db.session.query(Member).filter_by(id=member_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found'}), 404
        # Prevent duplicate
        exists = db.session.query(SevaMember).filter_by(seva_id=seva_id, member_id=member_id).first()
        if exists:
            return jsonify({'status': 'success', 'message': 'Member already in seva'}), 200
        seva_member = SevaMember(seva_id=seva_id, member_id=member_id)
        db.session.add(seva_member)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Member added to seva'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sevas/<seva_id>/members/<int:member_id>', methods=['DELETE'])
def api_remove_seva_member(seva_id, member_id):
    """Remove a member from a seva"""
    try:
        deleted = db.session.query(SevaMember).filter_by(seva_id=seva_id, member_id=member_id).delete()
        db.session.commit()
        if deleted == 0:
            return jsonify({'status': 'error', 'message': 'Member not found in seva'}), 404
        return jsonify({'status': 'success', 'message': 'Member removed from seva'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================================================
# LEGACY HTML ROUTES (For backward compatibility)
# ============================================================================

@app.route('/')
def dashboard():
    seva = get_seva_dict()
    return render_template('dashboard.html', seva=seva)

@app.route('/members')
def members():
    members_dict = get_all_members()
    assignments = get_assignments_dict()
    
    # Invert assignments: map sampark/karyakar name -> list of yuvak names
    assigned_map = {}
    for yuvak, info in assignments.items():
        sam = info.get('sampark')
        if not sam: continue
        assigned_map.setdefault(sam, []).append(yuvak)
    
    # Query params for filtering/sorting
    role_filter = request.args.get('role', '').strip()
    sort_opt = request.args.get('sort', '')
    query = request.args.get('q', '').strip()
    
    members_list = list(members_dict.values())
    
    # Build list of available roles for filter select
    roles = sorted({str(m.get('Type') or '').strip() for m in members_list})
    roles = [r for r in roles if r]
    
    # Apply role filter
    if role_filter:
        members_list = [m for m in members_list if safe_lower(m.get('Type')) == safe_lower(role_filter)]
    
    # Apply search query
    if query:
        ql = query.lower()
        def matches(m):
            fields = [
                str(m.get('Yuvak Name') or ''),
                str(m.get('Yuvak Address') or ''),
                str(m.get('Type') or ''),
                str(m.get('Yuvak Phone No.') or ''),
                str(m.get('Family Phone No.') or ''),
                str(m.get('Category') or '')
            ]
            return any(ql in f.lower() for f in fields)
        members_list = [m for m in members_list if matches(m)]
    
    # Apply sorting
    if sort_opt == 'alpha_asc':
        members_list = sorted(members_list, key=lambda m: str(m.get('Yuvak Name') or '').lower())
    elif sort_opt == 'alpha_desc':
        members_list = sorted(members_list, key=lambda m: str(m.get('Yuvak Name') or '').lower(), reverse=True)
    
    return render_template(
        'members.html',
        members=members_list,
        assigned_map=assigned_map,
        roles=roles,
        selected_role=role_filter,
        selected_sort=sort_opt,
        query=query
    )

@app.route('/member/<name>', methods=['GET', 'POST'])
def member_detail(name):
    member_obj = get_member_by_name(name)
    if not member_obj:
        return "Member not found", 404
    
    member = get_member_dict(member_obj)
    
    if request.method == 'POST':
        old_type = (member.get("Type") or "").lower()
        new_type = request.form.get("Type", "").lower()
        
        # Update member in database
        update_member(name, {
            "Category": request.form.get("Category", ""),
            "Yuvak Phone No.": request.form.get("Yuvak Phone No.", ""),
            "Family Phone No.": request.form.get("Family Phone No.", ""),
            "Yuvak Address": request.form.get("Yuvak Address", ""),
            "DOB": request.form.get("DOB", ""),
            "Status": request.form.get("Status", ""),
            "Study": request.form.get("Study", ""),
            "College Timing": request.form.get("College Timing", ""),
            "College Holiday": request.form.get("College Holiday", ""),
            "Job": request.form.get("Job", ""),
            "Job Timing": request.form.get("Job Timing", ""),
            "Job Holiday": request.form.get("Job Holiday", ""),
            "Remark": request.form.get("Remark", ""),
            "Type": request.form.get("Type", "")
        })
        
        if old_type == "yuvak" and new_type != "yuvak":
            set_assignment(member_obj.id, None)
        
        if new_type == "yuvak":
            sampark = request.form.get("sampark_choice")
            if sampark:
                set_assignment(member_obj.id, sampark)
            else:
                set_assignment(member_obj.id, None)
        
        return redirect(url_for("member_detail", name=name))
    
    # Get assigned Sampark Karyakar from database
    assignment = Assignment.query.filter_by(member_id=member_obj.id).first()
    assigned_sampark = assignment.sampark_name if assignment else None
    
    # Get suggested karyakar based on address similarity
    suggested_karyakar = []
    all_karyakar = []
    
    if safe_lower(member.get("Type")) == "yuvak":
        all_members = Member.query.all()
        for m in all_members:
            role = (m.member_type or "").lower()
            if role in ["sampark karyakar", "karyakar", "sanchalak"]:
                all_karyakar.append(m.name)
                # Simple similarity check (address matching)
                if member.get("Yuvak Address") and m.address:
                    if member.get("Yuvak Address").lower() in m.address.lower() or m.address.lower() in member.get("Yuvak Address").lower():
                        suggested_karyakar.append({"name": m.name, "score": 1})
    
    suggested_names = [s["name"] for s in suggested_karyakar[:5]]
    
    # Compute assigned yuvaks if this member is a karyakar/sampark/sanchalak
    assigned_list = []
    role_lower = safe_lower(member.get("Type"))
    if role_lower in ["sampark karyakar", "karyakar", "sanchalak", "sampark"]:
        assignments = Assignment.query.filter_by(sampark_name=name).all()
        for assignment in assignments:
            assigned_member = Member.query.get(assignment.member_id)
            if assigned_member:
                assigned_list.append(assigned_member.name)
    
    return render_template(
        "member_detail.html",
        member=member,
        assigned_sampark=assigned_sampark,
        suggested_karyakar=suggested_karyakar,
        suggested_names=suggested_names,
        all_karyakar=sorted(all_karyakar),
        assigned_list=assigned_list
    )

@app.route('/sessions')
def sessions():
    sessions_list = Session.query.order_by(Session.date.desc()).all()
    sessions_data = []
    for s in sessions_list:
        sessions_data.append({
            'id': s.id,
            'date': s.date.isoformat() if s.date else None,
            'start_time': s.start_time,
            'end_time': s.end_time,
            'status': s.status
        })
    return render_template('sessions_list.html', sessions=sessions_data)

@app.route('/sessions/create', methods=['GET', 'POST'])
def create_session_route():
    if request.method == 'POST':
        date = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        
        if date and start_time:
            # Generate session ID similar to API format
            import time
            timestamp = int(time.time() * 1000)
            session_id = f"S-{date.replace('-', '')}-{timestamp}"
            
            # Create session
            session_date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            session = Session(
                id=session_id,
                date=session_date_obj,
                start_time=start_time,
                end_time=end_time,
                status='ACTIVE'
            )
            db.session.add(session)
            db.session.commit()
            
            return redirect(url_for('session_attendance', session_id=session_id))
    
    return render_template('create_session.html')

@app.route('/sessions/<session_id>', methods=['GET', 'POST'])
def session_attendance(session_id):
    session_obj = get_session(session_id)
    if not session_obj:
        return "Session not found", 404
    
    members_dict = get_all_members()
    assignments = get_assignments_dict()
    
    # Get attendance for this session
    attendance_records = Attendance.query.filter_by(session_id=session_id).all()
    attendance_dict = {}
    for att in attendance_records:
        member = Member.query.get(att.member_id)
        if member:
            attendance_dict[member.name] = {
                "status": att.status,
                "time": att.arrival_time
            }
    
    session = get_session_dict(session_obj)
    if not session:
        session = {
            'id': session_obj.id,
            'date': session_obj.date.isoformat() if session_obj.date else None,
            'start_time': session_obj.start_time,
            'end_time': session_obj.end_time,
            'status': session_obj.status,
            'attendance': {}
        }
    session['attendance'] = attendance_dict
    
    if request.method == 'POST':
        # Update attendance
        for name in members_dict:
            if name in request.form:
                time_field = request.form.get(f"{name}_time", "")
                update_attendance(session_id, name, "Present", time_field if time_field else None)
            else:
                update_attendance(session_id, name, "Absent", None)
        return redirect(url_for('session_attendance', session_id=session_id))
    
    # Get previous session attendance
    prev_present = {name: False for name in members_dict}
    if session_obj.date:
        prev_session = Session.query.filter(
            Session.date < session_obj.date,
            Session.status == 'ENDED'
        ).order_by(Session.date.desc()).first()
        
        if prev_session:
            prev_attendance = Attendance.query.filter_by(session_id=prev_session.id).all()
            for att in prev_attendance:
                member = Member.query.get(att.member_id)
                if member and att.status == "Present":
                    prev_present[member.name] = True
    
    # Apply filtering and sorting
    query = request.args.get("q", "").strip().lower()
    selected_role = request.args.get("role", "").strip()
    selected_sort = request.args.get("sort", "").strip()
    
    filtered_members = dict(members_dict)
    
    if query:
        filtered_members = {
            name: m for name, m in filtered_members.items()
            if query in safe_lower(name) or query in safe_lower(m.get("Yuvak Address", ""))
        }
    
    if selected_role:
        filtered_members = {
            name: m for name, m in filtered_members.items()
            if safe_lower(m.get("Type")) == safe_lower(selected_role)
        }
    
    if selected_sort == "alpha_asc":
        filtered_members = dict(sorted(filtered_members.items(), key=lambda x: x[0].lower()))
    elif selected_sort == "alpha_desc":
        filtered_members = dict(sorted(filtered_members.items(), key=lambda x: x[0].lower(), reverse=True))
    
    roles = sorted(set(safe_lower(m.get("Type")) for m in members_dict.values() if m.get("Type")))
    
    return render_template(
        "session_attendance.html",
        session=session,
        session_id=session_id,
        members=filtered_members,
        all_members=members_dict,
        assignments=assignments,
        prev_present=prev_present,
        query=query,
        selected_role=selected_role,
        selected_sort=selected_sort,
        roles=roles
    )

@app.route('/sessions/<session_id>/end', methods=['POST'])
def end_session_route(session_id):
    if end_session(session_id):
        return redirect(url_for('session_attendance', session_id=session_id))
    return "Session not found", 404

@app.route('/seva')
def seva_list():
    seva = get_seva_dict()
    members = get_all_members()
    return render_template("seva_list.html", seva=seva, members=members)

@app.route('/seva/create', methods=['GET', 'POST'])
def create_seva_route():
    members = get_all_members()
    
    if request.method == 'POST':
        seva_id = str(uuid.uuid4())[:8]
        seva_name = request.form.get("seva_name", "")
        seva_type = request.form.get("seva_type", "")
        selected_members = request.form.getlist("members")
        
        create_seva(seva_id, seva_name, seva_type, selected_members)
        return redirect(url_for("seva_list"))
    
    return render_template("create_seva.html", members=members)

@app.route('/seva/<seva_id>/edit', methods=['GET', 'POST'])
def edit_seva_route(seva_id):
    seva_data = get_seva_dict()
    members = get_all_members()
    seva = seva_data.get(seva_id)
    
    if not seva:
        return "Seva not found", 404
    
    if request.method == 'POST':
        seva_name = request.form.get("seva_name", "")
        seva_type = request.form.get("seva_type", "")
        selected_members = request.form.getlist("members")
        
        update_seva(seva_id, seva_name, seva_type, selected_members)
        return redirect(url_for("seva_list"))
    
    return render_template("edit_seva.html", seva_id=seva_id, seva=seva, members=members)

@app.route('/seva/<seva_id>/delete', methods=['POST'])
def delete_seva_route(seva_id):
    if delete_seva(seva_id):
        return redirect(url_for("seva_list"))
    return "Seva not found", 404

@app.route('/reports/session/<session_id>')
def session_report(session_id):
    session_obj = get_session(session_id)
    if not session_obj:
        return "Session not found", 404
    
    members_dict = get_all_members()
    
    # Get attendance for this session
    attendance_records = Attendance.query.filter_by(session_id=session_id).all()
    
    # Build report list with arrival times (same structure as PDF route)
    report = []  # list of {name, role, status, arrival_time}
    role_summary = {}

    attendance_map = {att.member_id: att for att in attendance_records}

    for member_name, member_data in members_dict.items():
        member_obj = Member.query.filter_by(name=member_name).first()
        if not member_obj:
            continue

        att = attendance_map.get(member_obj.id)
        if att:
            status = att.status
            arrival_time = att.arrival_time or ''
        else:
            status = 'Absent'
            arrival_time = ''

        role = member_data.get('Type', 'Unknown')
        member_timing = member_data.get('College Timing') or member_data.get('Job Timing') or ''

        report.append({
            'name': member_name,
            'role': role,
            'status': status,
            'arrival_time': arrival_time,
            'member_timing': member_timing
        })

        role_summary.setdefault(role, {'Present': 0, 'Absent': 0})
        if status == 'Present':
            role_summary[role]['Present'] += 1
        else:
            role_summary[role]['Absent'] += 1
    
    session = get_session_dict(session_obj)
    if not session:
        session = {
            'id': session_obj.id,
            'date': session_obj.date.isoformat() if session_obj.date else None,
            'start_time': session_obj.start_time,
            'end_time': session_obj.end_time,
            'status': session_obj.status
        }
    
    return render_template(
        "session_report.html",
        session=session,
        session_id=session_id,
        report=report,
        role_summary=role_summary
    )

@app.route('/reports/session/<session_id>/pdf')
def session_report_pdf(session_id):
    # Render the session report HTML and convert to PDF for an identical look to the in-app report
    session_obj = get_session(session_id)
    if not session_obj:
        return "Session not found", 404

    members_dict = get_all_members()
    attendance_records = Attendance.query.filter_by(session_id=session_id).all()

    # Build report with arrival times
    report = []  # list of {name, role, status, arrival_time}
    role_summary = {}

    # Map existing attendance by member_id for quick lookup
    attendance_map = {att.member_id: att for att in attendance_records}

    # Include all members (present or absent). For present, include arrival_time; for absent, arrival_time is ''
    for member_name, member_data in members_dict.items():
        member_obj = Member.query.filter_by(name=member_name).first()
        if not member_obj:
            continue

        att = attendance_map.get(member_obj.id)
        if att:
            status = att.status
            arrival_time = att.arrival_time or ''
        else:
            status = 'Absent'
            arrival_time = ''

        role = member_data.get('Type', 'Unknown')
        # Prefer college timing, else job timing
        member_timing = member_data.get('College Timing') or member_data.get('Job Timing') or ''

        # Append to report list
        report.append({
            'name': member_name,
            'role': role,
            'status': status,
            'arrival_time': arrival_time,
            'member_timing': member_timing
        })

        # Update role summary counts
        role_summary.setdefault(role, {'Present': 0, 'Absent': 0})
        if status == 'Present':
            role_summary[role]['Present'] += 1
        else:
            role_summary[role]['Absent'] += 1

    # Render HTML template
    from datetime import datetime
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html = render_template(
        "session_report.html",
        session=session_obj if isinstance(session_obj, dict) else get_session_dict(session_obj),
        session_id=session_id,
        report=report,
        role_summary=role_summary,
        generated_at=generated_at
    )

    # Convert HTML -> PDF using xhtml2pdf
    try:
        from xhtml2pdf import pisa
    except Exception as e:
        print("xhtml2pdf not installed:", e)
        return "PDF generation dependency missing (xhtml2pdf). Please run `pip install xhtml2pdf`.", 501

    buf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buf)
    if pisa_status.err:
        print("pisa error:", pisa_status.err)
        return "Failed to generate PDF", 500

    buf.seek(0)
    return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=f'session_{session_id}_report.pdf')

# API: session report
@app.route('/api/sessions/<session_id>/report', methods=['GET'])
def api_get_session_report(session_id):
    """Return session report as JSON"""
    try:
        session_obj = get_session(session_id)
        if not session_obj:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404

        members_dict = get_all_members()
        attendance_records = Attendance.query.filter_by(session_id=session_id).all()

        report = {"Present": [], "Absent": []}
        role_summary = {}

        for att in attendance_records:
            member = Member.query.get(att.member_id)
            if member:
                member_name = member.name
                member_data = members_dict.get(member_name, {})
                role = member_data.get("Type", "Unknown")
                status = att.status
                report[status].append({"name": member_name, "role": role, "id": member.id})
                if role not in role_summary:
                    role_summary[role] = {"Present": 0, "Absent": 0}
                role_summary[role][status] += 1

        # Mark members without attendance as Absent
        for member_name, member_data in members_dict.items():
            member_obj = Member.query.filter_by(name=member_name).first()
            if member_obj:
                if not any(att.member_id == member_obj.id for att in attendance_records):
                    role = member_data.get("Type", "Unknown")
                    report["Absent"].append({"name": member_name, "role": role, "id": member_obj.id})
                    if role not in role_summary:
                        role_summary[role] = {"Present": 0, "Absent": 0}
                    role_summary[role]["Absent"] += 1

        session = get_session_dict(session_obj)
        if not session:
            session = {
                'id': session_obj.id,
                'date': session_obj.date.isoformat() if session_obj.date else None,
                'start_time': session_obj.start_time,
                'end_time': session_obj.end_time,
                'status': session_obj.status
            }

        return jsonify({'status': 'success', 'data': {'session': session, 'report': report, 'role_summary': role_summary}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# MONTHLY REPORTS API
@app.route('/api/reports/monthly', methods=['GET'])
def api_monthly_report():
    """Get monthly attendance report data as JSON"""
    try:
        members_dict = get_all_members()
        
        # Get months parameter from query string
        months = int(request.args.get('months', 1))
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*months)
        
        # Filter sessions by date range
        filtered_sessions = Session.query.filter(
            Session.status == 'ENDED',
            Session.date >= start_date.date(),
            Session.date <= end_date.date()
        ).order_by(Session.date).all()
        
        # Initialize data structures
        leadership_absent = {}  # Sampark Karyakar, Karyakar, Sanchalak
        yuvak_absent = {}      # Yuvak members
        summary = {}
        
        # Initialize summary for all categories
        for category in ["Sampark Karyakar", "Karyakar", "Sanchalak", "Yuvak"]:
            summary[category] = {"total_members": 0, "present": 0, "absent": 0}
        
        # Track members to count unique ones
        member_attendance = {}
        
        # Process each session
        for session_obj in filtered_sessions:
            session_date = session_obj.date.isoformat() if session_obj.date else ""
            attendance_records = Attendance.query.filter_by(session_id=session_obj.id).all()
            
            # Process attendance records
            for att in attendance_records:
                member = Member.query.get(att.member_id)
                if not member:
                    continue
                
                member_name = member.name
                member_data = members_dict.get(member_name, {})
                role = str(member_data.get("Type", "Unknown")).strip()
                status = att.status
                
                # Initialize member tracking
                if member_name not in member_attendance:
                    member_attendance[member_name] = {
                        "role": role,
                        "present": 0,
                        "absent": 0,
                        "present_dates": [],
                        "absence_dates": []
                    }
                
                # Count attendance
                if status == "Present":
                    member_attendance[member_name]["present"] += 1
                    member_attendance[member_name]["present_dates"].append(session_date)
                else:
                    member_attendance[member_name]["absent"] += 1
                    member_attendance[member_name]["absence_dates"].append(session_date)
        
        # Organize by category
        for member_name, data in member_attendance.items():
            role = data["role"]
            
            if role == "Yuvak":
                yuvak_absent[member_name] = {
                    "present_dates": data["present_dates"],
                    "absence_dates": data["absence_dates"],
                    "present_count": data["present"],
                    "absence_count": data["absent"]
                }
                summary["Yuvak"]["total_members"] += 1
                summary["Yuvak"]["present"] += data["present"]
                summary["Yuvak"]["absent"] += data["absent"]
            elif role in ["Sampark Karyakar", "Karyakar", "Sanchalak"]:
                leadership_absent[member_name] = {
                    "role": role,
                    "present_dates": data["present_dates"],
                    "absence_dates": data["absence_dates"],
                    "present_count": data["present"],
                    "absence_count": data["absent"]
                }
                summary[role]["total_members"] += 1
                summary[role]["present"] += data["present"]
                summary[role]["absent"] += data["absent"]
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_sessions': len(filtered_sessions),
                'leadership_absent': leadership_absent,
                'yuvak_absent': yuvak_absent,
                'summary': summary,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'selected_months': months
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/reports/monthly')
def monthly_report():
    members_dict = get_all_members()

    members_dict = get_all_members()
    
    # Get months parameter from query string
    months = int(request.args.get('months', 1))
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30*months)
    
    # Filter sessions by date range
    filtered_sessions = Session.query.filter(
        Session.status == 'ENDED',
        Session.date >= start_date.date(),
        Session.date <= end_date.date()
    ).order_by(Session.date).all()
    
    # Initialize data structures
    leadership_absent = {}  # Sampark Karyakar, Karyakar, Sanchalak
    yuvak_absent = {}      # Yuvak members
    summary = {}
    
    # Initialize summary for all categories
    for category in ["Sampark Karyakar", "Karyakar", "Sanchalak", "Yuvak"]:
        summary[category] = {"total_members": 0, "present": 0, "absent": 0}
    
    # Track members to count unique ones
    member_attendance = {}
    
    # Process each session
    for session_obj in filtered_sessions:
        session_date = session_obj.date.isoformat() if session_obj.date else ""
        attendance_records = Attendance.query.filter_by(session_id=session_obj.id).all()
        
        # Process attendance records
        for att in attendance_records:
            member = Member.query.get(att.member_id)
            if not member:
                continue
            
            member_name = member.name
            member_data = members_dict.get(member_name, {})
            role = str(member_data.get("Type", "Unknown")).strip()
            status = att.status
            
            # Initialize member tracking
            if member_name not in member_attendance:
                member_attendance[member_name] = {
                    "role": role,
                    "present": 0,
                    "absent": 0,
                    "present_dates": [],
                    "absence_dates": []
                }
            
            # Count attendance
            if status == "Present":
                member_attendance[member_name]["present"] += 1
                member_attendance[member_name]["present_dates"].append(session_date)
            else:
                member_attendance[member_name]["absent"] += 1
                member_attendance[member_name]["absence_dates"].append(session_date)
    
    # Organize by category
    for member_name, data in member_attendance.items():
        role = data["role"]
        
        if role == "Yuvak":
            yuvak_absent[member_name] = {
                "present_dates": data["present_dates"],
                "absence_dates": data["absence_dates"],
                "present_count": data["present"],
                "absence_count": data["absent"]
            }
            summary["Yuvak"]["total_members"] += 1
            summary["Yuvak"]["present"] += data["present"]
            summary["Yuvak"]["absent"] += data["absent"]
        elif role in ["Sampark Karyakar", "Karyakar", "Sanchalak"]:
            leadership_absent[member_name] = {
                "role": role,
                "present_dates": data["present_dates"],
                "absence_dates": data["absence_dates"],
                "present_count": data["present"],
                "absence_count": data["absent"]
            }
            summary[role]["total_members"] += 1
            summary[role]["present"] += data["present"]
            summary[role]["absent"] += data["absent"]
    
    return render_template(
        "monthly_report.html",
        total_sessions=len(filtered_sessions),
        leadership_absent=leadership_absent,
        yuvak_absent=yuvak_absent,
        summary=summary,
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        selected_months=months
    )

@app.route('/reports/monthly/pdf')
def monthly_report_pdf():
    # Render the monthly report HTML and convert to PDF for consistent formatting
    months = int(request.args.get('months', 1))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)

    # Gather the same data used by the monthly_report page
    filtered_sessions = Session.query.filter(
        Session.status == 'ENDED',
        Session.date >= start_date.date(),
        Session.date <= end_date.date()
    ).order_by(Session.date).all()

    members_dict = get_all_members()
    member_attendance = {}

    for session_obj in filtered_sessions:
        session_date = session_obj.date.isoformat() if session_obj.date else ""
        attendance_records = Attendance.query.filter_by(session_id=session_obj.id).all()

        for att in attendance_records:
            member = Member.query.get(att.member_id)
            if not member:
                continue
            member_name = member.name
            role = str(members_dict.get(member_name, {}).get('Type', 'Unknown')).strip()
            if member_name not in member_attendance:
                member_attendance[member_name] = {
                    'role': role,
                    'present': 0,
                    'absent': 0,
                    'present_dates': [],
                    'absence_dates': []
                }
            if att.status == 'Present':
                member_attendance[member_name]['present'] += 1
                member_attendance[member_name]['present_dates'].append(session_date)
            else:
                member_attendance[member_name]['absent'] += 1
                member_attendance[member_name]['absence_dates'].append(session_date)

    # Render HTML template
    html = render_template(
        'monthly_report.html',
        total_sessions=len(filtered_sessions),
        leadership_absent={},
        yuvak_absent=member_attendance,
        summary={},
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        selected_months=months
    )

    try:
        from xhtml2pdf import pisa
    except Exception as e:
        print("xhtml2pdf not installed:", e)
        return "PDF generation dependency missing (xhtml2pdf). Please run `pip install xhtml2pdf`.", 501

    buf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buf)
    if pisa_status.err:
        print("pisa error:", pisa_status.err)
        return "Failed to generate PDF", 500

    buf.seek(0)
    return send_file(buf, mimetype='application/pdf', as_attachment=True, download_name=f'monthly_report_{months}m.pdf')

if __name__ == '__main__':
    app.run(debug=True)
