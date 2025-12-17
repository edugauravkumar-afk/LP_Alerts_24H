# 🚀 PUSH TO GITHUB & WINDOWS SETUP GUIDE

## 📤 STEP 1: PUSH TO GITHUB (macOS - Current Machine)

### Option A: Create New Repository on GitHub

1. **Go to GitHub:** https://github.com/new
2. **Create repository:**
   - **Repository name:** `LP_Alerts_24H`
   - **Description:** `24-Hour LP Alert Checker for LATAM & Greater China English Campaigns`
   - **Public/Private:** Choose as needed
   - **Do NOT initialize with README** (we already have one)
   - Click **Create repository**

3. **Copy the repository URL** from GitHub (looks like):
   ```
   https://github.com/edugauravkumar-afk/LP_Alerts_24H.git
   ```

### Step 2: Push from macOS

```bash
# Navigate to project directory
cd /Users/gaurav.k/Desktop/geoedge-country-projects/LP_Alerts_24H

# Add remote repository
git remote add origin https://github.com/edugauravkumar-afk/LP_Alerts_24H.git

# Verify remote was added
git remote -v

# Push to GitHub
git push -u origin master

# Verify
git log --oneline -5
```

**Expected output:**
```
Counting objects: 100, done.
Delta compression using up to 8 threads.
Compressing objects: 100%
Writing objects: 100%

[new branch]      master -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

✅ **Done! Repository is now on GitHub**

---

## 💻 STEP 2: SETUP ON WINDOWS MACHINE

### Prerequisites
- [ ] Windows 10/11
- [ ] Python 3.10+ installed from python.org
- [ ] Git installed from git-scm.com

---

### STEP 1: Clone Repository

**On Windows machine, open Command Prompt or PowerShell:**

```bash
# Navigate to desired location
cd C:\Projects

# Clone repository
git clone https://github.com/edugauravkumar-afk/LP_Alerts_24H.git

# Enter directory
cd LP_Alerts_24H

# List files to verify
dir
```

**Expected files:**
```
main.py
send_email.py
config.py
requirements.txt
.env.example
.gitignore
schedule_windows.bat
WINDOWS_SETUP.md
README.md
```

---

### STEP 2: Create Virtual Environment

**In Command Prompt (as regular user, NOT Administrator yet):**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# For Command Prompt:
venv\Scripts\activate.bat

# For PowerShell (if using):
.\venv\Scripts\Activate.ps1
```

**You should see `(venv)` in your prompt:**
```
(venv) C:\Projects\LP_Alerts_24H>
```

---

### STEP 3: Install Dependencies

**With `(venv)` activated:**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Expected packages:**
```
pymysql
requests
python-dotenv
```

---

### STEP 4: Configure Environment (.env file)

**Create `.env` file:**

```bash
# Copy template
copy .env.example .env

# Open with Notepad
notepad .env
```

**Configure these values in `.env`:**

```ini
# Database Configuration
MYSQL_HOST=your-database-hostname.com
MYSQL_PORT=6033
MYSQL_USER=your_database_username
MYSQL_PASSWORD=your_database_password
MYSQL_DB=trc

# GeoEdge API Configuration
GEOEDGE_API_KEY=your-geoedge-api-key-here
GEOEDGE_API_BASE=https://api.geoedge.com/rest/analytics/v3

# Email Recipients
RECIPIENTS=your-email@company.com
CC_RECIPIENTS=manager@company.com

# SMTP Server
SMTP_SERVER=ildcsmtp.office.taboola.com
```

**Save and close Notepad (Ctrl+S, Ctrl+W)**

---

### STEP 5: Test Configuration

**With `(venv)` activated:**

```bash
# Test database connection
python test_system.py

# Test email sending
python test_email.py

# Test main script
python main.py
```

**Expected output for main.py:**
```
[2025-12-17 19:35:30] 🎯 LP ALERTS CHECKER - 24 HOURS
[2025-12-17 19:35:35] ✅ Found 100000 English-targeting campaigns
[2025-12-17 19:37:30] ✅ Alert check complete: X alerts sent
```

✅ **If you see this, configuration is correct!**

---

### STEP 6: Schedule Daily Automated Runs

**Open Command Prompt AS ADMINISTRATOR:**

1. **Press Windows key** and type `cmd`
2. **Right-click** "Command Prompt"
3. **Select** "Run as administrator"
4. **Navigate to project:**
   ```bash
   cd C:\Projects\LP_Alerts_24H
   ```

5. **Run the batch file:**
   ```bash
   schedule_windows.bat
   ```

**Expected output:**
```
Creating scheduled task "LP_Alerts_24H"...
✅ Task created successfully!
🕐 LP Alerts will run daily at 08:00 AM UTC
```

---

### STEP 7: Verify Scheduling

**Verify task was created (in Administrator Command Prompt):**

```bash
# List the task
schtasks /query /tn "LP_Alerts_24H" /v

# Check if task exists
schtasks /query /tn "LP_Alerts_24H" /fo list /v
```

**Or manually open Task Scheduler:**
1. Press `Win + R`
2. Type `taskschd.msc`
3. Press Enter
4. Find "LP_Alerts_24H" in the list
5. Verify trigger is set to "Daily 08:00 AM"

✅ **Done! System is scheduled!**

---

## 📊 SUMMARY - What Happens Now

| When | What Happens |
|---|---|
| **08:00 AM UTC Daily** | Windows Task Scheduler triggers the task |
| **Task starts** | `python.exe` runs `main.py` |
| **Database** | Fetches 100,000 English campaigns |
| **API** | Gets LP alerts from last 24 hours (6 chunks) |
| **Processing** | Matches and filters for LATAM & Greater China |
| **Email** | Sends alert to recipients (with or without alerts) |
| **Logging** | Results written to `alert_checker.log` |
| **Duration** | ~2-3 minutes total execution |

---

## 📁 Windows Directory Structure

```
C:\Projects\LP_Alerts_24H\
├── venv\                          (Virtual environment - created by you)
├── main.py                        (Main script)
├── send_email.py                  (Email module)
├── config.py                      (Configuration)
├── requirements.txt               (Dependencies list)
├── .env                           (Your credentials - DO NOT SHARE)
├── .env.example                   (Template)
├── .gitignore                     (Tells git what to ignore)
├── schedule_windows.bat           (Windows scheduler)
├── README.md                      (Project overview)
├── WINDOWS_SETUP.md              (Detailed guide)
├── WINDOWS_QUICK_START.md        (Quick checklist)
├── alert_checker.log             (Created automatically with logs)
└── seen_lp_alerts.json           (Created automatically, tracks alerts)
```

---

## 🔍 Monitor Execution

**View latest log entries:**

```bash
# In Command Prompt
type alert_checker.log

# Or for just last 20 lines
powershell -Command "Get-Content alert_checker.log -Tail 20"

# Or in PowerShell
Get-Content alert_checker.log -Tail 20 -Wait
```

**Watch logs in real-time (PowerShell):**
```powershell
Get-Content alert_checker.log -Wait
```

---

## ⚠️ Important Notes

- ✅ **Never share `.env` file** - contains credentials
- ✅ **Virtual environment** needs to be created on each machine
- ✅ **Timezone is UTC** - 08:00 AM UTC = 3:00 AM EST
- ✅ **Computer shouldn't sleep** during scheduled time
- ✅ **Administrator privileges** required for task scheduling
- ✅ **Python must be in PATH** for task to run

---

## 🆘 Troubleshooting

### "Python not found"
```bash
# Verify Python installed
python --version

# If not, download from python.org
# Make sure "Add Python to PATH" is checked
```

### "Virtual environment won't activate"
```bash
# For Command Prompt:
venv\Scripts\activate.bat

# For PowerShell:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### "pip install fails"
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

### "Task not running at scheduled time"
1. Check Windows Task Scheduler
2. Verify time is 08:00 AM
3. Check "Run with highest privileges" is enabled
4. Ensure computer isn't sleeping
5. Check firewall isn't blocking

### "Email not sending"
```bash
# Test email configuration
python test_email.py

# Check SMTP server and recipients in .env
```

---

## 📱 Next Steps

1. ✅ Push code to GitHub (instructions above)
2. ✅ Share GitHub URL with team
3. ✅ Each team member clones repo
4. ✅ Each follows Windows setup steps
5. ✅ Each configures their own `.env` file
6. ✅ Each runs `schedule_windows.bat`
7. ✅ System runs automatically!

---

## 🎯 Git Commands Reference

```bash
# Check status
git status

# View history
git log --oneline

# Make changes
git add .
git commit -m "Description"
git push origin master

# Update from GitHub
git pull origin master
```

---

## ✨ You're All Set!

**On macOS:**
- ✅ Code committed to git
- ✅ Ready to push to GitHub

**On Windows:**
- ✅ Follow steps above
- ✅ Runs automatically daily at 08:00 AM UTC
- ✅ No manual intervention needed

**Questions?** Check `WINDOWS_SETUP.md` or `README.md` in the repository!
