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
        cached_at TEXT
    )
    ''')
    conn.commit()
    conn.close()


def fetch_from_cache(scientific_name, db_path="db/species_cache.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM species_cache WHERE scientific_name = ?", (scientific_name,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "scientific_name": row[1],
            "common_name": row[2],
            "category": row[3],
            "taxonomy": json.loads(row[4]),
            "regions": json.loads(row[5]),
            "synonyms": json.loads(row[6]),
            "habitats": json.loads(row[7]),
            "extra_info": json.loads(row[8]),
            "cached_at": row[9]
        }

    return None


def insert_into_cache(data, db_path="db/species_cache.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    INSERT INTO species_cache 
    (scientific_name, common_name, category, taxonomy_json, regions_json, synonyms_json, habitats_json, extra_info_json, cached_at) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("scientific_name"),
        data.get("common_name"),
        data.get("category"),
        json.dumps(data.get("taxonomy")),
        json.dumps(data.get("regions", [])),
        json.dumps(data.get("synonyms", [])),
        json.dumps(data.get("habitats", [])),
        json.dumps(data.get("extra_info", {})),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
