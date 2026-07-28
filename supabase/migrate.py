#!/usr/bin/env python3
"""
Migrate data from SQLite to Supabase.

Usage:
  1. Install: pip install supabase
  2. Create a Supabase project at https://supabase.com
  3. Get your project URL and anon key from Project Settings -> API
  4. Run: python supabase/migrate.py

The script reads from local SQLite and writes to Supabase.
It clears existing Supabase tables before inserting (safe on fresh deploy).
"""
import os
import sys
import sqlite3

try:
    from supabase import create_client, Client
except ImportError:
    print("Missing dependency. Run: pip install supabase")
    sys.exit(1)


SQLITE_PATH = os.environ.get(
    "SQLITE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "database.sqlite"),
)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY env vars first.")
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def migrate(supabase: Client):
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print("Reading surahs...")
    surahs = [dict(row) for row in cur.execute("SELECT * FROM surahs ORDER BY sura_id").fetchall()]

    print("Reading verses...")
    verses = [dict(row) for row in cur.execute("SELECT * FROM verses ORDER BY ayat_id").fetchall()]

    print("Reading tafsir_sections...")
    sections = [dict(row) for row in cur.execute("SELECT * FROM tafsir_sections ORDER BY id").fetchall()]

    print("Reading tafsir_content...")
    tafsir = [dict(row) for row in cur.execute("SELECT * FROM tafsir_content ORDER BY id").fetchall()]

    conn.close()

    print("Clearing Supabase tables...")
    supabase.table("tafsir_content").delete().neq("id", 0).execute()
    supabase.table("tafsir_sections").delete().neq("id", 0).execute()
    supabase.table("verses").delete().neq("ayat_id", 0).execute()
    supabase.table("surahs").delete().neq("sura_id", 0).execute()

    print("Inserting surahs...")
    supabase.table("surahs").insert(surahs).execute()

    print("Inserting verses...")
    supabase.table("verses").insert(verses).execute()

    print("Inserting tafsir_sections...")
    supabase.table("tafsir_sections").insert(sections).execute()

    print("Inserting tafsir_content...")
    supabase.table("tafsir_content").insert(tafsir).execute()

    print("Done.")


if __name__ == "__main__":
    migrate(get_supabase())
