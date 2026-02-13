from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import json, re, uuid, os
from datetime import datetime, timedelta
from pdf_utils import generate_pdf, generate_session_pdf_detailed
from config import Config
from models import db, Member, Session, Attendance, Assignment, Seva, SevaMember
from db_helpers import (
    get_all_members, get_member_by_name, update_member, get_assignments_dict,
    get_session, create_session, update_attendance, end_session,
    get_seva_dict, create_seva, update_seva, delete_seva, 
    get_session_dict, set_assignment, get_assignment_for_member
)

ADMIN_NAME = "Jay Soni"
ADMIN_PHONE = "+918401112824"

# ================= APP =================
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

BASE_DIR = "C:/Users/Darshan/Desktop/BAPS_APP/attendance-system"

MEMBERS_FILE = f"{BASE_DIR}/data/members.json"
ASSIGNMENT_FILE = f"{BASE_DIR}/data/assignments.json"
SESSIONS_FILE = f"{BASE_DIR}/data/sessions.json"
SEVA_FILE = f"{BASE_DIR}/data/seva.json"

os.makedirs(f"{BASE_DIR}/reports/pdfs/session", exist_ok=True)
os.makedirs(f"{BASE_DIR}/reports/pdfs/monthly", exist_ok=True)

# ================= HELPERS =================
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_members(): return load_json(MEMBERS_FILE)
def load_assignments(): return load_json(ASSIGNMENT_FILE)
def load_sessions(): return load_json(SESSIONS_FILE)
def load_seva(): return load_json(SEVA_FILE)

def save_members(d): save_json(MEMBERS_FILE, d)
def save_assignments(d): save_json(ASSIGNMENT_FILE, d)
def save_sessions(d): save_json(SESSIONS_FILE, d)
def save_seva(d): save_json(SEVA_FILE, d)

def safe_lower(v): return str(v).strip().lower()

def normalize_phone(p):
    if p is None: return None
    try:
        s = str(p).strip()
    except:
        return None
    return s if s.startswith("+") else "+91" + s

def send_sms(phone, msg):
    # SMS system disabled — log intended message instead of sending
    try:
        p = normalize_phone(phone) or phone
    except:
        p = phone
    print(f"[SMS disabled] To: {p} Msg: {msg}")

def address_tokens(a):
    if not a: return set()
    a = re.sub(r"[^a-z0-9\s]", " ", str(a).lower())
    return set(a.split())

def similarity_score(a1, a2):
    return len(address_tokens(a1) & address_tokens(a2))

# ================= PDF =================
def generate_session_pdf(session_id):
    sessions = load_sessions()
    members = load_members()
    assignments = load_assignments()
    session = sessions.get(session_id)

    if not session or session.get("status") != "ENDED":
        return

    path = f"{BASE_DIR}/reports/pdfs/session/session_{session_id}.pdf"
    generate_session_pdf_detailed(session_id, session, members, assignments, path)

# ================= ROUTES =================

@app.route("/")
def dashboard():
    seva = get_seva_dict()
    return render_template("dashboard.html", seva=seva)

# ---------- MEMBERS ----------
@app.route("/members")
def members():
    members_dict = get_all_members()
    assignments = get_assignments_dict()

    # invert assignments: map sampark/karyakar name -> list of yuvak names
    assigned_map = {}
    for yuvak, info in assignments.items():
        sam = info.get('sampark')
        if not sam: continue
        assigned_map.setdefault(sam, []).append(yuvak)

    # Query params for filtering/sorting
    role_filter = request.args.get('role','').strip()
    sort_opt = request.args.get('sort','')
    query = request.args.get('q','').strip()

    members_list = list(members_dict.values())

    # build list of available roles for filter select
    roles = sorted({ str(m.get('Type') or '').strip() for m in members_list })
    roles = [r for r in roles if r]

    # apply role filter
    if role_filter:
        members_list = [m for m in members_list if str(m.get('Type') or '').strip() == role_filter]

    # apply search query
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

    # apply sorting
    if sort_opt == 'alpha_asc':
        members_list = sorted(members_list, key=lambda m: str(m.get('Yuvak Name') or '').lower())
    elif sort_opt == 'alpha_desc':
        members_list = sorted(members_list, key=lambda m: str(m.get('Yuvak Name') or '').lower(), reverse=True)

    return render_template(
        "members.html",
        members=members_list,
        assigned_map=assigned_map,
        roles=roles,
        selected_role=role_filter,
        selected_sort=sort_opt,
        query=query
    )

@app.route("/member/<name>", methods=["GET","POST"])
def member_detail(name):
    member_obj = get_member_by_name(name)
    if not member_obj:
        return "Member not found", 404
    
    member = {
        "Yuvak Name": member_obj.name,
        "Type": member_obj.member_type,
        "Category": member_obj.category,
        "Yuvak Phone No.": member_obj.phone,
        "Family Phone No.": member_obj.family_phone,
        "Yuvak Address": member_obj.address,
        "DOB": member_obj.dob.isoformat() if member_obj.dob else "",
        "Status": member_obj.status,
        "Study": member_obj.study,
        "College Timing": member_obj.college_timing,
        "College Holiday": member_obj.college_holiday,
        "Job": member_obj.job,
        "Job Timing": member_obj.job_timing,
        "Job Holiday": member_obj.job_holiday,
        "Remark": member_obj.remark
    }

    if request.method == "POST":
        old_type = safe_lower(member.get("Type"))
        new_type = safe_lower(request.form.get("Type"))

        # Update member in database
        update_member(name, {
            "Category": request.form.get("Category",""),
            "Yuvak Phone No.": request.form.get("Yuvak Phone No.",""),
            "Family Phone No.": request.form.get("Family Phone No.",""),
            "Yuvak Address": request.form.get("Yuvak Address",""),
            "DOB": request.form.get("DOB",""),
            "Status": request.form.get("Status",""),
            "Study": request.form.get("Study",""),
            "College Timing": request.form.get("College Timing",""),
            "College Holiday": request.form.get("College Holiday",""),
            "Job": request.form.get("Job",""),
            "Job Timing": request.form.get("Job Timing",""),
            "Job Holiday": request.form.get("Job Holiday",""),
            "Remark": request.form.get("Remark",""),
            "Type": request.form.get("Type","")
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
    assignment = db.session.query(Assignment).filter_by(member_id=member_obj.id).first()
    assigned_sampark = assignment.sampark_name if assignment else None

    suggested_karyakar = []
    all_karyakar = []

    if safe_lower(member.get("Type")) == "yuvak":
        # Get all members from database to find sampark candidates
        all_members = db.session.query(Member).all()
        for m in all_members:
            role = safe_lower(m.member_type)
            if role in ["sampark karyakar", "karyakar", "sanchalak"]:
                all_karyakar.append(m.name)
                score = similarity_score(
                    member.get("Yuvak Address",""),
                    m.address or ""
                )
                if score > 0:
                    suggested_karyakar.append({
                        "name": m.name,
                        "score": score
                    })

        suggested_karyakar = sorted(
            suggested_karyakar,
            key=lambda x: x["score"],
            reverse=True
        )[:5]

    # helper list of suggested names for template rendering
    suggested_names = [s["name"] for s in suggested_karyakar]

    # compute assigned yuvaks if this member is a karyakar/sampark/sanchalak
    assigned_list = []
    role_lower = safe_lower(member.get("Type"))
    if role_lower in ["sampark karyakar", "karyakar", "sanchalak", "sampark"]:
        # Get all assignments where this member is the sampark
        assignments = db.session.query(Assignment).filter_by(sampark_name=name).all()
        for assignment in assignments:
            assigned_member = db.session.query(Member).filter_by(id=assignment.member_id).first()
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

# ---------- SESSIONS ----------
@app.route("/sessions")
def sessions_list():
    sessions = load_sessions()
    now = datetime.now()
    updated = False
    out = []

    for sid, s in sessions.items():
        s.setdefault("attendance", {})
        if s.get("status") == "ACTIVE":
            try:
                end_dt = datetime.strptime(
                    f"{s['date']} {s['end_time']}",
                    "%Y-%m-%d %H:%M"
                )
                if now >= end_dt:
                    s["status"] = "ENDED"
                    updated = True
            except:
                pass

        s["id"] = sid
        out.append(s)

    if updated:
        save_sessions(sessions)

    return render_template("sessions_list.html", sessions=out)

@app.route("/sessions/create", methods=["GET","POST"])
def create_session():
    sessions = load_sessions()
    if request.method == "POST":
        date_str = request.form.get("date", "")
        start_time_str = request.form.get("start_time", "")
        end_time_str = request.form.get("end_time", "")
        
        # Validate date and time are not in the past
        try:
            now = datetime.now()
            session_date = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Check if date is in the past
            if session_date.date() < now.date():
                return "Error: Cannot create session for past dates", 400
            
            # Check if time is in the past for today
            if session_date.date() == now.date():
                start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
                if start_time_obj < now.time():
                    return "Error: Cannot create session for past times. Current system time: " + now.strftime("%H:%M"), 400
        except ValueError as e:
            return f"Error: Invalid date or time format - {e}", 400
        
        sid = str(uuid.uuid4())
        sessions[sid] = {
            "date": date_str,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "status": "ACTIVE",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attendance": {}
        }
        save_sessions(sessions)
        return redirect(url_for("session_attendance", session_id=sid))
    return render_template("create_session.html")


@app.route("/api/upcoming_birthdays")
def api_upcoming_birthdays():
    """Return JSON list of member names whose birthday falls within the
    next 7 days (inclusive) of the provided `date` query param (YYYY-MM-DD).
    If `date` is missing or invalid, uses today's date.
    """
    members = load_members()
    date_str = request.args.get("date")
    try:
        base_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
    except:
        base_date = datetime.now()

    results = []
    for name, m in members.items():
        dob_raw = m.get("DOB")
        if not dob_raw or dob_raw in ["-", "nan", None]:
            continue
        dob = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dob = datetime.strptime(str(dob_raw), fmt)
                break
            except:
                continue
        if not dob:
            continue

        # compute next birthday date (year may roll over)
        month = dob.month
        day = dob.day
        try:
            candidate = datetime(base_date.year, month, day)
        except ValueError:
            # skip invalid dates like Feb 29 on non-leap year
            continue
        if candidate.date() < base_date.date():
            try:
                candidate = datetime(base_date.year + 1, month, day)
            except ValueError:
                continue

        delta_days = (candidate.date() - base_date.date()).days
        if 0 <= delta_days <= 7:
            results.append({"name": name, "birthday": candidate.strftime("%Y-%m-%d"), "in_days": delta_days})

    # sort by upcoming days
    results = sorted(results, key=lambda x: x["in_days"])
    return jsonify(results)

@app.route("/sessions/<session_id>", methods=["GET","POST"])
def session_attendance(session_id):
    sessions = load_sessions()
    members = load_members()
    assignments = load_assignments()
    session = sessions.get(session_id)

    if not session:
        return "Session not found", 404

    session.setdefault("attendance", {})

    if request.method == "POST":
        # Allow editing attendance even after session ends
        # Checkboxes submit only when checked. If checked => Present, else Absent
        for name in members:
            if name in request.form:
                time_field = request.form.get(f"{name}_time", "")
                session["attendance"][name] = {
                    "status": "Present",
                    "time": time_field
                }
            else:
                session["attendance"][name] = {
                    "status": "Absent",
                    "time": None
                }
        save_sessions(sessions)

    # determine previous sabha (most recent session with date < current session date)
    prev_present = {name: False for name in members}
    try:
        cur_date = datetime.strptime(session.get("date",""), "%Y-%m-%d")
    except:
        cur_date = None

    if cur_date:
        latest_prev = None
        latest_prev_dt = None
        for sid, s in sessions.items():
            if sid == session_id: continue
            sdate = s.get("date")
            if not sdate: continue
            try:
                sdt = datetime.strptime(str(sdate).split()[0], "%Y-%m-%d")
            except:
                continue
            if sdt < cur_date:
                if (latest_prev_dt is None) or (sdt > latest_prev_dt):
                    latest_prev_dt = sdt
                    latest_prev = s

        if latest_prev:
            prev_att = latest_prev.get("attendance", {})
            for name in members:
                prev_status = prev_att.get(name)
                # Handle both old format (string) and new format (dict)
                if isinstance(prev_status, dict):
                    prev_present[name] = (prev_status.get("status") == "Present")
                else:
                    prev_present[name] = (prev_status == "Present")

    # Apply filtering and sorting
    query = request.args.get("q", "").strip().lower()
    selected_role = request.args.get("role", "").strip()
    selected_sort = request.args.get("sort", "").strip()

    filtered_members = dict(members)

    # Filter by search query
    if query:
        filtered_members = {
            name: m for name, m in filtered_members.items()
            if query in safe_lower(name) or query in safe_lower(m.get("Yuvak Address", ""))
        }

    # Filter by role
    if selected_role:
        filtered_members = {
            name: m for name, m in filtered_members.items()
            if safe_lower(m.get("Type", "")) == safe_lower(selected_role)
        }

    # Apply sorting
    if selected_sort == "alpha_asc":
        filtered_members = dict(sorted(filtered_members.items(), key=lambda x: safe_lower(x[0])))
    elif selected_sort == "alpha_desc":
        filtered_members = dict(sorted(filtered_members.items(), key=lambda x: safe_lower(x[0]), reverse=True))

    # Get unique roles for dropdown
    roles = sorted(set(safe_lower(m.get("Type", "")) for m in members.values() if m.get("Type")))

    return render_template(
        "session_attendance.html",
        session=session,
        session_id=session_id,
        members=filtered_members,
        all_members=members,
        assignments=assignments,
        prev_present=prev_present,
        query=query,
        selected_role=selected_role,
        selected_sort=selected_sort,
        roles=roles
    )

@app.route("/sessions/<session_id>/end", methods=["POST"])
def end_session(session_id):
    sessions = load_sessions()
    members = load_members()
    assignments = load_assignments()
    session = sessions.get(session_id)

    if not session:
        return "Session not found", 404
    if session["status"] == "ENDED":
        return redirect(url_for("session_attendance", session_id=session_id))

    session["status"] = "ENDED"
    save_sessions(sessions)

    attendance = session.get("attendance", {})

    for name, status_info in attendance.items():
        # Handle both old format (string) and new format (dict with status and time)
        if isinstance(status_info, dict):
            status = status_info.get("status", "Absent")
        else:
            status = status_info
        
        if status != "Absent": continue
        member = members.get(name, {})
        role = safe_lower(member.get("Type"))

        if role == "yuvak":
            sampark = assignments.get(name, {}).get("sampark")
            sampark_member = members.get(sampark)
            # Check sampark status with format handling
            sampark_status = attendance.get(sampark)
            if isinstance(sampark_status, dict):
                sampark_status = sampark_status.get("status")
            
            if sampark_member and sampark_status == "Present":
                send_sms(
                    sampark_member.get("Yuvak Phone No."),
                    f"Yuvak {name} is ABSENT today."
                )
            else:
                send_sms(
                    ADMIN_PHONE,
                    f"Yuvak {name} and Sampark {sampark} are ABSENT."
                )
        else:
            send_sms(
                ADMIN_PHONE,
                f"{member.get('Type')} {name} is ABSENT today."
            )

    generate_session_pdf(session_id)
    return redirect(url_for("session_attendance", session_id=session_id))

# ---------- REPORTS ----------
@app.route("/reports/session/<session_id>")
def session_report(session_id):
    sessions = load_sessions()
    members = load_members()
    session = sessions.get(session_id)

    if not session:
        return "Session not found", 404

    report = {"Present": [], "Absent": []}
    role_summary = {}

    for n, st in session.get("attendance", {}).items():
        # Handle both old format (string) and new format (dict with status and time)
        if isinstance(st, dict):
            status = st.get("status", "Absent")
        else:
            status = st
        
        role = members.get(n, {}).get("Type","Unknown")
        report[status].append({"name": n, "role": role})
        role_summary.setdefault(role, {"Present":0,"Absent":0})
        role_summary[role][status] += 1

    return render_template(
        "session_report.html",
        session=session,
        session_id=session_id,
        report=report,
        role_summary=role_summary
    )

@app.route("/reports/session/<session_id>/pdf")
def download_session_pdf(session_id):
    path = f"{BASE_DIR}/reports/pdfs/session/session_{session_id}.pdf"
    if not os.path.exists(path):
        generate_session_pdf(session_id)
    if not os.path.exists(path):
        return "PDF not available", 404
    return send_file(path, as_attachment=True)

@app.route("/reports/monthly")
def monthly_report():
    sessions = load_sessions()
    members = load_members()
    assignments = load_assignments()
    
    # Get months parameter from query string
    months = int(request.args.get('months', 1))
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30*months)
    
    # Filter sessions by date range
    filtered_sessions = []
    for s in sessions.values():
        if s.get("status") != "ENDED":
            continue
        try:
            session_date = datetime.strptime(s.get("date", ""), "%Y-%m-%d")
            if start_date <= session_date <= end_date:
                filtered_sessions.append(s)
        except:
            continue
    
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
    for session in filtered_sessions:
        session_date = session.get("date", "")
        attendance = session.get("attendance", {})
        
        for member_name, status_info in attendance.items():
            member_data = members.get(member_name, {})
            role = str(member_data.get("Type", "Unknown")).strip()
            
            # Initialize member tracking
            if member_name not in member_attendance:
                member_attendance[member_name] = {
                    "role": role,
                    "present": 0,
                    "absent": 0,
                    "present_dates": [],
                    "absence_dates": []
                }
            
            # Extract status (handle both string and dict formats)
            if isinstance(status_info, dict):
                status = status_info.get("status", "Absent")
            else:
                status = status_info
            
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

@app.route("/reports/monthly/pdf")
def download_monthly_pdf():
    """Generate and download monthly attendance report as PDF with category grouping and absence dates"""
    from reportlab.lib.pagesizes import letter, landscape, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    
    sessions = load_sessions()
    members = load_members()
    
    # Get months parameter
    months = int(request.args.get('months', 1))
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30*months)
    
    # Filter sessions by date range
    filtered_sessions = []
    for s in sessions.values():
        if s.get("status") != "ENDED":
            continue
        try:
            session_date = datetime.strptime(s.get("date", ""), "%Y-%m-%d")
            if start_date <= session_date <= end_date:
                filtered_sessions.append(s)
        except:
            continue
    
    # Initialize data structures
    leadership_absent = {}  # Sampark Karyakar, Karyakar, Sanchalak
    yuvak_absent = {}      # Yuvak members
    summary = {}
    
    # Initialize summary for all categories
    for category in ["Sampark Karyakar", "Karyakar", "Sanchalak", "Yuvak"]:
        summary[category] = {"total_members": 0, "present": 0, "absent": 0}
    
    # Track members
    member_attendance = {}
    
    # Process each session
    for session in filtered_sessions:
        session_date = session.get("date", "")
        attendance = session.get("attendance", {})
        
        for member_name, status_info in attendance.items():
            member_data = members.get(member_name, {})
            role = str(member_data.get("Type", "Unknown")).strip()
            
            # Initialize member tracking
            if member_name not in member_attendance:
                member_attendance[member_name] = {
                    "role": role,
                    "present": 0,
                    "absent": 0,
                    "present_dates": [],
                    "absence_dates": []
                }
            
            # Extract status (handle both string and dict formats)
            if isinstance(status_info, dict):
                status = status_info.get("status", "Absent")
            else:
                status = status_info
            
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
    
    # Create PDF with A4 landscape for better width
    pdf_path = f"{BASE_DIR}/reports/pdfs/monthly/monthly_report.pdf"
    try:
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4), topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.4*inch, rightMargin=0.4*inch)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=8,
            alignment=1
        )
        elements.append(Paragraph("MONTHLY ATTENDANCE REPORT", title_style))
        
        # Period info
        period_style = ParagraphStyle('Period', parent=styles['Normal'], fontSize=9, alignment=1)
        elements.append(Paragraph(
            f"<b>Period:</b> {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} | <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            period_style
        ))
        elements.append(Spacer(1, 8))
        
        # Leadership groups table
        heading_style = ParagraphStyle('Heading', parent=styles['Heading3'], fontSize=11, textColor=colors.HexColor('#1f4788'), spaceAfter=6)
        elements.append(Paragraph("<b>SAMPARK KARYAKAR & LEADERSHIP GROUPS</b>", heading_style))
        
        if leadership_absent:
            # Build table data with proper wrapping
            table_data = [["Name", "Role", "Presence Dates", "Absence Dates", "P", "A"]]
            
            small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, leading=8)
            
            for member, data in sorted(leadership_absent.items()):
                present_str = ", ".join(data["present_dates"]) if data["present_dates"] else "-"
                absence_str = ", ".join(data["absence_dates"]) if data["absence_dates"] else "-"
                
                table_data.append([
                    Paragraph(member, small_style),
                    Paragraph(data["role"], small_style),
                    Paragraph(present_str, small_style),
                    Paragraph(absence_str, small_style),
                    str(data["present_count"]),
                    str(data["absence_count"])
                ])
            
            # Use Paragraph to allow text wrapping in cells
            table = Table(table_data, colWidths=[1.8*inch, 1.2*inch, 2.2*inch, 2.2*inch, 0.5*inch, 0.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-2, -1), 'LEFT'),
                ('ALIGN', (-2, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("<i>No data recorded for leadership groups in this period.</i>", styles['Normal']))
        
        elements.append(Spacer(1, 10))
        
        # Yuvak members table
        elements.append(Paragraph("<b>YUVAK (YOUTH MEMBERS)</b>", heading_style))
        
        if yuvak_absent:
            # Build table data
            table_data = [["Name", "Presence Dates", "Absence Dates", "P", "A"]]
            
            small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, leading=8)
            
            for member, data in sorted(yuvak_absent.items()):
                present_str = ", ".join(data["present_dates"]) if data["present_dates"] else "-"
                absence_str = ", ".join(data["absence_dates"]) if data["absence_dates"] else "-"
                
                table_data.append([
                    Paragraph(member, small_style),
                    Paragraph(present_str, small_style),
                    Paragraph(absence_str, small_style),
                    str(data["present_count"]),
                    str(data["absence_count"])
                ])
            
            table = Table(table_data, colWidths=[2*inch, 2.5*inch, 2.5*inch, 0.5*inch, 0.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-2, -1), 'LEFT'),
                ('ALIGN', (-2, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fffacd')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8e1')])
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("<i>No data recorded for Yuvak members in this period.</i>", styles['Normal']))
        
        elements.append(PageBreak())
        
        # Summary statistics
        elements.append(Paragraph("<b>SUMMARY STATISTICS</b>", heading_style))
        elements.append(Spacer(1, 6))
        
        summary_data = [["Category", "Total Members", "Total Present", "Total Absent", "Attendance %"]]
        for category in ["Sampark Karyakar", "Karyakar", "Sanchalak", "Yuvak"]:
            stats = summary[category]
            total_att = stats["present"] + stats["absent"]
            att_pct = (stats["present"] / total_att * 100) if total_att > 0 else 0
            summary_data.append([
                category,
                str(stats["total_members"]),
                str(stats["present"]),
                str(stats["absent"]),
                f"{att_pct:.1f}%"
            ])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        elements.append(summary_table)
        
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"<b>Total Sessions Analyzed:</b> {len(filtered_sessions)}", ParagraphStyle('Info', parent=styles['Normal'], fontSize=9)))
        
        doc.build(elements)
        return send_file(pdf_path, as_attachment=True, download_name=f"monthly_report_{months}m.pdf")
    except Exception as e:
        print(f"Error generating monthly PDF: {e}")
        import traceback
        traceback.print_exc()
        return f"Error generating PDF: {str(e)}", 500

# ================= SEVA =================
@app.route("/seva")
def seva_list():
    seva = load_seva()
    members = load_members()
    return render_template("seva_list.html", seva=seva, members=members)

@app.route("/seva/create", methods=["GET", "POST"])
def create_seva():
    members = load_members()
    
    if request.method == "POST":
        seva_id = str(uuid.uuid4())[:8]
        seva_name = request.form.get("seva_name", "")
        seva_type = request.form.get("seva_type", "")
        selected_members = request.form.getlist("members")
        
        seva = load_seva()
        seva[seva_id] = {
            "name": seva_name,
            "type": seva_type,
            "members": selected_members,
            "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_seva(seva)
        return redirect(url_for("seva_list"))
    
    return render_template("create_seva.html", members=members)

@app.route("/seva/<seva_id>/edit", methods=["GET", "POST"])
def edit_seva(seva_id):
    seva_data = load_seva()
    members = load_members()
    seva = seva_data.get(seva_id)
    
    if not seva:
        return "Seva not found", 404
    
    if request.method == "POST":
        seva["name"] = request.form.get("seva_name", "")
        seva["type"] = request.form.get("seva_type", "")
        seva["members"] = request.form.getlist("members")
        save_seva(seva_data)
        return redirect(url_for("seva_list"))
    
    return render_template("edit_seva.html", seva_id=seva_id, seva=seva, members=members)

@app.route("/seva/<seva_id>/delete", methods=["POST"])
def delete_seva(seva_id):
    seva = load_seva()
    seva.pop(seva_id, None)
    save_seva(seva)
    return redirect(url_for("seva_list"))

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
