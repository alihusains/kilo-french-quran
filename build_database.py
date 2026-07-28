import sqlite3
import csv
import zipfile
import xml.etree.ElementTree as ET
import glob
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'oc_frenchquran.sqlite')
CSV_PATH = os.path.join(BASE, 'French Quran - Tafsir - quran (1).csv')

DOCX_FOLDERS = [
    'sendingthesurahs',
    'pleasefindattachedthesecondpartofthesurahs_',
    'pleasefindattachedthethirdpartofthesurahs_',
    'pleasefindattachedthefourthpartofthesurahs_',
    'pleasefindattachedthefifthpartofthesurahs_',
    'pleasefindattachedthesixthpartofthesurahs_',
    'pleasefindattachedtheseventhpartofthesurahs_',
    'pleasefindattachedtheeighthpartofthesurahs_',
    'pleasefindattachedtheninthpartofthesurahs_',
    'pleasefindattachedthetenthpartofthesurahs_',
]

SECTION_HEADER_PAT = re.compile(
    r'^[a-e]\)\s+(Abrégé de la table thématique|Aperçu du contenu|Bienfaits de la récitation|'
    r'Circonstances de la révélation|Exégèse et commentaire|Messages? et leçons? à tirer)'
)

SECTION_TITLE_MAP = {
    'Abrégé de la table thématique': 'themes',
    'Aperçu du contenu': 'apercu',
    'Bienfaits de la récitation': 'merites',
    'Circonstances de la révélation': 'contexte',
    'Exégèse et commentaire': 'tafsir',
    'Message et leçon à tirer': 'enseignements',
    'Message et leçons à tirer': 'enseignements',
    'Messages et leçons à tirer': 'enseignements',
}
CONNEXTE_PAT = re.compile(r'^[-\u2013]*\s*(?:Les\s+)?[Cc]irconstances?\s+de\s+la\s+révélation\b')


def build_docx_map():
    mapping = {}
    for folder in DOCX_FOLDERS:
        pattern = os.path.join(BASE, folder, '*.docx')
        for fpath in glob.glob(pattern):
            fname = os.path.basename(fpath)
            match = re.match(r'(\d+)-', fname)
            if match:
                sura_id = int(match.group(1))
                mapping[sura_id] = fpath
    return mapping

def read_docx_lines(path):
    with zipfile.ZipFile(path) as z:
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        lines = []
        for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = []
            for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if t.text:
                    texts.append(t.text)
            line = ''.join(texts).strip()
            if line:
                lines.append(line)
    return lines

def extract_name_french(lines):
    for line in lines[:5]:
        m = re.search(r'«([^»]+)»', line)
        if m:
            return m.group(1).strip()
    return ''

def parse_sections(lines):
    sections = {}
    current_code = None
    current_lines = []
    tafsir_buffer = []
    contexte_buffer = []
    in_contexte_sub = False
    has_contexte = False

    for line in lines:
        sm = SECTION_HEADER_PAT.match(line)
        if sm:
            if current_code and current_lines:
                text = '\n'.join(current_lines).strip()
                if current_code == 'tafsir':
                    tafsir_buffer.append(text)
                elif current_code == 'contexte':
                    contexte_buffer.append(text)
                else:
                    sections[current_code] = text
                current_lines = []
            title = sm.group(1)
            current_code = SECTION_TITLE_MAP[title]
            in_contexte_sub = False
            continue

        if current_code == 'tafsir' and CONNEXTE_PAT.match(line):
            if current_lines:
                tafsir_buffer.append('\n'.join(current_lines).strip())
                current_lines = []
            in_contexte_sub = True
            has_contexte = True
            continue

        if current_code is not None:
            current_lines.append(line)

    if current_code and current_lines:
        text = '\n'.join(current_lines).strip()
        if current_code == 'tafsir' and in_contexte_sub:
            contexte_buffer.append(text)
            tafsir_buffer.append(text)
        elif current_code == 'tafsir':
            tafsir_buffer.append(text)
        elif current_code == 'contexte':
            contexte_buffer.append(text)
        else:
            sections[current_code] = text

    if tafsir_buffer:
        sections['tafsir'] = '\n\n'.join(tafsir_buffer).strip()
    if contexte_buffer:
        sections['contexte'] = '\n\n'.join(contexte_buffer).strip()
        has_contexte = True

    return sections, has_contexte

def extract_verse_translations(tafsir_text, sura_verse_count):
    results = {}
    lines = tafsir_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue

        is_arabic = bool(re.search(r'[\u0600-\u06FF]', line))

        if not is_arabic:
            continue

        has_single_verse = bool(re.search(r'[\u0600-\u06FF][\u0660-\u0669]+\s*$', line))
        has_multiple_verses = False
        arabic_digit_count = len(re.findall(r'[\u0660-\u0669]+', line))

        multi_verse_mode = False
        if arabic_digit_count > 1 or not has_single_verse:
            multi_verse_mode = True

        trans_lines = []
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                i += 1
                continue
            m = re.match(r'(\d+)[-\u2013]\s+(.+)', next_line, re.DOTALL)
            if not m:
                break
            trans_lines.append((int(m.group(1)), m.group(2).strip()))
            i += 1

        if multi_verse_mode:
            for vnum, trans in trans_lines:
                if 1 <= vnum <= sura_verse_count and vnum not in results:
                    results[vnum] = trans
        else:
            for vnum, trans in trans_lines:
                if 1 <= vnum <= sura_verse_count and vnum not in results:
                    results[vnum] = trans
                    break

    return results

def main():
    print('Reading CSV...')
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f'  CSV rows: {len(csv_rows)}')

    docx_map = build_docx_map()
    print(f'  DOCX files mapped: {len(docx_map)} surahs')

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript('''
        CREATE TABLE surahs (
            sura_id INTEGER PRIMARY KEY,
            name_ar TEXT NOT NULL,
            name_french TEXT,
            type TEXT,
            ayat_count INTEGER
        );

        CREATE TABLE verses (
            ayat_id INTEGER PRIMARY KEY,
            sura_id INTEGER NOT NULL,
            ayat_no INTEGER NOT NULL,
            juz_no INTEGER,
            ayat_ar TEXT,
            ayat_fr TEXT,
            ayat_sajda INTEGER DEFAULT 0,
            audio_url TEXT,
            audio_translation_french TEXT,
            audio_tafsir TEXT,
            FOREIGN KEY (sura_id) REFERENCES surahs(sura_id)
        );

        CREATE TABLE tafsir_sections (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            title_fr TEXT NOT NULL,
            title_fr_short TEXT NOT NULL,
            title_en TEXT,
            sort_order INTEGER NOT NULL
        );

        CREATE TABLE tafsir_content (
            id INTEGER PRIMARY KEY,
            sura_id INTEGER NOT NULL,
            section_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (sura_id) REFERENCES surahs(sura_id),
            FOREIGN KEY (section_id) REFERENCES tafsir_sections(id)
        );

        CREATE UNIQUE INDEX idx_tafsir_sura_section ON tafsir_content(sura_id, section_id);
        CREATE INDEX idx_verses_sura ON verses(sura_id);
    ''')

    sections_data = [
        ('themes', 'Abrégé de la table thématique de la sourate', 'Thèmes', 'Themes', 1),
        ('apercu', 'Aperçu du contenu de la sourate', 'Aperçu', 'Overview', 2),
        ('merites', 'Bienfaits de la récitation', 'Mérites', 'Virtues', 3),
        ('contexte', 'Circonstances de la révélation', 'Contexte', 'Context', 4),
        ('tafsir', 'Exégèse et commentaire de la sourate', 'Tafsir', 'Tafsir', 5),
        ('enseignements', 'Message et leçon à tirer de la sourate', 'Enseignements', 'Lessons', 6),
    ]
    cur.executemany(
        'INSERT OR IGNORE INTO tafsir_sections (code, title_fr, title_fr_short, title_en, sort_order) VALUES (?, ?, ?, ?, ?)',
        sections_data
    )

    section_id_map = {}
    for row in cur.execute('SELECT id, code FROM tafsir_sections').fetchall():
        section_id_map[row[1]] = row[0]

    print('Loading surahs and verses from CSV...')
    sura_data = {}
    verse_rows = []
    for r in csv_rows:
        sid = int(r['sura_id'])
        if sid not in sura_data:
            sura_data[sid] = {
                'name_ar': r['sura_name_ar'],
                'name_french': r['sura_name_french'].strip() if r['sura_name_french'].strip() else None,
                'type': r['sura_type'],
                'ayat_count': int(r['sura_ayat']),
            }
        verse_rows.append((
            int(r['ayat_id']), sid, int(r['ayat_no']),
            int(r['juz_no']) if r['juz_no'].strip() else None,
            r['ayat_ar'], None, int(r['ayat_sajda']),
            r['audio'].strip() or None,
            r['audio_translation_french'].strip() or None,
            r['audio_tafsir'].strip() or None,
        ))

    for sid, sd in sura_data.items():
        cur.execute(
            'INSERT OR REPLACE INTO surahs (sura_id, name_ar, name_french, type, ayat_count) VALUES (?, ?, ?, ?, ?)',
            (sid, sd['name_ar'], sd['name_french'], sd['type'], sd['ayat_count'])
        )

    cur.executemany(
        '''INSERT OR REPLACE INTO verses
           (ayat_id, sura_id, ayat_no, juz_no, ayat_ar, ayat_fr, ayat_sajda, audio_url, audio_translation_french, audio_tafsir)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        verse_rows
    )
    conn.commit()
    print(f'  {len(sura_data)} surahs, {len(verse_rows)} verses loaded.')

    print('Parsing DOCX files...')
    total_fr = 0
    parsed = 0

    for sura_id in sorted(docx_map.keys()):
        docx_path = docx_map[sura_id]
        try:
            lines = read_docx_lines(docx_path)
        except Exception as e:
            print(f'  ERROR reading sura {sura_id}: {e}')
            continue
        if not lines:
            continue

        name_french = extract_name_french(lines[:5])
        if name_french:
            cur.execute('UPDATE surahs SET name_french = ? WHERE sura_id = ?', (name_french, sura_id))

        sections, has_contexte = parse_sections(lines)

        for code in ['themes', 'apercu', 'merites', 'tafsir', 'enseignements']:
            content = sections.get(code, '')
            if content.strip() and code in section_id_map:
                cur.execute(
                    'INSERT OR REPLACE INTO tafsir_content (sura_id, section_id, content) VALUES (?, ?, ?)',
                    (sura_id, section_id_map[code], content)
                )

        if has_contexte and sections.get('contexte', '').strip():
            cur.execute(
                'INSERT OR REPLACE INTO tafsir_content (sura_id, section_id, content) VALUES (?, ?, ?)',
                (sura_id, section_id_map['contexte'], sections['contexte'])
            )

        vc = sura_data.get(sura_id, {}).get('ayat_count', 0)
        fr_count = 0
        if vc > 0 and sections.get('tafsir'):
            trans = extract_verse_translations(sections['tafsir'], vc)
            for vnum, translation in trans.items():
                cur.execute(
                    'UPDATE verses SET ayat_fr = ? WHERE sura_id = ? AND ayat_no = ? AND (ayat_fr IS NULL OR ayat_fr = ?)',
                    (translation, sura_id, vnum, '')
                )
                fr_count += 1
                total_fr += 1

        if sura_id <= 5 or sura_id >= 110:
            print(f'  Sura {sura_id}: {name_french or "?"} — {len(sections)} sections, {fr_count}/{vc} ayat_fr')

        parsed += 1
        if parsed % 20 == 0:
            conn.commit()
            print(f'  Progress: {parsed}/114')

    conn.commit()

    cur.execute('SELECT COUNT(DISTINCT sura_id) FROM tafsir_content')
    tc_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM tafsir_content')
    tc_rows = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM verses WHERE ayat_fr IS NOT NULL AND ayat_fr != ?', ('',))
    fr_final = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM surahs WHERE name_french IS NOT NULL AND name_french != ?', ('',))
    nf_count = cur.fetchone()[0]

    print(f'\nDone!')
    print(f'  surahs: {len(sura_data)} (with name_french: {nf_count})')
    print(f'  verses: {len(verse_rows)} (with ayat_fr: {fr_final})')
    print(f'  tafsir_content: {tc_rows} rows across {tc_count} surahs')

    conn.close()

if __name__ == '__main__':
    main()
