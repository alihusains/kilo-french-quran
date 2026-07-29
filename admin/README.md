# Quran Admin

Flask admin panel for browsing surahs, editing verses, and managing tafsir.

## Quick Links

- **GitHub Pages Frontend**: https://alihusains.github.io/kilo-french-quran/
- **Supabase Project**: https://supabase.com/dashboard/project/ayyfeobcubwoasrshhbg

## Quick Start (local)

```bash
cd admin
./start.sh
# Open http://localhost:5001
# Login with ADMIN_PASSWORD (default: admin123)
```

## Deployment Options

### Option 1: PythonAnywhere (Free, No Credit Card Required)

PythonAnywhere offers a free always-on web app at `yourname.pythonanywhere.com`.

#### Step 1: Upload Files

1. Sign up at https://www.pythonanywhere.com (free account)
2. Go to the **Files** tab
3. Create a folder: `/home/yourname/frenchquran/`
4. Upload everything from the `admin/` folder
5. Upload `oc_frenchquran.sqlite` from the project root

#### Step 2: Install Flask

1. Go to **Consoles** → **Start a new bash console**
2. Run:
```bash
cd ~/frenchquran
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure Web App

1. Go to the **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** → **Python 3.11**
4. **Source code**: `/home/yourname/frenchquran`
5. **Working directory**: `/home/yourname/frenchquran`
6. **WSGI file**: Replace with:
```python
import os
import sys
path = '/home/yourname/frenchquran'
if path not in sys.path:
    sys.path.insert(0, path)

if 'DATABASE_PATH' not in os.environ:
    os.environ['DATABASE_PATH'] = os.path.join(path, 'oc_frenchquran.sqlite')
if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'change-me-in-production'
if 'ADMIN_PASSWORD' not in os.environ:
    os.environ['ADMIN_PASSWORD'] = 'admin123'

from app import app as application
```
7. **Virtualenv**: `/home/yourname/frenchquran/venv`
8. Click **Reload**

Done! Your admin panel is live at `yourname.pythonanywhere.com`.

### Option 2: Docker

```bash
# Build and run
docker compose up -d

# Access at http://localhost:5001
```

### Option 3: GitHub Pages (Read-Only)

For a frontend-only version read from Supabase:
1. Deploy `admin/dist/index.html` to GitHub Pages
2. The site will be live at https://alihusains.github.io/kilo-french-quran/

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_PASSWORD` | Login password for admin | `admin123` |
| `DATABASE_PATH` | Path to SQLite database | `oc_frenchquran.sqlite` |
| `FLASK_SECRET_KEY` | Session signing key | `change-me-in-production` |
| `PORT` | Server port | `5001` |

## Database Repair

If you need to rebuild the database from source files:

```bash
cd admin
python build_database.py
```

This reads from:
- `French Quran - Tafsir - quran (1).csv` (verse data)
- DOCX files in `sendingthesurahs/` and `pleasefindattachedthe*/` folders

## Share with Non-Technical Users

To make the admin panel accessible externally:

### Using Cloudflare Tunnel

```bash
# Install cloudflared (macOS)
brew install cloudflared

# Start tunnel
./tunnel.sh

# Share the generated URL
```

### Using ngrok

```bash
npm install -g ngrok
ngrok http 5001
```

## Project Structure

```
frenchquran/
├── admin/                    # Flask admin application
│   ├── app.py               # Main Flask application
│   ├── run.py               # Entry point script
│   ├── wsgi.py              # WSGI entry point
│   ├── templates/           # HTML templates
│   ├── dist/index.html    # GitHub Pages frontend
│   ├── Dockerfile         # Docker build
│   ├── docker-compose.yml # Docker compose
│   ├── requirements.txt   # Python dependencies
│   └── start.sh           # Startup script
├── build_database.py      # Database builder
├── oc_frenchquran.sqlite  # Database file
├── supabase/              # Supabase migration
└── database.sqlite        # Legacy database (deprecated)
```

## Non-Technical User Notes

1. **Login**: Use `ADMIN_PASSWORD` (default: `admin123`)
2. **CRUD Operations**: All operations available via web UI
3. **Backup**: The `oc_frenchquran.sqlite` file contains all data
4. **Mobile**: Responsive design works on phones/tablets
5. **API**: Supabase connection at https://supabase.com/dashboard/project/ayyfeobcubwoasrshhbg

## Troubleshooting

- **Blank page**: Check browser console for errors
- **Cannot login**: Verify `ADMIN_PASSWORD` matches
- **No data**: Run migration to populate database
- **Database missing**: Run `python build_database.py` first
