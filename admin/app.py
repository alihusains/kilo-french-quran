import os
from datetime import timedelta

from flask import Flask, g
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change-me-in-production')
app.permanent_session_lifetime = timedelta(hours=8)

# Database configuration
DB_PATH = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'oc_frenchquran.sqlite'))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


def validate_database():
    """Validate that the database file exists and is readable."""
    if not os.path.exists(DB_PATH):
        raise RuntimeError(
            f"Database not found at: {DB_PATH}\n"
            "Please ensure the database file exists.\n"
            "You can build it by running: python build_database.py\n"
            "Or set DATABASE_PATH environment variable to the correct path."
        )
    
    # Test database connectivity
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Database error: {e}\nPlease check your database file.")


# Run validation on startup
with app.app_context():
    validate_database()


def get_db():
    """Get database connection with row factory."""
    if 'db' not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exc):
    """Close database connection on app context teardown."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def login_required(f):
    """Decorator to require login for routes."""
    def wrapper(*args, **kwargs):
        from flask import session, redirect, url_for
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with password authentication."""
    from flask import render_template, request, session, flash
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session.permanent = True
            session['logged_in'] = True
            from flask import redirect, url_for
            return redirect(url_for('dashboard'))
        flash('Incorrect password', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Handle user logout."""
    from flask import session, redirect, url_for
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    """Display dashboard with statistics."""
    from flask import render_template
    db = get_db()
    surah_count = db.execute('SELECT COUNT(*) as c FROM surahs').fetchone()['c']
    verse_count = db.execute('SELECT COUNT(*) as c FROM verses').fetchone()['c']
    tafsir_count = db.execute('SELECT COUNT(*) as c FROM tafsir_content').fetchone()['c']
    section_count = db.execute('SELECT COUNT(*) as c FROM tafsir_sections').fetchone()['c']
    return render_template('dashboard.html', surah_count=surah_count, verse_count=verse_count,
                           tafsir_count=tafsir_count, section_count=section_count)


# Surahs & Verses

@app.route('/surahs')
@login_required
def surah_list():
    """List all surahs with search functionality."""
    from flask import render_template, request
    db = get_db()
    
    # Get search query
    search = request.args.get('q', '').strip()
    
    if search:
        # Search by name (french or arabic) or sura_id
        surahs = db.execute(
            "SELECT * FROM surahs WHERE name_french LIKE ? OR name_ar LIKE ? OR sura_id = ? ORDER BY sura_id",
            (f'%{search}%', f'%{search}%', int(search) if search.isdigit() else 0)
        ).fetchall()
    else:
        surahs = db.execute('SELECT * FROM surahs ORDER BY sura_id').fetchall()
    
    return render_template('surahs.html', surahs=surahs, search=search)


@app.route('/surahs/<int:sura_id>')
@login_required
def surah_detail(sura_id):
    """Display detailed view of a surah with verses and tafsir."""
    from flask import render_template, flash, redirect, url_for
    
    db = get_db()
    surah = db.execute('SELECT * FROM surahs WHERE sura_id = ?', (sura_id,)).fetchone()
    if not surah:
        flash('Surah not found', 'error')
        return redirect(url_for('surah_list'))
    verses = db.execute('SELECT * FROM verses WHERE sura_id = ? ORDER BY ayat_no', (sura_id,)).fetchall()
    tafsir_entries = db.execute('''
        SELECT t.id, t.section_id, s.title_fr, t.content
        FROM tafsir_content t
        JOIN tafsir_sections s ON s.id = t.section_id
        WHERE t.sura_id = ?
        ORDER BY s.sort_order
    ''', (sura_id,)).fetchall()
    return render_template('surah_detail.html', surah=surah, verses=verses, tafsir_entries=tafsir_entries)


@app.route('/verses/edit/<int:ayat_id>', methods=['GET', 'POST'])
@login_required
def verse_edit(ayat_id):
    """Edit a single verse."""
    from flask import render_template, flash, redirect, url_for, request
    
    db = get_db()
    verse = db.execute('SELECT * FROM verses WHERE ayat_id = ?', (ayat_id,)).fetchone()
    if not verse:
        flash('Verse not found', 'error')
        return redirect(url_for('surah_list'))
    if request.method == 'POST':
        arabic = request.form.get('ayat_ar', '').strip()
        french = request.form.get('ayat_fr', '').strip()
        audio_url = request.form.get('audio_url', '').strip()
        audio_fr = request.form.get('audio_translation_french', '').strip()
        audio_tafsir = request.form.get('audio_tafsir', '').strip()
        db.execute('''
            UPDATE verses SET ayat_ar = ?, ayat_fr = ?, audio_url = ?, audio_translation_french = ?, audio_tafsir = ?
            WHERE ayat_id = ?
        ''', (arabic, french, audio_url, audio_fr, audio_tafsir, ayat_id))
        db.commit()
        flash('Verse updated', 'success')
        return redirect(url_for('surah_detail', sura_id=verse['sura_id']))
    return render_template('verse_edit.html', verse=verse)


# Tafsir CRUD

@app.route('/tafsir')
@login_required
def tafsir_list():
    """List all tafsir entries with search functionality."""
    from flask import render_template, request
    db = get_db()
    
    # Get search query
    search = request.args.get('q', '').strip()
    
    if search:
        entries = db.execute('''
            SELECT t.id, t.sura_id, s.name_french as surah_name, s.name_ar as surah_name_ar,
                   t.section_id, sec.title_fr as section_title, t.content
            FROM tafsir_content t
            JOIN surahs s ON s.sura_id = t.sura_id
            JOIN tafsir_sections sec ON sec.id = t.section_id
            WHERE s.name_french LIKE ? OR s.name_ar LIKE ? OR sec.title_fr LIKE ? OR t.content LIKE ?
            ORDER BY t.sura_id, sec.sort_order
        ''', (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        entries = db.execute('''
            SELECT t.id, t.sura_id, s.name_french as surah_name, s.name_ar as surah_name_ar,
                   t.section_id, sec.title_fr as section_title, t.content
            FROM tafsir_content t
            JOIN surahs s ON s.sura_id = t.sura_id
            JOIN tafsir_sections sec ON sec.id = t.section_id
            ORDER BY t.sura_id, sec.sort_order
        ''').fetchall()
    
    return render_template('tafsir_list.html', entries=entries, search=search)


@app.route('/tafsir/create', methods=['GET', 'POST'])
@login_required
def tafsir_create():
    """Create a new tafsir entry."""
    from flask import render_template, flash, redirect, url_for
    
    db = get_db()
    if request.method == 'POST':
        sura_id = request.form.get('sura_id', type=int)
        section_id = request.form.get('section_id', type=int)
        content = request.form.get('content', '').strip()
        if not sura_id or not section_id or not content:
            flash('All fields are required', 'error')
        else:
            db.execute('INSERT INTO tafsir_content (sura_id, section_id, content) VALUES (?, ?, ?)',
                       (sura_id, section_id, content))
            db.commit()
            flash('Tafsir entry created', 'success')
            return redirect(url_for('tafsir_list'))
    surahs = db.execute('SELECT * FROM surahs ORDER BY sura_id').fetchall()
    sections = db.execute('SELECT * FROM tafsir_sections ORDER BY sort_order').fetchall()
    return render_template('tafsir_form.html', surahs=surahs, sections=sections, entry=None)


@app.route('/tafsir/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def tafsir_edit(id):
    """Edit an existing tafsir entry."""
    from flask import render_template, flash, redirect, url_for, request
    
    db = get_db()
    entry = db.execute('SELECT * FROM tafsir_content WHERE id = ?', (id,)).fetchone()
    if not entry:
        flash('Tafsir entry not found', 'error')
        return redirect(url_for('tafsir_list'))
    if request.method == 'POST':
        sura_id = request.form.get('sura_id', type=int)
        section_id = request.form.get('section_id', type=int)
        content = request.form.get('content', '').strip()
        if not sura_id or not section_id or not content:
            flash('All fields are required', 'error')
        else:
            db.execute('UPDATE tafsir_content SET sura_id = ?, section_id = ?, content = ? WHERE id = ?',
                       (sura_id, section_id, content, id))
            db.commit()
            flash('Tafsir entry updated', 'success')
            return redirect(url_for('tafsir_list'))
    surahs = db.execute('SELECT * FROM surahs ORDER BY sura_id').fetchall()
    sections = db.execute('SELECT * FROM tafsir_sections ORDER BY sort_order').fetchall()
    return render_template('tafsir_form.html', surahs=surahs, sections=sections, entry=entry)


@app.route('/tafsir/delete/<int:id>', methods=['POST'])
@login_required
def tafsir_delete(id):
    """Delete a tafsir entry."""
    from flask import flash, redirect, url_for
    
    db = get_db()
    entry = db.execute('SELECT id FROM tafsir_content WHERE id = ?', (id,)).fetchone()
    if entry:
        db.execute('DELETE FROM tafsir_content WHERE id = ?', (id,))
        db.commit()
        flash('Tafsir entry deleted', 'success')
    else:
        flash('Tafsir entry not found', 'error')
    return redirect(url_for('tafsir_list'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
