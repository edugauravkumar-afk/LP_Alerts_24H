# 🎯 START HERE - LP Alerts 24H

Welcome! This folder contains everything you need to run 24-hour LP alerts independently.

## ⚡ 30-Second Overview

**What:** Checks for landing page changes in last 24 hours  
**Where:** LATAM (6 countries) + Greater China (4 countries)  
**When:** Run manually or schedule daily  
**Result:** HTML email with alert summary

---

## 🚀 Get Started (3 Steps)

### 1. Setup (1 minute)
```bash
bash setup.sh
```

### 2. Configure (1 minute)
```bash
# Edit .env with your credentials
# Copy from your existing setup:
# - GEOEDGE_API_KEY
# - MYSQL credentials
# - ALERT_EMAIL
```

### 3. Run (3 minutes)
```bash
python main.py
```

**✅ Done!** Check `alert_checker.log` for results

---

## 📚 Documentation

**Pick Your Path:**

- **New to this?** → Read [QUICK_START.md](QUICK_START.md)
- **Need details?** → Read [README.md](README.md)
- **Want reference?** → Read [INDEX.md](INDEX.md)
- **Setup help?** → Read [SETUP_SUMMARY.md](SETUP_SUMMARY.md)
- **Full checklist?** → Read [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)

---

## 📦 What's Included

```
main.py              ← Run this to check alerts
config.py            ← Configuration
send_email.py        ← Email module
test_system.py       ← Verify setup works
setup.sh             ← Automatic setup
requirements.txt     ← Python packages
.env.example         ← Credentials template
```

---

## 🎯 How It Works

```
Find English campaigns → Query API → Match to publishers
         ↓
Get publisher country → Filter LATAM/Greater China → Send email
```

**Time:** 2-3 minutes per run

---

## ✅ Before You Start

1. You have credentials:
   - GEOEDGE_API_KEY
   - MYSQL access
   - ALERT_EMAIL

2. You have network access to:
   - GeoEdge API
   - MySQL database
   - SMTP server

3. Python 3.6+ installed

---

## 🔥 Quick Commands

```bash
# Setup everything
bash setup.sh

# Test system
python test_system.py

# Run alerts
python main.py

# Check logs
tail -f alert_checker.log

# View credentials template
cat .env.example
```

---

## 💡 Common Questions

**Q: Will it spam me with emails?**  
A: No! Deduplication prevents duplicate emails for same alerts.

**Q: What if I get 0 alerts?**  
A: Normal! Means no LP changes in last 24 hours. Check logs to verify it's working.

**Q: Can I schedule this to run daily?**  
A: Yes! Add to cron or Windows Task Scheduler. See README.md

**Q: What if setup fails?**  
A: Run `python test_system.py` to diagnose the issue.

---

## 📊 Regions Monitored

**LATAM:** Mexico, Argentina, Brazil, Chile, Colombia, Peru  
**Greater China:** China, Hong Kong, Taiwan, Macau

---

## 🆘 Troubleshooting

**Setup issues?**  
→ Run: `python test_system.py`

**Can't run main.py?**  
→ Run: `bash setup.sh` again

**Check logs:**  
→ `tail -f alert_checker.log`

**More help?**  
→ See [README.md](README.md)

---

## 📈 Next Steps

1. ✅ Run setup.sh
2. ✅ Edit .env
3. ✅ Run test_system.py
4. ✅ Run python main.py
5. ✅ Check logs
6. ✅ (Optional) Schedule daily

---

**Ready?** Let's go! 🚀

```bash
bash setup.sh
```

---

**Need help?**
- [QUICK_START.md](QUICK_START.md) - Fast setup
- [README.md](README.md) - Full docs
- [alert_checker.log](alert_checker.log) - Execution logs
