# BAPS Attendance System - Dependencies & Requirements

## 📋 Complete Requirements List

### System Requirements

#### Windows
- **OS**: Windows 7 SP1 or higher (Windows 10/11 recommended)
- **Python**: 3.8+ (3.11 recommended)
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB minimum
- **Python Packages**: See below

#### Mac
- **OS**: macOS 10.14 (High Sierra) or higher
- **Python**: 3.8+ (3.11 recommended)
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 500MB minimum
- **Package Manager**: Homebrew (optional but recommended)

#### Linux (Ubuntu/Debian)
- **OS**: Ubuntu 18.04 LTS or higher
- **Python**: 3.8+ (3.11 recommended)
- **RAM**: 2GB minimum
- **Disk Space**: 500MB minimum

---

## 🐍 Python Packages (requirements.txt)

### Core Dependencies
```
Flask==2.2.3
Werkzeug==2.2.3
Jinja2==3.1.2
MarkupSafe==2.1.1
click==8.1.7
itsdangerous==2.1.2
```
**Purpose**: Web framework and templating engine

### Data Processing
```
pandas==2.0.3
numpy==1.24.3
openpyxl==3.1.2
```
**Purpose**: Data manipulation, Excel file handling

### PDF Generation
```
reportlab==4.0.4
```
**Purpose**: Create professional PDF reports

### HTTP & Utilities
```
requests==2.31.0
python-dotenv==1.0.0
```
**Purpose**: HTTP requests and environment variables

---

## 🔧 Installation Methods

### Method 1: Automatic (Recommended)

**Windows:**
```bash
# Double-click run.bat
# OR
run.bat
```

**Mac/Linux:**
```bash
# Make script executable
chmod +x run.sh

# Run script
./run.sh
```

### Method 2: Manual Installation

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

---

## ✅ Verification Checklist

After installation, verify everything:

### 1. Python Installation
```bash
python --version          # Windows
python3 --version         # Mac/Linux
```
Expected: `Python 3.8.0` or higher

### 2. Virtual Environment
Ensure `(venv)` appears in terminal prompt

### 3. All Packages Installed
```bash
pip list
```

You should see:
- Flask 2.2.3
- pandas 2.0.3
- reportlab 4.0.4
- And others from requirements.txt

### 4. Application Launch
```bash
python app.py             # Windows
python3 app.py            # Mac/Linux
```

Expected: Server running on `http://127.0.0.1:5000`

### 5. Browser Access
Open: `http://localhost:5000`

Expected: BAPS Attendance Dashboard loads

---

## 🚫 Common Installation Issues

### Issue 1: Python Not Found
**Windows:**
```
'python' is not recognized as an internal or external command
```
**Solution:**
- Reinstall Python with "Add Python to PATH" checked
- Use full path: `C:\Python311\python.exe app.py`

**Mac/Linux:**
```
python3: command not found
```
**Solution:**
```bash
# Install Python via Homebrew
brew install python@3.11

# Or download from python.org
```

### Issue 2: Virtual Environment Error
**Error:** `No module named venv`

**Solution:**
```bash
# Windows
python -m pip install --upgrade pip

# Mac/Linux
python3 -m pip install --upgrade pip
```

### Issue 3: pip Not Found
**Error:** `pip: command not found`

**Solution:**
```bash
# Windows
python -m pip install --upgrade pip

# Mac/Linux
python3 -m pip install --upgrade pip
```

### Issue 4: Requirements Installation Fails
**Error:** `ERROR: Could not install packages`

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing without cache
pip install --no-cache-dir -r requirements.txt

# Install one by one to identify issue
pip install Flask==2.2.3
pip install pandas==2.0.3
# etc...
```

### Issue 5: Module Import Errors
**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
1. Verify virtual environment is activated (look for `(venv)`)
2. Run: `pip install -r requirements.txt`
3. Check: `pip list` should show Flask

---

## 📦 Optional Dependencies

### SMS Notifications (Optional)
```bash
pip install twilio==8.10.0
```
**Note**: Only needed if using SMS/WhatsApp features

### Excel Import (Already Included)
```bash
openpyxl==3.1.2
```
Allows importing member data from Excel files

---

## 🔄 Upgrading Dependencies

To update all packages to latest versions:
```bash
pip install --upgrade -r requirements.txt
```

To upgrade specific package:
```bash
pip install --upgrade Flask
```

To freeze current versions:
```bash
pip freeze > requirements.txt
```

---

## 💾 Storage Requirements

### Data Files
- `members.json` - ~100KB (500 members)
- `sessions.json` - ~50KB (100 sessions)
- `attendance.json` - ~100KB
- `assignments.json` - ~50KB

**Total for 500 members**: ~300KB

### PDF Reports
- Session PDF: ~200KB-500KB per session
- Monthly PDF: ~500KB-1MB depending on period

---

## 🖥️ Browser Requirements

No special installation needed. Supported browsers:
- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers

---

## 🌐 Network Requirements

- **Local Network Only**: No internet required for basic operation
- **SMS Notifications**: Requires internet connection + Twilio account
- **Excel Import**: No internet required

---

## 📊 Performance Specs

- **Members**: Supports 500+
- **Sessions**: Supports 100+
- **Concurrent Users**: 1-5 (development server)
- **Response Time**: <1 second for most operations
- **PDF Generation**: 2-5 seconds

---

## 🔐 Security Considerations

- Data stored in plain JSON (no encryption)
- No user authentication by default
- Suitable for internal/trusted networks
- Keep `data/` folder secure
- Regular backups recommended

---

## 📝 Quick Reference

### Windows Setup (One-liner)
```bash
python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python app.py
```

### Mac Setup (One-liner)
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python3 app.py
```

---

## ✨ Verification Script

Run this to verify setup:

**Windows (save as verify.bat):**
```batch
@echo off
python --version
python -m venv --help >nul
pip --version
python -c "import flask; print(f'Flask: {flask.__version__}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python -c "import reportlab; print('ReportLab: OK')"
echo All checks passed!
```

**Mac/Linux (save as verify.sh):**
```bash
#!/bin/bash
python3 --version
python3 -m venv --help > /dev/null
pip --version
python3 -c "import flask; print(f'Flask: {flask.__version__}')"
python3 -c "import pandas; print(f'Pandas: {pandas.__version__}')"
python3 -c "import reportlab; print('ReportLab: OK')"
echo "All checks passed!"
```

---

## 🚀 Next Steps

1. ✅ Install Python 3.8+
2. ✅ Create virtual environment
3. ✅ Install packages: `pip install -r requirements.txt`
4. ✅ Run application: `python app.py`
5. ✅ Open browser: `http://localhost:5000`

---

## 📞 Support

For dependency issues:
1. Check Python version: `python --version`
2. Check pip: `pip --version`
3. List installed packages: `pip list`
4. See SETUP_GUIDE.md for detailed help

---

**Last Updated**: January 25, 2026
**Compatible With**: Python 3.8+, Flask 2.2.3, Flask 2.3.x, Flask 3.0.x
