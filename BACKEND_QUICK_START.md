# Quick Start: Backend REST API Conversion

## Step 1: Install Flask-CORS

Add to `attendance-system/requirements.txt`:
```
Flask-CORS==4.0.0
```

Run:
```bash
cd attendance-system
pip install -r requirements.txt
```

## Step 2: Update Flask App

In `app.py`, add these imports at the top:

```python
from flask_cors import CORS
from functools import wraps
import json
```

After creating the Flask app, add CORS:

```python
app = Flask(__name__)
db.init_app(app)
CORS(app)  # Enable CORS for all routes
```

## Step 3: Convert Routes to REST API

### Remove Old HTML Routes

Delete or comment out:
- `/` (dashboard)
- `/members` (members list)
- `/member/<name>` (keep but modify)
- `/sessions` (sessions list)
- `/session/<id>` (sessions detail)
- All other render_template calls

### Add New API Routes

Replace or add alongside existing routes:

```python
# ===== API ROUTES =====

# Members API
@app.route("/api/members", methods=["GET"])
def api_get_members():
    try:
        members_list = get_all_members()
        return jsonify([get_member_dict(m) for m in members_list]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/member/<name>", methods=["GET"])
def api_get_member(name):
    try:
        member = get_member_by_name(name)
        if not member:
            return jsonify({"error": "Member not found"}), 404
        return jsonify(get_member_dict(member)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/member/<name>", methods=["PUT"])
def api_update_member(name):
    try:
        data = request.json
        update_member(name, data)
        member = get_member_by_name(name)
        return jsonify(get_member_dict(member)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Sessions API
@app.route("/api/sessions", methods=["GET"])
def api_get_sessions():
    try:
        sessions = db.session.query(Session).all()
        return jsonify([{
            "id": s.id,
            "date": s.date.isoformat(),
            "start_time": s.start_time,
            "end_time": s.end_time,
            "status": s.status
        } for s in sessions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/session/<int:session_id>", methods=["GET"])
def api_get_session(session_id):
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/session", methods=["POST"])
def api_create_session():
    try:
        data = request.json
        new_session = Session(
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            start_time=data["start_time"],
            status="ACTIVE"
        )
        db.session.add(new_session)
        db.session.commit()
        return jsonify({
            "id": new_session.id,
            "date": new_session.date.isoformat(),
            "start_time": new_session.start_time,
            "status": new_session.status
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/api/session/<int:session_id>/end", methods=["POST"])
def api_end_session(session_id):
    try:
        session = db.session.query(Session).get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        session.status = "ENDED"
        session.end_time = datetime.now().strftime("%H:%M")
        db.session.commit()
        return jsonify({
            "id": session.id,
            "status": session.status,
            "end_time": session.end_time
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Attendance API
@app.route("/api/attendance", methods=["POST"])
def api_record_attendance():
    try:
        data = request.json
        update_attendance(
            data["session_id"],
            data["member_name"],
            data["status"],
            data.get("arrival_time")
        )
        return jsonify({"message": "Attendance recorded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Assignments API
@app.route("/api/assignments", methods=["GET"])
def api_get_assignments():
    try:
        return jsonify(get_assignments_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/assignment", methods=["POST"])
def api_set_assignment():
    try:
        data = request.json
        set_assignment(data["member_id"], data.get("sampark_name"))
        return jsonify({"message": "Assignment updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Sevas API
@app.route("/api/sevas", methods=["GET"])
def api_get_sevas():
    try:
        return jsonify(get_seva_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/seva", methods=["POST"])
def api_create_seva():
    try:
        data = request.json
        seva = create_seva(data)
        return jsonify(seva), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/seva/<int:seva_id>", methods=["PUT"])
def api_update_seva(seva_id):
    try:
        data = request.json
        seva = update_seva(seva_id, data)
        return jsonify(seva), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/seva/<int:seva_id>", methods=["DELETE"])
def api_delete_seva(seva_id):
    try:
        delete_seva(seva_id)
        return jsonify({"message": "Seva deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

## Step 4: Test Backend

```bash
cd attendance-system
python app.py
```

Test endpoints with curl:

```bash
# Get all members
curl http://localhost:5000/api/members

# Get specific member
curl http://localhost:5000/api/member/Dharshan%20Patel

# Get all sessions
curl http://localhost:5000/api/sessions

# Create session
curl -X POST http://localhost:5000/api/session \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-01-25","start_time":"10:00"}'
```

## Step 5: Run Frontend

In another terminal:

```bash
cd baps-frontend
npm run dev
```

Open: http://localhost:3000

## Step 6: Test Integration

1. Go to http://localhost:3000/members
2. Should see list of members from database
3. Click "Edit" on a member
4. Should navigate to member detail page
5. Test other pages

## Common Issues & Solutions

### CORS Error
**Problem:** "Access to XMLHttpRequest blocked by CORS policy"

**Solution:** Ensure Flask-CORS is installed and CORS is enabled:
```python
from flask_cors import CORS
CORS(app)
```

### 404 Not Found
**Problem:** API endpoints return 404

**Solution:** Check:
1. Flask is running on port 5000
2. Routes are prefixed with `/api/`
3. Method matches (GET, POST, PUT, DELETE)

### Connection Refused
**Problem:** "Cannot GET http://localhost:5000/api/..."

**Solution:**
1. Start Flask backend: `python app.py`
2. Check .env.local has correct URL
3. Ensure backend is on port 5000

### JSON Decode Error
**Problem:** Request body not being parsed

**Solution:** Ensure:
1. Content-Type header is "application/json"
2. Data is valid JSON
3. Using `request.json` not `request.data`

## Files to Modify

- `attendance-system/requirements.txt` - Add Flask-CORS
- `attendance-system/app.py` - Add API routes
- Keep all existing functions in db_helpers.py
- Keep database models and migrations

## Files to Keep

- ✅ models.py - Database models
- ✅ db_helpers.py - Database functions
- ✅ config.py - Database configuration
- ✅ init_db.py - Migration script
- ✅ .env - Environment variables

## Files to Remove (Optional)

- templates/ folder (no longer needed)
- static/ folder (CSS/JS moved to Next.js)
- HTML rendering code from routes

## Next Steps

After API is working:
1. ✅ Backend running on http://localhost:5000
2. ✅ Frontend running on http://localhost:3000
3. ✅ API endpoints responding with JSON
4. ✅ Frontend displaying data from API
5. Test all CRUD operations
6. Add error handling in frontend
7. Deploy to production

---

## Summary

Convert Flask from rendering HTML to serving JSON API:
1. Add Flask-CORS
2. Replace `render_template()` with `jsonify()`
3. Keep all database logic the same
4. Return JSON responses instead of HTML
5. Test with Frontend on port 3000

Both servers run simultaneously:
- Backend: http://localhost:5000 (Flask)
- Frontend: http://localhost:3000 (Next.js)
