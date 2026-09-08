"""
化学纤维全景数据库构建脚本 (Chemical Fibers Comprehensive Database Builder - 2026)
涵盖人类截至2026年已发现、工业化或处于前沿研发阶段的全部化学纤维体系（再生纤维、常规合成纤维、生物基降解纤维、高性能特种纤维、碳基纤维、无机陶瓷/金属纤维、前沿智能仿生纤维）
"""

import sqlite3
import json
import csv
import os

DB_PATH = "chemical_fibers.db"
JSON_PATH = "chemical_fibers_dataset.json"
CSV_PATH = "chemical_fibers_catalog.csv"
SQL_SCHEMA_PATH = "schema.sql"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_schema(conn):
    schema_sql = """
    -- 分类体系表
    DROP TABLE IF EXISTS fiber_standards;
    DROP TABLE IF EXISTS fiber_aliases;
    DROP TABLE IF EXISTS fibers_fts;
    DROP TABLE IF EXISTS fibers;
    DROP TABLE IF EXISTS categories;

    CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code VARCHAR(20) UNIQUE NOT NULL,
        name_zh VARCHAR(100) NOT NULL,
        name_en VARCHAR(100) NOT NULL,
        parent_id INTEGER REFERENCES categories(id),
        description TEXT
    );

    -- 化学纤维核心实体表
    CREATE TABLE fibers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL REFERENCES categories(id),
        code VARCHAR(30) UNIQUE NOT NULL,             -- 常用代号/简写 (如 PET, PA66, PPTA, PBO, PAN-CF)
        name_zh VARCHAR(100) NOT NULL,                -- 中文通用名称 (如 聚对苯二甲酸乙二醇酯纤维/涤纶)
        name_en VARCHAR(100) NOT NULL,                -- 英文名称 (如 Polyethylene Terephthalate Fiber / Polyester)
        chemical_name VARCHAR(150),                   -- 规范化学名
        chemical_formula VARCHAR(150),                -- 分子式 / 重复单元式
        cas_number VARCHAR(50),                       -- CAS登记号
        generation VARCHAR(50),                       -- 纤维代际 (第1代传统通用, 第2代改性差别化, 第3代高性能特种, 第4代前沿智能绿色)
        discovery_year VARCHAR(30),                   -- 实验室合成/发明年代
        commercial_year VARCHAR(30),                  -- 首次工业化商业应用年代
        pioneering_entity VARCHAR(150),               -- 原创发明人或首发企业机构
        spinning_method TEXT,                         -- 主要纺丝与成型工艺 (熔融/湿法/干法/凝胶/静电/液晶相/CVD等)
        
        -- 物理力学与热学特性指标 (基准参考值)
        density_g_cm3 REAL,                           -- 密度 (g/cm³)
        tensile_strength_cn_dtex REAL,                -- 断裂强度 (cN/dtex)
        tensile_strength_gpa REAL,                    -- 断裂强度 (GPa)
        tensile_modulus_gpa REAL,                     -- 拉伸弹性模量 (GPa)
        elongation_at_break_pct REAL,                 -- 断裂伸长率 (%)
        moisture_regain_pct REAL,                     -- 公定回潮率 (%)
        loi_pct REAL,                                 -- 极限氧指数 LOI (%)
        melting_point_c REAL,                         -- 熔点 (°C, 若不熔则注分解点)
        max_service_temp_c REAL,                      -- 长期连续耐热/服役温度 (°C)
        
        -- 核心应用与属性标签
        typical_applications TEXT,                    -- 典型工业/民用/尖端国防应用
        representative_brands TEXT,                   -- 代表性历史与现存商业品牌
        tech_status_2026 TEXT,                        -- 截至2026年最新产业化水平与前沿进展
        is_bio_based BOOLEAN DEFAULT 0,               -- 是否生物基原料来源
        is_biodegradable BOOLEAN DEFAULT 0,           -- 是否具有环境生物降解性
        is_high_performance BOOLEAN DEFAULT 0         -- 是否属于战略级高性能/特种纤维
    );

    -- 别名与商标对照表 (用于多维度反查与智能检索)
    CREATE TABLE fiber_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fiber_id INTEGER NOT NULL REFERENCES fibers(id) ON DELETE CASCADE,
        alias VARCHAR(100) NOT NULL,
        alias_type VARCHAR(50) NOT NULL               -- trade_name(商标), abbreviation(缩写), colloquial(俗称), iso_code(国际代码)
    );

    -- 关联标准化规范表 (GB/T, ISO, ASTM, FZ/T 等)
    CREATE TABLE fiber_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fiber_id INTEGER NOT NULL REFERENCES fibers(id) ON DELETE CASCADE,
        standard_org VARCHAR(50) NOT NULL,            -- ISO, GB, ASTM, FZ, DIN 等
        standard_code VARCHAR(100) NOT NULL,          -- 标准编号 (如 ISO 2076, GB/T 4146)
        standard_title TEXT                           -- 标准全称
    );

    -- 建立高性能 B-Tree 索引
    CREATE INDEX idx_fibers_code ON fibers(code);
    CREATE INDEX idx_fibers_category ON fibers(category_id);
    CREATE INDEX idx_fibers_density ON fibers(density_g_cm3);
    CREATE INDEX idx_fibers_strength_cn ON fibers(tensile_strength_cn_dtex);
    CREATE INDEX idx_fibers_strength_gpa ON fibers(tensile_strength_gpa);
    CREATE INDEX idx_fibers_modulus ON fibers(tensile_modulus_gpa);
    CREATE INDEX idx_fibers_loi ON fibers(loi_pct);
    CREATE INDEX idx_fibers_temp ON fibers(max_service_temp_c);
    CREATE INDEX idx_fibers_tags ON fibers(is_bio_based, is_biodegradable, is_high_performance);
    CREATE INDEX idx_aliases_lookup ON fiber_aliases(alias);

    -- 全文检索引擎 FTS5 (支持中文与英文模糊组合智能索引)
    CREATE VIRTUAL TABLE fibers_fts USING fts5(
        code,
        name_zh,
        name_en,
        chemical_name,
        spinning_method,
        typical_applications,
        representative_brands,
        tech_status_2026,
        content='fibers',
        content_rowid='id'
    );
    """
    conn.executescript(schema_sql)
    with open(SQL_SCHEMA_PATH, "w", encoding="utf-8") as f:
        f.write(schema_sql)

def main():
    conn = get_db_connection()
    init_schema(conn)
    print("Schema initialized successfully.")
    conn.close()

if __name__ == "__main__":
    main()
