# -*- coding: utf-8 -*-
"""
Main Database Assembler and Index Builder
化学纤维全景数据库集成与多维索引构建器 (截至2026年)
"""
import sqlite3
import json
import csv
import os

from categories_def import CATEGORIES
from fibers_data_part1 import FIBERS_PART_1
from fibers_data_part2 import FIBERS_PART_2
from fibers_data_part3 import FIBERS_PART_3
from fibers_data_part4 import FIBERS_PART_4

DB_FILE = "chemical_fibers.db"
JSON_FILE = "chemical_fibers_dataset.json"
CSV_FILE = "chemical_fibers_catalog.csv"
SCHEMA_FILE = "schema.sql"

def build_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Read and apply schema
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

    # 2. Insert Categories
    category_id_map = {}
    for cat in CATEGORIES:
        cid, code, name_zh, name_en, parent_id, desc = cat
        cursor.execute("""
            INSERT INTO categories (id, code, name_zh, name_en, parent_id, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cid, code, name_zh, name_en, parent_id, desc))
        category_id_map[code] = cid

    # 3. Combine Fiber Datasets
    all_fibers = FIBERS_PART_1 + FIBERS_PART_2 + FIBERS_PART_3 + FIBERS_PART_4
    print(f"Total fiber entries to import: {len(all_fibers)}")

    # 4. Insert Fibers, Aliases, Standards, and FTS Index
    for f in all_fibers:
        cat_id = category_id_map[f["category_code"]]
        cursor.execute("""
            INSERT INTO fibers (
                category_id, code, name_zh, name_en, chemical_name, chemical_formula,
                cas_number, generation, discovery_year, commercial_year, pioneering_entity,
                spinning_method, density_g_cm3, tensile_strength_cn_dtex, tensile_strength_gpa,
                tensile_modulus_gpa, elongation_at_break_pct, moisture_regain_pct, loi_pct,
                melting_point_c, max_service_temp_c, typical_applications, representative_brands,
                tech_status_2026, is_bio_based, is_biodegradable, is_high_performance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cat_id, f["code"], f["name_zh"], f["name_en"], f.get("chemical_name"), f.get("chemical_formula"),
            f.get("cas_number"), f.get("generation"), f.get("discovery_year"), f.get("commercial_year"), f.get("pioneering_entity"),
            f.get("spinning_method"), f.get("density_g_cm3"), f.get("tensile_strength_cn_dtex"), f.get("tensile_strength_gpa"),
            f.get("tensile_modulus_gpa"), f.get("elongation_at_break_pct"), f.get("moisture_regain_pct"), f.get("loi_pct"),
            f.get("melting_point_c"), f.get("max_service_temp_c"), f.get("typical_applications"), f.get("representative_brands"),
            f.get("tech_status_2026"), f.get("is_bio_based", 0), f.get("is_biodegradable", 0), f.get("is_high_performance", 0)
        ))
        fiber_id = cursor.lastrowid

        # Insert aliases
        for alias, alias_type in f.get("aliases", []):
            cursor.execute("""
                INSERT INTO fiber_aliases (fiber_id, alias, alias_type)
                VALUES (?, ?, ?)
            """, (fiber_id, alias, alias_type))

        # Insert standards
        for std_org, std_code, std_title in f.get("standards", []):
            cursor.execute("""
                INSERT INTO fiber_standards (fiber_id, standard_org, standard_code, standard_title)
                VALUES (?, ?, ?, ?)
            """, (fiber_id, std_org, std_code, std_title))

        # Insert into FTS5 index
        cursor.execute("""
            INSERT INTO fibers_fts (
                rowid, code, name_zh, name_en, chemical_name,
                spinning_method, typical_applications, representative_brands, tech_status_2026
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fiber_id, f["code"], f["name_zh"], f["name_en"], f.get("chemical_name", ""),
            f.get("spinning_method", ""), f.get("typical_applications", ""),
            f.get("representative_brands", ""), f.get("tech_status_2026", "")
        ))

    conn.commit()
    print("Database built successfully with FTS5 and B-Tree indexes!")

    # 5. Export JSON
    cursor.execute("""
        SELECT f.*, c.code as category_code, c.name_zh as category_name_zh, c.name_en as category_name_en
        FROM fibers f
        JOIN categories c ON f.category_id = c.id
        ORDER BY f.id
    """)
    col_names = [desc[0] for desc in cursor.description]
    json_records = []
    for row in cursor.fetchall():
        record = dict(zip(col_names, row))
        fid = record["id"]

        # Fetch aliases
        cursor.execute("SELECT alias, alias_type FROM fiber_aliases WHERE fiber_id = ?", (fid,))
        record["aliases"] = [{"alias": a, "type": t} for a, t in cursor.fetchall()]

        # Fetch standards
        cursor.execute("SELECT standard_org, standard_code, standard_title FROM fiber_standards WHERE fiber_id = ?", (fid,))
        record["standards"] = [{"org": o, "code": c, "title": t} for o, c, t in cursor.fetchall()]

        json_records.append(record)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "database_title": "人类化学纤维全景数据库 (Chemical Fibers Comprehensive Dataset - Up to 2026)",
            "version": "2026.1.0",
            "date": "2026-09-08",
            "total_fibers_count": len(json_records),
            "categories_hierarchy": CATEGORIES,
            "fibers": json_records
        }, f, ensure_ascii=False, indent=2)
    print(f"Exported JSON dataset to {JSON_FILE}")

    # 6. Export CSV with UTF-8 BOM for Excel/Numbers compatibility
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        headers = [
            "序号", "分类代号", "分类名称", "纤维代码", "中文通用名", "英文名称", "化学命名",
            "CAS号", "代际划分", "发明年代", "商业化年代", "首发机构/发明人", "纺丝成型工艺",
            "密度(g/cm³)", "断裂强度(cN/dtex)", "断裂强度(GPa)", "拉伸模量(GPa)", "断裂伸长率(%)",
            "公定回潮率(%)", "极限氧指数LOI(%)", "熔点(°C)", "最高服役温度(°C)",
            "生物基", "可生物降解", "战略高性能", "代表品牌/商标", "典型应用领域", "2026技术成熟度与产业现状"
        ]
        writer.writerow(headers)

        for rec in json_records:
            writer.writerow([
                rec["id"],
                rec["category_code"],
                rec["category_name_zh"],
                rec["code"],
                rec["name_zh"],
                rec["name_en"],
                rec.get("chemical_name") or "",
                rec.get("cas_number") or "",
                rec.get("generation") or "",
                rec.get("discovery_year") or "",
                rec.get("commercial_year") or "",
                rec.get("pioneering_entity") or "",
                rec.get("spinning_method") or "",
                rec.get("density_g_cm3") if rec.get("density_g_cm3") is not None else "",
                rec.get("tensile_strength_cn_dtex") if rec.get("tensile_strength_cn_dtex") is not None else "",
                rec.get("tensile_strength_gpa") if rec.get("tensile_strength_gpa") is not None else "",
                rec.get("tensile_modulus_gpa") if rec.get("tensile_modulus_gpa") is not None else "",
                rec.get("elongation_at_break_pct") if rec.get("elongation_at_break_pct") is not None else "",
                rec.get("moisture_regain_pct") if rec.get("moisture_regain_pct") is not None else "",
                rec.get("loi_pct") if rec.get("loi_pct") is not None else "",
                rec.get("melting_point_c") if rec.get("melting_point_c") is not None else "",
                rec.get("max_service_temp_c") if rec.get("max_service_temp_c") is not None else "",
                "是" if rec.get("is_bio_based") else "否",
                "是" if rec.get("is_biodegradable") else "否",
                "是" if rec.get("is_high_performance") else "否",
                rec.get("representative_brands") or "",
                rec.get("typical_applications") or "",
                rec.get("tech_status_2026") or ""
            ])
    print(f"Exported CSV catalog to {CSV_FILE}")

    conn.close()

if __name__ == "__main__":
    build_database()
