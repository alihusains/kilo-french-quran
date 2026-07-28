-- SQLite-to-Supabase migration script
-- Run this in Supabase Dashboard -> SQL Editor

BEGIN;

CREATE TABLE IF NOT EXISTS public.surahs (
  sura_id INTEGER PRIMARY KEY,
  name_ar TEXT NOT NULL,
  name_french TEXT NOT NULL,
  type TEXT,
  ayat_count INTEGER
);

CREATE TABLE IF NOT EXISTS public.verses (
  ayat_id INTEGER PRIMARY KEY,
  sura_id INTEGER NOT NULL REFERENCES public.surahs(sura_id),
  ayat_no INTEGER,
  juz_no INTEGER,
  ayat_ar TEXT,
  ayat_fr TEXT,
  ayat_sajda INTEGER,
  audio_url TEXT,
  audio_translation_french TEXT,
  audio_tafsir TEXT
);

CREATE TABLE IF NOT EXISTS public.tafsir_sections (
  id INTEGER PRIMARY KEY,
  code TEXT,
  title_fr TEXT,
  title_fr_short TEXT,
  sort_order INTEGER
);

CREATE TABLE IF NOT EXISTS public.tafsir_content (
  id SERIAL PRIMARY KEY,
  sura_id INTEGER NOT NULL REFERENCES public.surahs(sura_id),
  section_id INTEGER NOT NULL REFERENCES public.tafsir_sections(id),
  content TEXT
);

CREATE INDEX IF NOT EXISTS idx_verses_sura_id ON public.verses(sura_id);
CREATE INDEX IF NOT EXISTS idx_tafsir_content_sura_id ON public.tafsir_content(sura_id);
CREATE INDEX IF NOT EXISTS idx_tafsir_content_section_id ON public.tafsir_content(section_id);

COMMIT;
