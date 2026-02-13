# Backend API Endpoints Quick Reference

**Base URL:** `http://localhost:5000/api`

## Members API

### Get All Members
```
GET /members
Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "number": "123",
      "phone": "9876543210",
      "category": "Youth",
      "member_type": "Active",
      "address": "Address",
      "status": "Active",
      ...
    }
  ]
}
```

### Get Member by ID
```
GET /members/<member_id>
Response: 200 OK
{
  "status": "success",
  "data": { ... member object ... }
}
```

### Create Member
```
POST /members
Content-Type: application/json
{
  "name": "John Doe",
  "number": "123",
  "phone": "9876543210",
  "category": "Youth",
  "member_type": "Active",
  "address": "Address",
  "status": "Active"
}
Response: 201 Created
{
  "status": "success",
  "message": "Member created successfully",
  "id": 1
}
```

### Update Member
```
PUT /members/<member_id>
Content-Type: application/json
{
  "name": "Updated Name",
  "phone": "9876543211"
}
Response: 200 OK
{
  "status": "success",
  "message": "Member updated successfully"
}
```

---

## Sessions API

### Get All Sessions
```
GET /sessions
Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "id": "S-20260125",
      "date": "2026-01-25",
      "start_time": "09:00",
      "end_time": "10:00",
      "status": "ACTIVE",
      "created_date": "2026-01-25T10:30:00"
    }
  ]
}
```

### Get Session by ID
```
GET /sessions/<session_id>
Response: 200 OK
{
  "status": "success",
  "data": { ... session object ... }
}
```

### Create Session
```
POST /sessions
Content-Type: application/json
{
  "date": "2026-01-25",
  "start_time": "09:00",
  "end_time": "10:00",
  "status": "ACTIVE"
}
Response: 201 Created
{
  "status": "success",
  "message": "Session created successfully",
  "id": "S-20260125"
}
```

### End Session
```
PUT /sessions/<session_id>/end
Response: 200 OK
{
  "status": "success",
  "message": "Session ended successfully"
}
```

---

## Attendance API

### Get Session Attendance
```
GET /sessions/<session_id>/attendance
Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "session_id": "S-20260125",
      "member_id": 1,
      "member_name": "John Doe",
      "status": "Present",
      "sampark_name": "Sampark1",
      "recorded_date": "2026-01-25T10:30:00"
    }
  ]
}
```

### Update Attendance
```
POST /sessions/<session_id>/attendance
Content-Type: application/json
{
  "member_id": 1,
  "status": "Present",
  "sampark_name": "Sampark1"
}
Response: 201 Created
{
  "status": "success",
  "message": "Attendance updated successfully",
  "id": 1
}
```

---

## Assignments API

### Get All Assignments
```
GET /assignments
Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "member_id": 1,
      "member_name": "John Doe",
      "sampark_name": "Sampark1",
      "assigned_date": "2026-01-25T10:30:00"
    }
  ]
}
```

### Create Assignment
```
POST /assignments
Content-Type: application/json
{
  "member_id": 1,
  "sampark_name": "Sampark1"
}
Response: 201 Created
{
  "status": "success",
  "message": "Assignment created successfully",
  "id": 1
}
```

---

## Sevas API

### Get All Sevas
```
GET /sevas
Response: 200 OK
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Seva Name",
      "seva_type": "Type1",
      "created_date": "2026-01-25T10:30:00",
      "member_count": 5
    }
  ]
}
```

### Create Seva
```
POST /sevas
Content-Type: application/json
{
  "name": "Seva Name",
  "seva_type": "Type1"
}
Response: 201 Created
{
  "status": "success",
  "message": "Seva created successfully",
  "id": 1
}
```

### Update Seva
```
PUT /sevas/<seva_id>
Content-Type: application/json
{
  "name": "Updated Seva Name",
  "seva_type": "UpdatedType"
}
Response: 200 OK
{
  "status": "success",
  "message": "Seva updated successfully"
}
```

### Delete Seva
```
DELETE /sevas/<seva_id>
Response: 200 OK
{
  "status": "success",
  "message": "Seva deleted successfully"
}
```

---

## HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Frontend API Client Usage

```typescript
import { apiClient } from "@/lib/api/client";

// Members
const members = await apiClient.getAllMembers();
const member = await apiClient.getMemberById(1);
await apiClient.createMember({ name: "John", ... });
await apiClient.updateMember(1, { name: "Jane" });

// Sessions
const sessions = await apiClient.getAllSessions();
const session = await apiClient.getSession("S-20260125");
await apiClient.createSession({ date: "2026-01-25", ... });
await apiClient.endSession("S-20260125");

// Attendance
const attendance = await apiClient.getSessionAttendance("S-20260125");
await apiClient.updateAttendance("S-20260125", 1, "Present");

// Assignments
const assignments = await apiClient.getAssignments();
await apiClient.setAssignment(1, "Sampark1");

// Sevas
const sevas = await apiClient.getAllSevas();
await apiClient.createSeva({ name: "Seva", seva_type: "Type" });
await apiClient.updateSeva(1, { name: "Updated" });
await apiClient.deleteSeva(1);
```

---

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

### Backend (.env)
```
FLASK_ENV=development
DATABASE_URL=sqlite:///members.db
```

---

**Last Updated:** January 25, 2026
