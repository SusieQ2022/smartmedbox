# Contributing Guide

This document explains how every team member should contribute to the
SmartMedBox repository. Because the project is **graded individually**, it is
essential that each person commits their own work under their own GitHub
account so the commit history accurately reflects who did what.

---

## Golden rules

1. **Commit your own work under your own account.** Never let one person push
   everyone's code. The grading explicitly checks the Git history for
   individual contributions.
2. **Commit often, in small logical units.** Many small, well-described commits
   are better than one giant commit.
3. **Write clear commit messages** in English (see format below).
4. **Always pull before you push** to avoid conflicts.

---

## One-time setup (each member, on their own computer)

```bash
# Configure your identity (use the email linked to your GitHub account)
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"

# Clone the repository
git clone https://github.com/<your-org>/smartmedbox.git
cd smartmedbox

# Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Daily workflow

```bash
# 1. Get the latest changes before you start
git pull origin main

# 2. Make your changes to the files you are responsible for
#    (edit code, docs, etc.)

# 3. Stage only the files you worked on
git add src/your_file.py

# 4. Commit with a clear message
git commit -m "Add weight sensor calibration routine"

# 5. Push to the shared repository
git push origin main
```

---

## Commit message format

Use a short imperative summary (max ~60 characters):

```
Add camera-based intake confirmation
Fix double-take detection threshold
Update installation guide for Raspberry Pi
Refactor LLM fallback logic for readability
```

Avoid vague messages like `update`, `changes`, or `fix stuff`.

---

## Branching (optional but recommended)

For larger features, work on a branch and open a Pull Request so a teammate can
review before merging:

```bash
git checkout -b feature/voice-output
# ... make changes, commit ...
git push origin feature/voice-output
# Then open a Pull Request on GitHub
```

---

## Running tests before you push

Please make sure the test suite passes before pushing:

```bash
python -m pytest tests/ -v
```

---

## Checking individual contributions

At any time, you can review who contributed what:

```bash
git shortlog -sne                 # commit count per author
git log --author="Your Name"      # your own commits
git log --oneline --graph         # full visual history
```

---

## Work package ownership

See [`docs/CONTRIBUTIONS.md`](docs/CONTRIBUTIONS.md) for the assignment of
primary work packages. Every member is expected to contribute across hardware,
code, report, and presentation — the table records each person's main focus.
