# Flask Backend to REST API Conversion Guide

## Overview
Convert the existing Flask app from rendering HTML templates to returning JSON API responses that the Next.js frontend can consume.

## Changes Required to `app.py`

### 1. Add CORS Support
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

### 2. Add Flask-RESTful (Optional but Recommended)
```python
pip install Flask-RESTful
```

### 3. Convert Routes Pattern

#### Before (HTML Response):
```python
@app.route("/members")
def members():
    members_list = get_all_members()
    return render_template("members.html", members=members_list)
```

#### After (JSON Response):
```python
@app.route("/api/members", methods=["GET"])
def get_members():
    try:
        members_list = get_all_members()
        members_dict = [get_member_dict(m) for m in members_list]
        return jsonify(members_dict), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## API Endpoints to Create

### Members Endpoints

```python
@app.route("/api/members", methods=["GET"])
def get_members():
    """Get all members"""
    members_list = get_all_members()
    return jsonify([get_member_dict(m) for m in members_list]), 200

@app.route("/api/member/<name>", methods=["GET"])
def get_member(name):
    """Get member by name"""
    member = get_member_by_name(name)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    return jsonify(get_member_dict(member)), 200

@app.route("/api/member", methods=["POST"])
def create_member():
    """Create new member"""
    data = request.json
    try:
        member = create_new_member(data)
        return jsonify(get_member_dict(member)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/member/<name>", methods=["PUT"])
def update_member_api(name):
    """Update member"""
    data = request.json
    try:
        updated = update_member(name, data)
        return jsonify(get_member_dict(updated)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

### Sessions Endpoints

```python
@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    """Get all sessions"""
    sessions = db.session.query(Session).all()
    return jsonify([{
        "id": s.id,
        "date": s.date.isoformat(),
        "start_time": s.start_time,
        "end_time": s.end_time,
        "status": s.status
    } for s in sessions]), 200

@app.route("/api/session/<int:session_id>", methods=["GET"])
def get_session(session_id):
    """Get specific session"""
    session = db.session.query(Session).get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({
        "id": session.id,
        "date": session.date.isoformat(),
        "start_time": session.start_time,
        "end_time": session.end_time,
        "status": session.status
    }), 200

@app.route("/api/session", methods=["POST"])
def create_session_api():
    """Create new session"""
    data = request.json
    try:
        new_session = create_session(data)
        return jsonify({
            "id": new_session.id,
            "date": new_session.date.isoformat(),
            "start_time": new_session.start_time,
            "status": new_session.status
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/session/<int:session_id>/end", methods=["POST"])
def end_session_api(session_id):
    """End a session"""
    try:
        session = end_session(session_id)
        return jsonify({
            "id": session.id,
            "status": session.status,
            "end_time": session.end_time
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

### Attendance Endpoints

```python
@app.route("/api/attendance", methods=["POST"])
def record_attendance():
    """Record attendance"""
    data = request.json
    try:
        attendance = update_attendance(
            data["session_id"],
            data["member_name"],
            data["status"],
            data.get("arrival_time")
        )
        return jsonify({"message": "Attendance recorded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/session/<int:session_id>/attendance", methods=["GET"])
def get_attendance(session_id):
    """Get session attendance"""
    try:
        attendance = get_session_attendance(session_id)
        return jsonify(attendance), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

### Assignment Endpoints

```python
@app.route("/api/assignments", methods=["GET"])
def get_assignments_api():
    """Get all assignments"""
    assignments = get_assignments_dict()
    return jsonify(assignments), 200

@app.route("/api/assignment", methods=["POST"])
def create_assignment_api():
    """Create or update assignment"""
    data = request.json
    try:
        assignment = set_assignment(data["member_id"], data.get("sampark_name"))
        return jsonify(assignment), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

### Seva Endpoints

```python
@app.route("/api/sevas", methods=["GET"])
def get_sevas_api():
    """Get all sevas"""
    sevas = get_seva_dict()
    return jsonify(sevas), 200

@app.route("/api/seva", methods=["POST"])
def create_seva_api():
    """Create new seva"""
    data = request.json
    try:
        seva = create_seva(data)
        return jsonify(seva), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/seva/<int:seva_id>", methods=["PUT"])
def update_seva_api(seva_id):
    """Update seva"""
    data = request.json
    try:
        seva = update_seva(seva_id, data)
        return jsonify(seva), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/seva/<int:seva_id>", methods=["DELETE"])
def delete_seva_api(seva_id):
    """Delete seva"""
    try:
        delete_seva(seva_id)
        return jsonify({"message": "Seva deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

## Installation

Add to `requirements.txt`:
```
Flask-CORS==4.0.0
```

Then:
```bash
pip install -r requirements.txt
```

## Running the Backend

```bash
cd attendance-system
python app.py
# Backend runs on http://localhost:5000
```

## Testing API Endpoints

Use curl or Postman:

```bash
# Get all members
curl http://localhost:5000/api/members

# Get specific member
curl http://localhost:5000/api/member/Dharshan%20Patel

# Create new session
curl -X POST http://localhost:5000/api/session \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-01-25","start_time":"10:00","end_time":"11:00"}'

# Record attendance
curl -X POST http://localhost:5000/api/attendance \
  -H "Content-Type: application/json" \
  -d '{"session_id":1,"member_name":"Dharshan Patel","status":"Present","arrival_time":"10:05"}'
```

## Frontend Integration

Once API is ready, the Next.js frontend will:
1. Use `apiClient` from `src/lib/api/client.ts`
2. Make calls like: `apiClient.getAllMembers()`
3. Display data in React components with ShadCN UI

## Summary of Changes

| File | Change |
|------|--------|
| app.py | Add `/api/*` routes, return JSON instead of HTML |
| requirements.txt | Add Flask-CORS |
| HTML/CSS/JS files | DELETE (no longer needed) |

All existing database logic remains unchanged - just the response format changes from HTML to JSON.
