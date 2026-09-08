# -*- coding: utf-8 -*-
"""
Main Database Assembler and Multi-dimensional Index Builder (Textile-Focused Edition)
现代纺织化学纤维全景数据库与工程知识库全量集成构建器 (截至2026年)
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
from fibers_data_textile import FIBERS_TEXTILE, TEXTILE_BLENDS, TEXTILE_PROFILES_DATA

DB_FILE = "chemical_fibers.db"
JSON_FILE = "chemical_fibers_dataset.json"
CSV_FILE = "chemical_fibers_catalog.csv"
SCHEMA_FILE = "schema.sql"

def get_textile_domain(f):
    if f.get("textile_domain"):
        return f["textile_domain"]
    cat = f.get("category_code", "")
    code = f.get("code", "")
    if cat in ("REG_CELL", "REG_PROT", "SYN_PET", "SYN_PA", "SYN_PAN", "SYN_PU", "SYN_DIFF_PET"):
        return "服装用纺织品 / 家用纺织品"
    elif cat in ("REG_POLY", "SYN_PO", "SYN_PVA", "SYN_HALO", "SYN_MICRO"):
        return "家用纺织品 / 产业用纺织品"
    elif cat in ("BIO_ALIPH", "BIO_FDCA"):
        return "服装用纺织品 / 产业用纺织品"
    elif cat in ("HP_ARAMID", "HP_UHMWPE", "HP_HETERO", "HP_ENG", "HP_FLUORO", "HP_THERMO"):
        return "产业用纺织品 (特种安全防护与工程)"
    elif cat in ("CF_PAN", "CF_PITCH", "CF_RAYON", "CF_NANO", "CF_ACT"):
        return "产业用纺织品 (先进结构复合材料与功能吸附)"
    elif cat in ("INORG_GLASS", "INORG_MINERAL", "INORG_CERAMIC", "INORG_METAL"):
        return "产业用纺织品 (无机增强/电子玻纤/隔热防辐射)"
    elif cat in ("EMG_BIOENG", "EMG_SMART", "EMG_ENERGY", "EMG_AERO", "EMG_2D", "EMG_TEXTILE_FUNC"):
        return "服装用纺织品 / 智能穿戴纺织品"
    return "综合纺织品"

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
    all_fibers = FIBERS_PART_1 + FIBERS_PART_2 + FIBERS_PART_3 + FIBERS_PART_4 + FIBERS_TEXTILE
    print(f"Total fiber entries to import: {len(all_fibers)}")

    # 4. Insert Fibers, Aliases, Standards, Textile Profiles, and FTS Index
    for f in all_fibers:
        cat_id = category_id_map[f["category_code"]]
        domain = get_textile_domain(f)
        cursor.execute("""
            INSERT INTO fibers (
                category_id, code, name_zh, name_en, chemical_name, chemical_formula,
                cas_number, generation, discovery_year, commercial_year, pioneering_entity,
                spinning_method, density_g_cm3, tensile_strength_cn_dtex, tensile_strength_gpa,
                tensile_modulus_gpa, elongation_at_break_pct, moisture_regain_pct, loi_pct,
                melting_point_c, max_service_temp_c, textile_domain, typical_applications, representative_brands,
                tech_status_2026, is_bio_based, is_biodegradable, is_high_performance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cat_id, f["code"], f["name_zh"], f["name_en"], f.get("chemical_name"), f.get("chemical_formula"),
            f.get("cas_number"), f.get("generation"), f.get("discovery_year"), f.get("commercial_year"), f.get("pioneering_entity"),
            f.get("spinning_method"), f.get("density_g_cm3"), f.get("tensile_strength_cn_dtex"), f.get("tensile_strength_gpa"),
            f.get("tensile_modulus_gpa"), f.get("elongation_at_break_pct"), f.get("moisture_regain_pct"), f.get("loi_pct"),
            f.get("melting_point_c"), f.get("max_service_temp_c"), domain, f.get("typical_applications"), f.get("representative_brands"),
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

        # Insert textile profile
        tp = TEXTILE_PROFILES_DATA.get(f["code"], {})
        cursor.execute("""
            INSERT INTO textile_profiles (
                fiber_id, cross_section_shape, fineness_dtex_range, yarn_processing_types,
                hand_feel_drape, dyeing_characteristics, colorfastness_rating,
                moisture_thermal_comfort, pilling_abrasion_grade, elastic_recovery_feature,
                recommended_blends, weaving_knitting_suitability, care_and_washing, eco_certifications
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fiber_id,
            tp.get("cross_section_shape", "常规截面"),
            tp.get("fineness_dtex_range", "常规规格"),
            tp.get("yarn_processing_types", "机织/针织长丝与短纤纱"),
            tp.get("hand_feel_drape", "典型纺织手感"),
            tp.get("dyeing_characteristics", "常规印染工艺"),
            tp.get("colorfastness_rating", "耐洗4级"),
            tp.get("moisture_thermal_comfort", "良好服用舒适性"),
            tp.get("pilling_abrasion_grade", "耐磨抗起球良好"),
            tp.get("elastic_recovery_feature", "尺寸稳定性好"),
            tp.get("recommended_blends", "支持多种天然与化学纤维混纺"),
            tp.get("weaving_knitting_suitability", "圆机针织与机织通用"),
            tp.get("care_and_washing", "常规水洗保养"),
            tp.get("eco_certifications", "符合生态纺织品标准")
        ))

        # Insert into FTS5 index
        cursor.execute("""
            INSERT INTO fibers_fts (
                rowid, code, name_zh, name_en, chemical_name, spinning_method,
                typical_applications, representative_brands, tech_status_2026,
                textile_domain, cross_section_shape, hand_feel_drape,
                dyeing_characteristics, moisture_thermal_comfort, recommended_blends, eco_certifications
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fiber_id, f["code"], f["name_zh"], f["name_en"], f.get("chemical_name", ""),
            f.get("spinning_method", ""), f.get("typical_applications", ""),
            f.get("representative_brands", ""), f.get("tech_status_2026", ""),
            domain, tp.get("cross_section_shape", ""), tp.get("hand_feel_drape", ""),
            tp.get("dyeing_characteristics", ""), tp.get("moisture_thermal_comfort", ""),
            tp.get("recommended_blends", ""), tp.get("eco_certifications", "")
        ))

    # 5. Insert Textile Blends Matrix
    for blend in TEXTILE_BLENDS:
        cursor.execute("""
            INSERT INTO textile_blends_matrix (
                blend_name, fiber_components, classic_ratio,
                synergy_advantages, typical_fabrics, dyeing_finishing_notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, blend)

    conn.commit()
    print("Database built successfully with textile profiles, blends matrix, FTS5, and B-Tree indexes!")

    # 6. Export Enhanced JSON
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

        # Fetch textile profile
        cursor.execute("""
            SELECT cross_section_shape, fineness_dtex_range, yarn_processing_types,
                   hand_feel_drape, dyeing_characteristics, colorfastness_rating,
                   moisture_thermal_comfort, pilling_abrasion_grade, elastic_recovery_feature,
                   recommended_blends, weaving_knitting_suitability, care_and_washing, eco_certifications
            FROM textile_profiles WHERE fiber_id = ?
        """, (fid,))
        tp_row = cursor.fetchone()
        if tp_row:
            tp_cols = [desc[0] for desc in cursor.description]
            record["textile_profile"] = dict(zip(tp_cols, tp_row))
        else:
            record["textile_profile"] = None

        json_records.append(record)

    # Fetch blends matrix for JSON export
    cursor.execute("SELECT blend_name, fiber_components, classic_ratio, synergy_advantages, typical_fabrics, dyeing_finishing_notes FROM textile_blends_matrix ORDER BY id")
    blend_cols = [desc[0] for desc in cursor.description]
    blends_list = [dict(zip(blend_cols, r)) for r in cursor.fetchall()]

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "database_title": "现代纺织化学纤维全景数据库与纺织工程知识库 (Textile Chemical Fibers Comprehensive Dataset - Up to 2026)",
            "version": "2026.2.0-Textile",
            "date": "2026-09-08",
            "textile_focus": "以纺织服装、家纺与产业用纺织品为第一核心，系统覆盖全系化纤物理化学、纺织工程力学、微观截面、染整工艺、混纺协同与生态认证",
            "total_fibers_count": len(json_records),
            "classic_blends_count": len(blends_list),
            "categories_hierarchy": CATEGORIES,
            "classic_blends_matrix": blends_list,
            "fibers": json_records
        }, f, ensure_ascii=False, indent=2)
    print(f"Exported JSON dataset to {JSON_FILE}")

    # 7. Export CSV with UTF-8 BOM for Excel/Numbers compatibility
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        headers = [
            "序号", "分类代号", "分类名称", "纤维代码", "中文通用名", "英文名称", "化学命名",
            "CAS号", "代际划分", "发明年代", "商业化年代", "首发机构/发明人", "纺丝成型工艺",
            "纺织应用领域", "截面微观形态", "典型线密度细度(dtex)", "纱线加工形态", "手感风格与悬垂性",
            "染色特性与适用染料", "热湿舒适性与导湿机制", "抗起球与耐磨评级", "弹性与保形抗皱特性",
            "黄金混纺配伍方案", "适用织造工艺", "洗涤保养与熨烫指南", "生态纺织认证",
            "密度(g/cm³)", "断裂强度(cN/dtex)", "断裂强度(GPa)", "拉伸模量(GPa)", "断裂伸长率(%)",
            "公定回潮率(%)", "极限氧指数LOI(%)", "熔点(°C)", "最高服役温度(°C)",
            "生物基", "可生物降解", "战略高性能", "代表品牌/商标", "典型应用领域", "2026技术成熟度与产业现状"
        ]
        writer.writerow(headers)

        for rec in json_records:
            tp = rec.get("textile_profile") or {}
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
                rec.get("textile_domain") or "",
                tp.get("cross_section_shape") or "",
                tp.get("fineness_dtex_range") or "",
                tp.get("yarn_processing_types") or "",
                tp.get("hand_feel_drape") or "",
                tp.get("dyeing_characteristics") or "",
                tp.get("moisture_thermal_comfort") or "",
                tp.get("pilling_abrasion_grade") or "",
                tp.get("elastic_recovery_feature") or "",
                tp.get("recommended_blends") or "",
                tp.get("weaving_knitting_suitability") or "",
                tp.get("care_and_washing") or "",
                tp.get("eco_certifications") or "",
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
