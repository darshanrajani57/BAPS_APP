# BAPS Attendance System - Quick Start Guide

## ⚡ Quick Setup (5 Minutes)

### Windows Users

**Step 1: Open Command Prompt**
Press `Win + R`, type `cmd`, and press Enter

**Step 2: Navigate to Project**
```bash
cd C:\Users\YourUsername\Desktop\BAPS_APP\attendance-system
```

**Step 3: Create & Activate Virtual Environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**Step 4: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Run Application**
```bash
python app.py
```

**Step 6: Open in Browser**
Go to: `http://localhost:5000`

---

### Mac Users

**Step 1: Open Terminal**
Press `Cmd + Space`, type `terminal`, and press Enter

**Step 2: Navigate to Project**
```bash
cd /path/to/attendance-system
```

**Step 3: Create & Activate Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 4: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 5: Run Application**
```bash
python3 app.py
```

**Step 6: Open in Browser**
Go to: `http://localhost:5000`

---

## 📋 Pre-requisites Check

Before running, ensure you have:

- ✅ Python 3.8 or higher installed
- ✅ Internet connection for initial setup
- ✅ At least 500MB disk space
- ✅ Administrator access (Windows) or sudo access (Mac)

### Check Python Version
**Windows:**
```bash
python --version
```

**Mac:**
```bash
python3 --version
```

Should show: `Python 3.8.x` or higher

---

## 🚀 Start Application

### When Application Starts Successfully, You'll See:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Access the Application
Open your browser and go to: **http://localhost:5000**

---

## ⏹️ Stop Application

Press `CTRL + C` in the terminal/command prompt

---

## 🔧 Common Commands

### Reactivate Virtual Environment (next time you start)

**Windows:**
```bash
venv\Scripts\activate
```

**Mac:**
```bash
source venv/bin/activate
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Check Installed Packages
```bash
pip list
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "python not found" | Reinstall Python with PATH option |
| "No module named flask" | Run `pip install -r requirements.txt` |
| "Port 5000 in use" | Kill process or use different port |
| "Cannot connect" | Check if `python app.py` is running |
| "JSON file errors" | Ensure all files in `data/` folder exist |

---

## 📱 App Features

- ✅ Member Management
- ✅ Attendance Marking
- ✅ PDF Reports (1/3/6/9/12 months)
- ✅ Category-wise Grouping
- ✅ Birthday Notifications
- ✅ Absence Tracking with Dates
- ✅ System Time Synchronization

---

## 📚 For Detailed Setup

See **SETUP_GUIDE.md** for comprehensive instructions.

---

**Ready to go!** 🎉
