# BAPS Attendance System - Setup & Installation Guide

A comprehensive Flask-based attendance management system with PDF reporting, automated notifications, and member management.

---

## Table of Contents
- [System Requirements](#system-requirements)
- [Installation Steps](#installation-steps)
  - [Windows Installation](#windows-installation)
  - [Mac Installation](#mac-installation)
- [Dependencies](#dependencies)
- [Running the Application](#running-the-application)
- [Features Overview](#features-overview)
- [File Structure](#file-structure)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum
- **Disk Space**: 500MB
- **Internet Connection**: Required for SMS notifications (optional)

### Browser Compatibility
- Chrome/Chromium (Recommended)
- Firefox
- Safari
- Edge

---

## Installation Steps

### Windows Installation

#### Step 1: Install Python
1. Download Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation by opening Command Prompt and typing:
   ```bash
   python --version
   ```

#### Step 2: Install Git (Optional but Recommended)
1. Download from [git-scm.com](https://git-scm.com/)
2. Run installer and follow default settings

#### Step 3: Clone/Download the Project
**Option A: Using Git (Recommended)**
```bash
git clone <repository-url>
cd attendance-system
```

**Option B: Manual Download**
1. Download project as ZIP
2. Extract to desired location
3. Open Command Prompt and navigate to the folder:
   ```bash
   cd C:\Users\YourUsername\Desktop\BAPS_APP\attendance-system
   ```

#### Step 4: Create Virtual Environment
1. Open Command Prompt in the project directory
2. Create virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
   You should see `(venv)` at the start of your terminal line

#### Step 5: Install Dependencies
With virtual environment activated, run:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Verify Installation
Test if all dependencies are installed correctly:
```bash
pip list
```

---

### Mac Installation

#### Step 1: Install Python
**Option A: Using Homebrew (Recommended)**
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python@3.11
   ```

**Option B: Direct Download**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. Follow installation wizard

#### Step 2: Verify Python Installation
```bash
python3 --version
```

#### Step 3: Install Git (Optional)
```bash
brew install git
```

#### Step 4: Clone/Download the Project
**Option A: Using Git**
```bash
git clone <repository-url>
cd attendance-system
```

**Option B: Manual Download**
1. Download project as ZIP
2. Extract to desired location
3. Open Terminal and navigate:
   ```bash
   cd /path/to/attendance-system
   ```

#### Step 5: Create Virtual Environment
```bash
python3 -m venv venv
```

#### Step 6: Activate Virtual Environment
```bash
source venv/bin/activate
```
You should see `(venv)` at the start of your terminal

#### Step 7: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 8: Verify Installation
```bash
pip list
```

---

## Dependencies

### Required Python Packages

```
Flask==2.2.3              # Web framework
Werkzeug==2.2.3           # WSGI utility library
pandas==2.0.3             # Data manipulation
openpyxl==3.1.2           # Excel file handling
reportlab==4.0.4          # PDF generation
requests==2.31.0          # HTTP library
python-dotenv==1.0.0      # Environment variables
```

### Optional Dependencies (for SMS notifications)
```
twilio==8.10.0            # SMS/WhatsApp notifications
```

### Complete Requirements File
All dependencies are listed in `requirements.txt`

---

## Running the Application

### Windows

1. Open Command Prompt in project directory
2. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open browser and go to:
   ```
   http://localhost:5000
   ```

### Mac

1. Open Terminal in project directory
2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Run the application:
   ```bash
   python3 app.py
   ```
4. Open browser and go to:
   ```
   http://localhost:5000
   ```

### Stopping the Application
Press `CTRL + C` in the terminal/command prompt

---

## Features Overview

### 1. **Dashboard**
- View all members
- Quick session creation
- Recent attendance overview
- Birthday notifications

### 2. **Member Management**
- Add/Edit/Delete members
- Categorize by role (Yuvak, Sampark Karyakar, Karyakar, Sanchalak)
- Phone number management
- Date of birth tracking

### 3. **Session Management**
- Create attendance sessions
- Mark attendance with arrival times
- Real-time member status
- End session functionality
- Automatic SMS notifications (if configured)

### 4. **Attendance Tracking**
- Mark present/absent
- Capture arrival times
- View history
- Absence notifications

### 5. **Reports & Analytics**
- **Monthly Reports**: 1, 3, 6, 9, 12 month views
- **Category-wise Grouping**: Separate reports for leadership and youth
- **PDF Download**: Formatted reports with presence/absence dates
- **Statistics**: Attendance percentage and summaries

### 6. **Notifications**
- Birthday reminders
- Absence alerts
- SMS integration (optional)
- Automatic notifications

---

## File Structure

```
attendance-system/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── SETUP_GUIDE.md                  # This file
│
├── data/
│   ├── members.json               # Member database
│   ├── sessions.json              # Session records
│   ├── attendance.json            # Attendance logs
│   ├── assignments.json           # Leadership assignments
│   └── raw_excel/                 # Excel imports
│
├── templates/                      # HTML templates
│   ├── base.html                  # Base template
│   ├── dashboard.html             # Dashboard
│   ├── members.html               # Member list
│   ├── member_detail.html         # Member details
│   ├── create_session.html        # Session creation
│   ├── session_attendance.html    # Mark attendance
│   ├── session_report.html        # Session report
│   ├── monthly_report.html        # Monthly report
│   └── ...
│
├── static/
│   └── style.css                  # CSS styling
│
├── reports/
│   └── pdfs/
│       ├── session/               # Session PDFs
│       └── monthly/               # Monthly PDFs
│
├── logs/                          # Application logs
├── __pycache__/                   # Python cache
└── venv/                          # Virtual environment
```

---

## Environment Setup (Optional)

### For SMS Notifications (Optional)

1. Create `.env` file in project root:
   ```bash
   touch .env
   ```

2. Add Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

3. Install Twilio package:
   ```bash
   pip install twilio
   ```

---

## Running on Startup

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger and action
4. Action: `python.exe` with arguments: `C:\path\to\app.py`

### Mac (LaunchAgent)

Create `~/Library/LaunchAgents/com.baps.attendance.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.baps.attendance</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3</string>
    <string>/path/to/app.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
```

---

## Troubleshooting

### Issue: "python is not recognized as an internal or external command"
**Solution (Windows)**:
- Python not in PATH
- Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Python311\python.exe app.py`

### Issue: "No module named 'flask'" or other module errors
**Solution**:
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`
- Verify: `pip list`

### Issue: "Address already in use" on port 5000
**Solution**:
- Another application is using port 5000
- Kill the process and restart
- Or change port in `app.py`: `app.run(port=5001)`

### Issue: "Cannot connect to localhost:5000"
**Solution**:
- Ensure app.py is running
- Check terminal for error messages
- Try: `http://127.0.0.1:5000`
- Check firewall settings

### Issue: PDF generation fails
**Solution**:
- Ensure reportlab is installed: `pip install reportlab`
- Check disk space for PDF storage
- Verify permissions on `reports/` folder

### Issue: JSON file errors
**Solution**:
- Ensure all JSON files exist in `data/` folder
- Check file permissions
- Verify JSON syntax is valid

### Issue: Application crashes on startup
**Solution (Windows)**:
```bash
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

**Solution (Mac)**:
```bash
python3 -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
```

---

## First Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] JSON data files exist in `data/` folder
- [ ] Application runs without errors (`python app.py`)
- [ ] Browser opens to `http://localhost:5000`
- [ ] Can create members and sessions
- [ ] Reports generate successfully

---

## Support & Maintenance

### Regular Maintenance
- Backup JSON data files weekly
- Check logs for errors
- Update Python packages monthly: `pip install --upgrade -r requirements.txt`

### Data Backup
```bash
# Windows
copy data\*.json backups\

# Mac
cp data/*.json backups/
```

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## Quick Reference

### Windows Quick Start
```bash
cd C:\Users\YourUsername\Desktop\BAPS_APP\attendance-system
venv\Scripts\activate
python app.py
```

### Mac Quick Start
```bash
cd /path/to/attendance-system
source venv/bin/activate
python3 app.py
```

---

## Notes

- Default port: `5000`
- Debug mode: `ON` (for development)
- For production, use WSGI server like Gunicorn
- Data stored in JSON format (no database required)
- All times sync with system time
- Past date/time prevention enabled

---

## License & Credits

BAPS Attendance System - 2026

For issues or questions, contact the development team.

---

**Last Updated**: January 25, 2026
