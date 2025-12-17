# 🪟 Windows Setup Guide - LP Alerts 24H

Complete guide to set up and run LP Alerts 24H on Windows machines.

---

## ✅ Prerequisites

- Windows 10 or Windows 11
- Python 3.10+ installed ([Download here](https://www.python.org/downloads/))
- Git installed ([Download here](https://git-scm.com/download/win))
- Administrator access (for scheduling)

---

## 📥 Step 1: Clone Repository

```bash
# Open PowerShell or Command Prompt
# Navigate to your desired location
cd C:\Projects

# Clone the repository
git clone <your-repo-url>
cd LP_Alerts_24H
```

---

## 🔧 Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For PowerShell:
.\venv\Scripts\Activate.ps1

# For Command Prompt:
.\venv\Scripts\activate.bat

# You should see (venv) in your prompt
```

**Troubleshooting:** If you get execution policy error in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📦 Step 3: Install Dependencies

```bash
# Make sure you're in the project directory with (venv) activated
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed pymysql-1.x.x requests-2.x.x python-dotenv-1.x.x
```

---

## 🔐 Step 4: Configure Environment Variables

**Create `.env` file in project root:**

```bash
# Copy the example file
copy .env.example .env

# Edit .env with your configuration
# Open in Notepad or your favorite editor
notepad .env
```

**Required variables:**
```
# Database
MYSQL_HOST=your-db-host
MYSQL_PORT=6033
MYSQL_USER=your-username
MYSQL_PASSWORD=your-password
MYSQL_DB=trc

# GeoEdge API
GEOEDGE_API_KEY=your-api-key
GEOEDGE_API_BASE=https://api.geoedge.com/rest/analytics/v3

# Email
RECIPIENTS=recipient@example.com
CC_RECIPIENTS=cc@example.com (optional)
SMTP_SERVER=ildcsmtp.office.taboola.com
```

---

## ✅ Step 5: Test the Setup

**Test database connection:**
```bash
# With (venv) activated
python test_system.py
```

**Test email sending:**
```bash
python test_email.py
```

**Run the main script:**
```bash
python main.py
```

**Expected output:**
```
[2025-12-17 19:35:30] 🎯 LP ALERTS CHECKER - 24 HOURS
[2025-12-17 19:35:30] 📍 Fetching campaigns targeting English countries...
[2025-12-17 19:35:35] ✅ Found 100000 English-targeting campaigns
...
[2025-12-17 19:37:30] ✅ Alert check complete: X alerts sent to 1 recipients
```

---

## 📅 Step 6: Schedule Automated Runs

### Option A: Using Batch File (Easy)

1. **Open Command Prompt as Administrator**
   - Right-click `Command Prompt` → "Run as Administrator"

2. **Navigate to project directory:**
   ```bash
   cd C:\Path\To\LP_Alerts_24H
   ```

3. **Run the batch file:**
   ```bash
   schedule_windows.bat
   ```

4. **Done!** The task is scheduled to run daily at 08:00 AM

### Option B: Manual Task Scheduler Setup

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create new task**
   - Right-click "Task Scheduler Library"
   - Select "Create Basic Task"

3. **Configure task:**
   - **Name:** LP_Alerts_24H
   - **Description:** Daily LP Alert Checker for LATAM & Greater China
   - **Trigger:** Daily at 08:00 AM
   - **Action:** Start a program
     - **Program:** `C:\Path\To\LP_Alerts_24H\venv\Scripts\python.exe`
     - **Arguments:** `main.py`
     - **Start in:** `C:\Path\To\LP_Alerts_24H`

4. **Additional settings:**
   - ✅ "Run with highest privileges"
   - ✅ "Run whether user is logged in or not"

5. **Click Finish**

---

## 🔍 Step 7: Verify Scheduling

**Check if task was created:**
```bash
# Open Command Prompt as Administrator
schtasks /query /tn "LP_Alerts_24H" /v
```

**View task history:**
```bash
Get-ScheduledTaskInfo -TaskName "LP_Alerts_24H"
```

**Check log file:**
```bash
# Open the log file
type alert_checker.log

# Or in PowerShell with real-time updates
Get-Content alert_checker.log -Wait
```

---

## 🛠️ Troubleshooting

### "Python not found"
```bash
# Make sure python is installed
python --version

# If not, download from python.org and install
# Make sure "Add Python to PATH" is checked during installation
```

### "Virtual environment not activating"
```bash
# Make sure you're in the correct directory
cd C:\Path\To\LP_Alerts_24H

# Try the correct command for your shell:
# PowerShell:
.\venv\Scripts\Activate.ps1

# Command Prompt:
.\venv\Scripts\activate.bat
```

### "Dependencies not installing"
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then try installing requirements again
pip install -r requirements.txt
```

### "Task not running at scheduled time"
1. Open Task Scheduler
2. Right-click "LP_Alerts_24H" task
3. Check "Trigger" tab for correct time
4. Check "Conditions" tab - make sure computer isn't set to sleep
5. Check "Run with highest privileges" is enabled

### "Database connection error"
1. Verify credentials in `.env` file
2. Check database host is accessible
3. Test connection with: `python test_system.py`

### "Email not sending"
1. Verify RECIPIENTS in `.env` file
2. Verify SMTP_SERVER in `.env` file
3. Test email with: `python test_email.py`
4. Check firewall isn't blocking SMTP (port 25)

---

## 📊 Log File Location

Logs are stored in:
```
C:\Path\To\LP_Alerts_24H\alert_checker.log
```

View the latest entries:
```bash
# PowerShell - last 20 lines
Get-Content alert_checker.log -Tail 20

# Command Prompt - last 20 lines
powershell -Command "Get-Content alert_checker.log -Tail 20"
```

---

## 🔄 Daily Workflow

**Every day at 08:00 AM:**
1. Task Scheduler triggers the task
2. Python.exe runs `main.py`
3. Script fetches data from databases and APIs
4. Email is sent to recipients
5. Results are logged to `alert_checker.log`

---

## ❌ Remove Scheduling

**Delete the scheduled task:**
```bash
# Run as Administrator
schtasks /delete /tn "LP_Alerts_24H" /f
```

**Or manually:**
1. Open Task Scheduler
2. Locate "LP_Alerts_24H" task
3. Right-click and select "Delete"
4. Confirm deletion

---

## 📈 Performance Notes

- **Execution time:** ~2-3 minutes per run
- **Database queries:** 100,000+ campaigns fetched
- **API requests:** 6 chunked requests (4-hour windows)
- **Email:** Sent to all configured recipients

---

## ✨ Key Features

✅ Fully automated daily checks  
✅ Cross-platform Python code (macOS/Linux compatible)  
✅ Windows-native task scheduling  
✅ Comprehensive logging  
✅ Email alerts with beautiful formatting  
✅ Handles 0 alerts (sends status email)  
✅ Retry logic for API timeouts  
✅ Database connection pooling  

---

## 🆘 Support

For issues or questions:
1. Check the log file: `alert_checker.log`
2. Run tests: `python test_system.py`
3. Review configuration in `.env`
4. Check Windows Task Scheduler for error messages

---

## 📝 Notes

- Timezone: All times are in **UTC**
- Ensure system clock is accurate for scheduling
- Don't close Command Prompt after running batch file
- Task will run in background even if not logged in
- Log file grows over time - periodically clean up

---

**Ready to deploy!** 🚀
