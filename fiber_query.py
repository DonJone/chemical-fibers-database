#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chemical Fibers Query Engine & Interactive CLI (化学纤维全景数据库智能检索与索引系统 - 截至2026年)
"""
import sys
import sqlite3
import argparse
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chemical_fibers.db")

def get_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: 数据库文件不存在: {DB_PATH}，请先执行 build_all.py")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_fiber_summary(row):
    bio_tag = " [生物基]" if row["is_bio_based"] else ""
    degr_tag = " [可降解]" if row["is_biodegradable"] else ""
    hp_tag = " [战略高性能]" if row["is_high_performance"] else ""
    strength = f"{row['tensile_strength_gpa']} GPa" if row['tensile_strength_gpa'] is not None else "N/A"
    temp = f"{row['max_service_temp_c']} ℃" if row['max_service_temp_c'] is not None else "N/A"
    
    return (
        f"\033[1;36m[{row['code']}]\033[0m \033[1m{row['name_zh']}\033[0m ({row['name_en']})"
        f"{bio_tag}{degr_tag}{hp_tag}\n"
        f"  ├─ 强度: \033[32m{strength}\033[0m | 最高耐温: \033[33m{temp}\033[0m | 密度: {row['density_g_cm3'] or 'N/A'} g/cm³\n"
        f"  ├─ 代表品牌: {row['representative_brands'] or '通用标准品'}\n"
        f"  └─ 典型应用: {row['typical_applications'][:90] + '...' if row['typical_applications'] and len(row['typical_applications']) > 90 else (row['typical_applications'] or 'N/A')}"
    )

def print_detail(row, conn):
    cur = conn.cursor()
    fid = row["id"]
    
    # 别名
    cur.execute("SELECT alias, alias_type FROM fiber_aliases WHERE fiber_id = ?", (fid,))
    aliases = cur.fetchall()
    alias_str = "、".join([f"{a['alias']}({a['alias_type']})" for a in aliases]) if aliases else "无"
    
    # 标准
    cur.execute("SELECT standard_org, standard_code, standard_title FROM fiber_standards WHERE fiber_id = ?", (fid,))
    standards = cur.fetchall()
    std_str = "\n".join([f"    • [{s['standard_org']}] {s['standard_code']}: {s['standard_title']}" for s in standards]) if standards else "    暂未录入标准号"

    # 分类
    cur.execute("SELECT code, name_zh, name_en FROM categories WHERE id = ?", (row["category_id"],))
    cat = cur.fetchone()
    cat_str = f"{cat['name_zh']} ({cat['code']})" if cat else "未知"

    print("\n" + "="*80)
    print(f"\033[1;32m纤维代码: {row['code']}\033[0m | \033[1;37m{row['name_zh']}\033[0m | {row['name_en']}")
    print("="*80)
    print(f"【所属门类】: {cat_str}")
    print(f"【代际划分】: {row['generation'] or 'N/A'} (发明: {row['discovery_year'] or 'N/A'} | 商业化: {row['commercial_year'] or 'N/A'})")
    print(f"【先驱研发】: {row['pioneering_entity'] or 'N/A'}")
    print(f"【化学结构】: {row['chemical_name'] or 'N/A'} | 分子式: {row['chemical_formula'] or 'N/A'} | CAS: {row['cas_number'] or 'N/A'}")
    print(f"【成型工艺】: {row['spinning_method'] or 'N/A'}")
    print("-" * 80)
    print("【关键物理力学与热学常数】:")
    print(f"  • 密度: {row['density_g_cm3'] or 'N/A'} g/cm³")
    print(f"  • 断裂拉伸强度: {row['tensile_strength_gpa'] or 'N/A'} GPa ({row['tensile_strength_cn_dtex'] or 'N/A'} cN/dtex)")
    print(f"  • 拉伸弹性模量: {row['tensile_modulus_gpa'] or 'N/A'} GPa")
    print(f"  • 断裂伸长率: {row['elongation_at_break_pct'] or 'N/A'} %")
    print(f"  • 公定回潮率: {row['moisture_regain_pct'] or 'N/A'} %")
    print(f"  • 极限氧指数(LOI): {row['loi_pct'] or 'N/A'} %")
    print(f"  • 熔点/分解点: {row['melting_point_c'] or '不熔'} ℃")
    print(f"  • 最高连续服役温度: {row['max_service_temp_c'] or 'N/A'} ℃")
    print("-" * 80)
    print(f"【属性标签】: 生物基={bool(row['is_bio_based'])}, 可生物降解={bool(row['is_biodegradable'])}, 战略高性能={bool(row['is_high_performance'])}")
    print(f"【别名/商标对照】: {alias_str}")
    print(f"【代表性品牌】: {row['representative_brands'] or 'N/A'}")
    print(f"【主要应用领域】: {row['typical_applications'] or 'N/A'}")
    print(f"【2026年最新技术现状与发展】: \n  \033[36m{row['tech_status_2026'] or 'N/A'}\033[0m")
    print(f"【遵循规范与参考标准】:\n{std_str}")
    print("="*80 + "\n")

def cmd_search(keyword):
    conn = get_db()
    cur = conn.cursor()
    # 优先 FTS5 全文搜索
    try:
        cur.execute("""
            SELECT f.* FROM fibers_fts 
            JOIN fibers f ON fibers_fts.rowid = f.id
            WHERE fibers_fts MATCH ?
            ORDER BY rank
        """, (keyword,))
        rows = cur.fetchall()
    except Exception:
        # Fallback to standard LIKE if FTS fails
        pattern = f"%{keyword}%"
        cur.execute("""
            SELECT DISTINCT f.* FROM fibers f
            LEFT JOIN fiber_aliases a ON f.id = a.fiber_id
            WHERE f.code LIKE ? OR f.name_zh LIKE ? OR f.name_en LIKE ?
               OR f.chemical_name LIKE ? OR f.typical_applications LIKE ?
               OR f.representative_brands LIKE ? OR a.alias LIKE ?
        """, (pattern, pattern, pattern, pattern, pattern, pattern, pattern))
        rows = cur.fetchall()

    print(f"\n🔍 关键词搜索: '\033[1;33m{keyword}\033[0m' 共找到 \033[1;32m{len(rows)}\033[0m 条纤维记录:\n")
    for r in rows:
        print(format_fiber_summary(r))
        print()
    conn.close()

def cmd_get(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fibers WHERE UPPER(code) = UPPER(?)", (code,))
    row = cur.fetchone()
    if not row:
        # 尝试通过别名查找
        cur.execute("""
            SELECT f.* FROM fibers f 
            JOIN fiber_aliases a ON f.id = a.fiber_id
            WHERE UPPER(a.alias) = UPPER(?)
            LIMIT 1
        """, (code,))
        row = cur.fetchone()

    if row:
        print_detail(row, conn)
    else:
        print(f"\033[31m未找到代码或别名为 '{code}' 的化学纤维。\033[0m")
    conn.close()

def cmd_filter(args):
    conn = get_db()
    cur = conn.cursor()
    conditions = []
    params = []

    if args.category:
        cur.execute("SELECT id FROM categories WHERE UPPER(code) = UPPER(?) OR UPPER(name_zh) LIKE ?", (args.category, f"%{args.category}%"))
        cats = [c["id"] for c in cur.fetchall()]
        if cats:
            placeholders = ",".join("?" * len(cats))
            conditions.append(f"f.category_id IN ({placeholders})")
            params.extend(cats)

    if args.min_strength is not None:
        conditions.append("f.tensile_strength_gpa >= ?")
        params.append(args.min_strength)

    if args.min_temp is not None:
        conditions.append("f.max_service_temp_c >= ?")
        params.append(args.min_temp)

    if args.bio_based:
        conditions.append("f.is_bio_based = 1")

    if args.biodegradable:
        conditions.append("f.is_biodegradable = 1")

    if args.high_perf:
        conditions.append("f.is_high_performance = 1")

    sql = "SELECT f.* FROM fibers f"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY f.tensile_strength_gpa DESC NULLS LAST"

    cur.execute(sql, params)
    rows = cur.fetchall()
    print(f"\n🎯 过滤筛选完成，共匹配到 \033[1;32m{len(rows)}\033[0m 项化学纤维:\n")
    for r in rows:
        print(format_fiber_summary(r))
        print()
    conn.close()

def cmd_stats():
    conn = get_db()
    cur = conn.cursor()
    print("\n" + "="*70)
    print("📊 人类化学纤维全景数据库 (截至2026年) - 统计大屏")
    print("="*70)

    cur.execute("SELECT COUNT(*) FROM fibers")
    total = cur.fetchone()[0]
    print(f"总计收录化学纤维核心品种: \033[1;32m{total}\033[0m 种")

    cur.execute("SELECT COUNT(*) FROM fiber_aliases")
    total_aliases = cur.fetchone()[0]
    print(f"总计建立商标/俗称/别名索引: \033[1;36m{total_aliases}\033[0m 条")

    cur.execute("SELECT COUNT(*) FROM fiber_standards")
    total_stds = cur.fetchone()[0]
    print(f"关联国际/国家标准体系: \033[1;36m{total_stds}\033[0m 项\n")

    print("【特性标签分布】:")
    cur.execute("SELECT SUM(is_bio_based), SUM(is_biodegradable), SUM(is_high_performance) FROM fibers")
    bio, degr, hp = cur.fetchone()
    print(f"  🌱 生物基纤维 (Bio-based):       {bio} 种 (占比 {bio/total*100:.1f}%)")
    print(f"  ♻️  环境生物降解 (Biodegradable):  {degr} 种 (占比 {degr/total*100:.1f}%)")
    print(f"  🛡️  战略级高性能 (High-Perf):     {hp} 种 (占比 {hp/total*100:.1f}%)\n")

    print("【各大门类分布】:")
    cur.execute("""
        SELECT c.name_zh, COUNT(f.id) as cnt
        FROM categories c
        LEFT JOIN categories sub ON sub.parent_id = c.id
        LEFT JOIN fibers f ON (f.category_id = c.id OR f.category_id = sub.id)
        WHERE c.parent_id IS NULL
        GROUP BY c.id
        ORDER BY cnt DESC
    """)
    for row in cur.fetchall():
        print(f"  • {row[0]:<28}: {row[1]:>2} 种")

    print("\n【人类拉伸强度 TOP 5 极端高强纤维】:")
    cur.execute("""
        SELECT code, name_zh, tensile_strength_gpa 
        FROM fibers 
        WHERE tensile_strength_gpa IS NOT NULL 
        ORDER BY tensile_strength_gpa DESC LIMIT 5
    """)
    for r in cur.fetchall():
        print(f"  🥇 [{r['code']:<10}] {r['name_zh']:<26}: {r['tensile_strength_gpa']} GPa")

    print("\n【人类最高耐温极限 TOP 5 特种耐火纤维】:")
    cur.execute("""
        SELECT code, name_zh, max_service_temp_c 
        FROM fibers 
        WHERE max_service_temp_c IS NOT NULL 
        ORDER BY max_service_temp_c DESC LIMIT 5
    """)
    for r in cur.fetchall():
        print(f"  🔥 [{r['code']:<10}] {r['name_zh']:<26}: 连续服役 {r['max_service_temp_c']} ℃")

    print("="*70 + "\n")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="化学纤维全景数据库检索管理系统 (2026)")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # search
    p_search = subparsers.add_parser("search", help="全文关键词智能检索 (中英文/应用/商标)")
    p_search.add_argument("keyword", help="搜索关键词 (如: 芳纶, Kevlar, 防弹, 生物基, 导电)")

    # get
    p_get = subparsers.add_parser("get", help="查看指定纤维代码或别名的完整详情报告")
    p_get.add_argument("code", help="纤维简写代号或商标名 (如: PPTA, PET, PBO, T1000, 莱赛尔)")

    # filter
    p_filter = subparsers.add_parser("filter", help="按物理/化学/特性条件多维筛选")
    p_filter.add_argument("--category", help="分类代号或名称")
    p_filter.add_argument("--min-strength", type=float, help="最低抗拉强度 (GPa)")
    p_filter.add_argument("--min-temp", type=float, help="最低连续服役温度 (°C)")
    p_filter.add_argument("--bio-based", action="store_true", help="仅筛选生物基纤维")
    p_filter.add_argument("--biodegradable", action="store_true", help="仅筛选生物可降解纤维")
    p_filter.add_argument("--high-perf", action="store_true", help="仅筛选战略高性能纤维")

    # stats
    subparsers.add_parser("stats", help="查看数据库全景统计与性能榜单")

    # list
    p_list = subparsers.add_parser("list", help="罗列纤维精简索引清单")
    p_list.add_argument("--category", help="可选限制分类")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args.keyword)
    elif args.command == "get":
        cmd_get(args.code)
    elif args.command == "filter":
        cmd_filter(args)
    elif args.command == "stats":
        cmd_stats()
    elif args.command == "list":
        cmd_filter(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
