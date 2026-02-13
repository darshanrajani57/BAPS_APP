# BAPS Attendance Management System

A comprehensive Flask-based attendance tracking and management system designed for religious organizations with advanced reporting, member management, and automated notifications.

## 🎯 Overview

The BAPS Attendance System is a web-based application that helps manage member attendance, track absences, generate reports, and send notifications. It's specifically designed for organizations with multiple member categories and requires minimal technical setup.

## ✨ Key Features

### 1. **Member Management**
- Add, edit, and delete members
- Categorize members by role (Yuvak, Sampark Karyakar, Karyakar, Sanchalak)
- Track phone numbers and dates of birth
- Search and filter functionality
- Import members from Excel

### 2. **Attendance Tracking**
- Real-time attendance marking
- Capture arrival times for all members
- Mark present/absent with one click
- Track attendance history
- System time synchronization
- Prevent backdating of sessions

### 3. **Advanced Reporting**
- **Monthly Reports** (1, 3, 6, 9, 12 months)
- **Category-wise Grouping**: Separate reports for leadership and youth members
- **Detailed Absence Tracking**: Shows exact dates of absences and presences
- **PDF Generation**: Professional formatted reports
- **Attendance Statistics**: Calculate attendance percentages
- **Export Reports**: Download PDF reports anytime

### 4. **Session Management**
- Create attendance sessions with date and time
- Mark individual member attendance
- Real-time member presence status
- End session with one click
- Automatic timestamp recording
- SMS notifications (optional)

### 5. **Notifications & Alerts**
- Birthday reminders
- Absence notifications
- Auto SMS via Twilio (optional)
- WhatsApp notifications (optional)

### 6. **Dashboard**
- Quick overview of all members
- Recent attendance summary
- Upcoming birthdays
- Quick action buttons

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 2GB RAM
- 500MB disk space
- Modern web browser

### Installation & Running

**Windows:**
```bash
cd C:\Users\YourUsername\Desktop\BAPS_APP\attendance-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**Mac/Linux:**
```bash
cd /path/to/attendance-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open browser: `http://localhost:5000`

## 📦 Dependencies

All required packages are in `requirements.txt`:

```
Flask==2.2.3           - Web framework
pandas==2.0.3          - Data processing
openpyxl==3.1.2        - Excel handling
reportlab==4.0.4       - PDF generation
requests==2.31.0       - HTTP library
python-dotenv==1.0.0   - Environment variables
```

## 📁 Project Structure

```
attendance-system/
├── app.py                    # Main Flask application
├── SETUP_GUIDE.md            # Detailed setup instructions
├── QUICK_START.md            # Quick start guide
├── requirements.txt          # Python dependencies
│
├── data/                     # Data storage
│   ├── members.json         # Member records
│   ├── sessions.json        # Session data
│   ├── attendance.json      # Attendance logs
│   └── assignments.json     # Leadership assignments
│
├── templates/                # HTML templates
│   ├── dashboard.html       # Dashboard
│   ├── members.html         # Member list
│   ├── create_session.html  # Session creation
│   ├── session_attendance.html # Mark attendance
│   ├── monthly_report.html  # Monthly reports
│   └── ...
│
├── static/                   # Static files
│   └── style.css            # Styling
│
└── reports/                  # Generated reports
    └── pdfs/                # PDF files
```

## 🎓 How to Use

### 1. Add Members
1. Click "Members" in navigation
2. Click "Add Member"
3. Fill in details (name, role, phone, DOB)
4. Save

### 2. Create Attendance Session
1. Click "Create New Sabha" or "Create Session"
2. Select date and time
3. Click "Create"

### 3. Mark Attendance
1. From dashboard, click "Mark Attendance"
2. Check/uncheck each member
3. Arrival time auto-fills when marking present
4. Click "Submit Attendance"

### 4. View Reports
1. Click "Monthly Report"
2. Select time period (1/3/6/9/12 months)
3. View absence and presence dates
4. Download PDF if needed

## 📊 Report Features

### Monthly Report Shows:
- **Leadership Groups**: Sampark Karyakar, Karyakar, Sanchalak
- **Youth Members**: Yuvak group
- **For Each Member**:
  - Presence dates (dates member was present)
  - Absence dates (dates member was absent)
  - Total present count
  - Total absent count

### PDF Report Includes:
- Period covered
- Generation timestamp
- Grouped by member category
- Formatted tables
- Summary statistics
- Attendance percentages

## ⚙️ Configuration

### Environment Variables (Optional)
Create `.env` file for SMS notifications:
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Port Configuration
Default port: `5000`

To use different port, edit `app.py`:
```python
app.run(port=5001)
```

## 🔒 Security Features

- System time synchronization
- Past date/time prevention
- No backdating of sessions
- Automatic timestamp recording
- Session validation

## 🐛 Troubleshooting

### Common Issues

**Python not found:**
- Install Python with PATH option
- Use full path: `C:\Python311\python.exe`

**Module not found:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
```bash
# Find and kill process on port 5000
# Or change port in app.py
```

**Database errors:**
- Check `data/` folder exists
- Verify JSON file permissions
- Ensure files are not corrupted

See **SETUP_GUIDE.md** for detailed troubleshooting.

## 📖 Documentation

- **SETUP_GUIDE.md** - Comprehensive setup for Windows & Mac
- **QUICK_START.md** - 5-minute quick start guide
- This **README.md** - Overview and general information

## 💾 Data Storage

All data is stored in JSON format:
- **members.json** - Member information
- **sessions.json** - Attendance sessions
- **attendance.json** - Individual attendance records
- **assignments.json** - Leadership role assignments

Data is NOT encrypted. For sensitive data, ensure proper file permissions.

## 📱 Mobile Compatibility

The application works on:
- Desktop browsers
- Tablets (iPad, Android tablets)
- Mobile browsers (responsive design)

## 🔄 Auto-Backup Recommendation

Backup your `data/` folder regularly:
```bash
# Windows
copy data\*.json backup_location\

# Mac/Linux
cp data/*.json backup_location/
```

## 🚀 Performance

- Handles 500+ members efficiently
- Supports 100+ sessions
- Fast PDF generation
- Responsive UI

## 🛠️ Maintenance

### Regular Tasks
- Weekly backup of data files
- Monthly update of dependencies
- Check application logs
- Monitor disk space

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 📞 Support & Issues

For issues or questions:
1. Check SETUP_GUIDE.md troubleshooting section
2. Verify Python version: `python --version`
3. Check application logs in `logs/` folder
4. Ensure all dependencies installed: `pip list`

## 📝 System Time

The application uses your system's current time for:
- Session creation timestamps
- Attendance marking times
- Report generation
- All date/time validations

**Ensure your system clock is accurate for correct operation.**

## 🔐 Data Security

- No encryption on JSON files
- Keep `data/` folder secure
- Regular backups recommended
- Use strong folder permissions

## 📈 Scalability

Current implementation supports:
- 1000+ members
- 1000+ sessions
- JSON-based storage (suitable for small-medium organizations)

For larger scale, consider migrating to database.

## 🎨 UI/UX

- Clean, intuitive interface
- Responsive design
- Mobile-friendly
- Blue & white theme
- Easy navigation

## 🌐 Browser Support

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅

## 📅 Version Information

- **Current Version**: 1.0
- **Last Updated**: January 25, 2026
- **Python Support**: 3.8+
- **Flask Version**: 2.2.3

## 📄 License

BAPS Attendance System - All Rights Reserved

## 🙏 Credits

Developed for BAPS Organizations to simplify attendance management and reporting.

---

## Getting Started

1. **First Time?** → Read [QUICK_START.md](QUICK_START.md)
2. **Detailed Setup?** → Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. **Need Help?** → Check troubleshooting in SETUP_GUIDE.md

---

**Start managing attendance efficiently today!** 🎉

For detailed installation steps for your OS, see:
- [Windows Installation](SETUP_GUIDE.md#windows-installation)
- [Mac Installation](SETUP_GUIDE.md#mac-installation)
