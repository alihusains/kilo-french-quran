# Quran Admin

Flask admin panel for browsing surahs, editing verses, and managing tafsir.

## Quick Start (local)

```bash
cd admin
./start.sh
# Open http://localhost:5001
# Login with ADMIN_PASSWORD (default: admin123)
```

## Free Hosting (PythonAnywhere) — No credit card needed

PythonAnywhere gives you a free always-on web app at `yourname.pythonanywhere.com`.

### Step 1: Upload the files

1. Sign up at https://www.pythonanywhere.com (free account)
2. Go to the **Files** tab
3. Create a folder: `/home/yourname/frenchquran/`
4. Upload everything from the `admin/` folder into that directory
5. Also upload `database.sqlite` from the project root

### Step 2: Install Flask in a virtualenv

1. Go to the **Consoles** tab → **Start a new bash console**
2. Run:
```bash
cd ~/frenchquran
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Set up the web app

1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Choose **Python 3.11** (or latest available)
5. In **Source code**, enter: `/home/yourname/frenchquran`
6. In **Working directory**, enter: `/home/yourname/frenchquran`
7. Click the **WSGI configuration file** link and replace its contents with:
```python
import sys
path = '/home/yourname/frenchquran'
if path not in sys.path:
    sys.path.insert(0, path)

if 'DATABASE_PATH' not in os.environ:
    os.environ['DATABASE_PATH'] = os.path.join(path, 'database.sqlite')
if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'change-me-in-production'
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin123'

import os
from app import app as application
```
8. In **Virtualenv**, enter: `/home/yourname/frenchquran/venv`
9. Click **Reload**

Done. Your admin panel is live at `yourname.pythonanywhere.com`.

### Change the password (optional)

Set a custom admin password by adding in the WSGI file:
```python
os.environ['ADMIN_PASSWORD'] = 'your-secret-password'
```

### Notes
- SQLite writes persist across reboots
- If you update the database locally, re-upload `database.sqlite`
- Free tier is sufficient for a small team

## Environment Variables

- `ADMIN_PASSWORD` — login password (default: `admin123`)
- `DATABASE_PATH` — path to SQLite (default: `admin/../database.sqlite`)
- `FLASK_SECRET_KEY` — session signing key (change in production)
- `PORT` — server port (default: `5001` locally)

## Share with team

Create one login and share the URL. Team members can edit tafsir and verses directly in the browser.
