import sqlite3
import json
from datetime import datetime

def init_db(db_path="db/species_cache.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS species_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scientific_name TEXT,
        common_name TEXT,
        category TEXT,
        taxonomy_json TEXT,
        regions_json TEXT,
        synonyms_json TEXT,
        habitats_json TEXT,
        extra_info_json TEXT,
        wikipedia_json TEXT,
        cached_at TEXT,
        coordinates_json TEXT,
        iucn_json TEXT
    )
    ''')

    # Migration check: add new columns if missing in existing DB
    c.execute("PRAGMA table_info(species_cache)")
    columns = [col[1] for col in c.fetchall()]
    if "coordinates_json" not in columns:
        try:
            c.execute("ALTER TABLE species_cache ADD COLUMN coordinates_json TEXT")
        except Exception:
            pass
    if "iucn_json" not in columns:
        try:
            c.execute("ALTER TABLE species_cache ADD COLUMN iucn_json TEXT")
        except Exception:
            pass

    conn.commit()
    conn.close()


def fetch_from_cache(scientific_name, db_path="db/species_cache.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM species_cache WHERE scientific_name = ?", (scientific_name,))
    row = c.fetchone()
    conn.close()

    if row:
        coords = []
        if len(row) > 11 and row[11]:
            try:
                coords = json.loads(row[11])
            except Exception:
                coords = []

        iucn_data = None
        if len(row) > 12 and row[12]:
            try:
                iucn_data = json.loads(row[12])
            except Exception:
                iucn_data = None

        return {
            "scientific_name": row[1],
            "common_name": row[2],
            "category": row[3],
            "taxonomy": json.loads(row[4]) if row[4] else {},
            "regions": json.loads(row[5]) if row[5] else [],
            "synonyms": json.loads(row[6]) if row[6] else [],
            "habitats": json.loads(row[7]) if row[7] else [],
            "extra_info": json.loads(row[8]) if row[8] else {},
            "wikipedia": json.loads(row[9]) if row[9] else {},
            "cached_at": row[10],
            "coordinates": coords,
            "iucn_status": iucn_data
        }

    return None


def insert_into_cache(data, db_path="db/species_cache.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    INSERT INTO species_cache 
    (scientific_name, common_name, category, taxonomy_json, regions_json, synonyms_json, habitats_json, extra_info_json, wikipedia_json, cached_at, coordinates_json, iucn_json) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("scientific_name"),
        data.get("common_name"),
        data.get("category"),
        json.dumps(data.get("taxonomy")),
        json.dumps(data.get("regions", [])),
        json.dumps(data.get("synonyms", [])),
        json.dumps(data.get("habitats", [])),
        json.dumps(data.get("extra_info", {})),
        json.dumps(data.get("wikipedia", {})),
        datetime.now().isoformat(),
        json.dumps(data.get("coordinates", [])),
        json.dumps(data.get("iucn_status"))
    ))

    conn.commit()
    conn.close()
