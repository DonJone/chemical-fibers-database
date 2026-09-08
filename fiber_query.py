#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代纺织化学纤维与工程知识库交互式智能检索系统 (Textile Chemical Fibers CLI Query Engine)
截至2026年，以纺织服装、家纺与产业用纺织品为第一核心，系统覆盖全系化纤与面料工程知识
"""
import sys
import sqlite3
import argparse
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chemical_fibers.db")

def get_db():
    if not os.path.exists(DB_PATH):
        print(f"Error: 数据库文件不存在: {DB_PATH}，请先执行 build_all.py 构建数据库")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_fiber_summary(row, conn=None):
    bio_tag = " [🌱生物基]" if row["is_bio_based"] else ""
    degr_tag = " [♻️可降解]" if row["is_biodegradable"] else ""
    hp_tag = " [🛡️特种高性能]" if row["is_high_performance"] else ""
    domain = row["textile_domain"] if "textile_domain" in row.keys() else "综合纺织品"
    strength = f"{row['tensile_strength_gpa']} GPa" if row['tensile_strength_gpa'] is not None else "N/A"
    regain = f"{row['moisture_regain_pct']} %" if row['moisture_regain_pct'] is not None else "N/A"
    
    # 截面信息
    cs = ""
    if conn and "id" in row.keys():
        cur = conn.cursor()
        cur.execute("SELECT cross_section_shape, hand_feel_drape FROM textile_profiles WHERE fiber_id = ?", (row["id"],))
        tp = cur.fetchone()
        if tp and tp["cross_section_shape"]:
            cs = f" | 截面: {tp['cross_section_shape'].split('(')[0].strip()}"
    
    return (
        f"\033[1;36m[{row['code']}]\033[0m \033[1m{row['name_zh']}\033[0m ({row['name_en']})"
        f"{bio_tag}{degr_tag}{hp_tag}\n"
        f"  ├─ \033[35m【纺织门类】: {domain}\033[0m{cs}\n"
        f"  ├─ 物理指标: 强力 \033[32m{strength}\033[0m | 公定回潮率: \033[34m{regain}\033[0m | 密度: {row['density_g_cm3'] or 'N/A'} g/cm³\n"
        f"  ├─ 代表品牌: {row['representative_brands'] or '通用标准品'}\n"
        f"  └─ 典型应用: {row['typical_applications'][:95] + '...' if row['typical_applications'] and len(row['typical_applications']) > 95 else (row['typical_applications'] or 'N/A')}"
    )

def print_textile_card(row, conn):
    cur = conn.cursor()
    fid = row["id"]
    cur.execute("SELECT * FROM textile_profiles WHERE fiber_id = ?", (fid,))
    tp = cur.fetchone()
    if not tp:
        print("暂无纺织工程档案。")
        return

    print("\n" + "─"*80)
    print(f"\033[1;35m🧵 纺织工程与面料深度知识档案: [{row['code']}] {row['name_zh']}\033[0m")
    print("─"*80)
    print(f"  • \033[1m应用终端门类\033[0m: {row['textile_domain'] or '综合纺织品'}")
    print(f"  • \033[1m微观截面形态\033[0m: {tp['cross_section_shape'] or '常规截面'}")
    print(f"  • \033[1m典型细度范围\033[0m: {tp['fineness_dtex_range'] or 'N/A'}")
    print(f"  • \033[1m纱线加工形态\033[0m: {tp['yarn_processing_types'] or 'N/A'}")
    print(f"  • \033[1m手感风格触感\033[0m: \033[33m{tp['hand_feel_drape'] or 'N/A'}\033[0m")
    print(f"  • \033[1m印染与适用染料\033[0m: {tp['dyeing_characteristics'] or 'N/A'}")
    print(f"  • \033[1m色牢度评级\033[0m: {tp['colorfastness_rating'] or '耐洗4级'}")
    print(f"  • \033[1m热湿舒适与导湿\033[0m: \033[36m{tp['moisture_thermal_comfort'] or 'N/A'}\033[0m")
    print(f"  • \033[1m抗起球与耐磨\033[0m: {tp['pilling_abrasion_grade'] or 'N/A'}")
    print(f"  • \033[1m弹性与抗皱保形\033[0m: {tp['elastic_recovery_feature'] or 'N/A'}")
    print(f"  • \033[1;32m黄金混纺配伍方案\033[0m: \033[32m{tp['recommended_blends'] or 'N/A'}\033[0m")
    print(f"  • \033[1m适用织造工艺\033[0m: {tp['weaving_knitting_suitability'] or 'N/A'}")
    print(f"  • \033[1m洗涤保养与熨烫\033[0m: {tp['care_and_washing'] or 'N/A'}")
    print(f"  • \033[1;34m生态纺织品认证\033[0m: \033[34m{tp['eco_certifications'] or '符合标准'}\033[0m")
    print("─"*80)

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

    print("\n" + "="*85)
    print(f"\033[1;32m纤维代码: {row['code']}\033[0m | \033[1;37m{row['name_zh']}\033[0m | {row['name_en']}")
    print("="*85)
    print(f"【所属门类】: {cat_str}")
    print(f"【纺织领域】: \033[35m{row['textile_domain'] or '综合全领域'}\033[0m")
    print(f"【代际划分】: {row['generation'] or 'N/A'} (发明: {row['discovery_year'] or 'N/A'} | 商业化: {row['commercial_year'] or 'N/A'})")
    print(f"【先驱研发】: {row['pioneering_entity'] or 'N/A'}")
    print(f"【化学结构】: {row['chemical_name'] or 'N/A'} | 分子式: {row['chemical_formula'] or 'N/A'} | CAS: {row['cas_number'] or 'N/A'}")
    print(f"【成型工艺】: {row['spinning_method'] or 'N/A'}")
    print("-" * 85)
    print("【关键物理力学与热学指标】:")
    print(f"  • 密度: {row['density_g_cm3'] or 'N/A'} g/cm³")
    print(f"  • 断裂拉伸强度: {row['tensile_strength_gpa'] or 'N/A'} GPa ({row['tensile_strength_cn_dtex'] or 'N/A'} cN/dtex)")
    print(f"  • 拉伸弹性模量: {row['tensile_modulus_gpa'] or 'N/A'} GPa")
    print(f"  • 断裂伸长率: {row['elongation_at_break_pct'] or 'N/A'} %")
    print(f"  • 公定回潮率: \033[1;34m{row['moisture_regain_pct'] or 'N/A'} %\033[0m (吸湿舒适度关键指标)")
    print(f"  • 极限氧指数(LOI): \033[1;31m{row['loi_pct'] or 'N/A'} %\033[0m (阻燃防火指标)")
    print(f"  • 熔点/分解点: {row['melting_point_c'] or '不熔/碳化'} ℃")
    print(f"  • 最高连续服役温度: {row['max_service_temp_c'] or 'N/A'} ℃")
    print("-" * 85)
    print(f"【属性标签】: 生物基={bool(row['is_bio_based'])}, 可生物降解={bool(row['is_biodegradable'])}, 战略高性能={bool(row['is_high_performance'])}")
    print(f"【别名/商标对照】: {alias_str}")
    print(f"【代表性品牌】: {row['representative_brands'] or 'N/A'}")
    print(f"【主要应用场景】: {row['typical_applications'] or 'N/A'}")
    print(f"【2026年最新技术产业进展】: \n  \033[36m{row['tech_status_2026'] or 'N/A'}\033[0m")
    print(f"【技术规范与纺织行业标准】:\n{std_str}")
    
    # 打印纺织深度档案
    print_textile_card(row, conn)
    print("="*85 + "\n")

def cmd_search(keyword):
    conn = get_db()
    cur = conn.cursor()
    matched_rows = []
    seen_ids = set()

    # 1. 如果关键词长度 >= 3，尝试 FTS5 全文倒排检索
    if len(keyword) >= 3:
        try:
            cur.execute("""
                SELECT f.* FROM fibers_fts 
                JOIN fibers f ON fibers_fts.rowid = f.id
                WHERE fibers_fts MATCH ?
                ORDER BY rank
            """, (keyword,))
            for r in cur.fetchall():
                if r["id"] not in seen_ids:
                    matched_rows.append(r)
                    seen_ids.add(r["id"])
        except Exception:
            pass

    # 2. 结合模糊 LIKE 搜索覆盖短关键词、别名及纺织深度档案
    pattern = f"%{keyword}%"
    cur.execute("""
        SELECT DISTINCT f.* FROM fibers f
        LEFT JOIN fiber_aliases a ON f.id = a.fiber_id
        LEFT JOIN textile_profiles tp ON f.id = tp.fiber_id
        WHERE f.code LIKE ? OR f.name_zh LIKE ? OR f.name_en LIKE ?
           OR f.chemical_name LIKE ? OR f.typical_applications LIKE ?
           OR f.representative_brands LIKE ? OR a.alias LIKE ?
           OR f.textile_domain LIKE ? OR tp.cross_section_shape LIKE ?
           OR tp.hand_feel_drape LIKE ? OR tp.dyeing_characteristics LIKE ?
           OR tp.moisture_thermal_comfort LIKE ? OR tp.recommended_blends LIKE ?
           OR tp.weaving_knitting_suitability LIKE ? OR tp.eco_certifications LIKE ?
    """, (pattern, pattern, pattern, pattern, pattern, pattern, pattern,
          pattern, pattern, pattern, pattern, pattern, pattern, pattern, pattern))
    for r in cur.fetchall():
        if r["id"] not in seen_ids:
            matched_rows.append(r)
            seen_ids.add(r["id"])

    print(f"\n🔍 纺织与化纤知识库检索: '\033[1;33m{keyword}\033[0m' 共找到 \033[1;32m{len(matched_rows)}\033[0m 项相关条目:\n")
    for r in matched_rows:
        print(format_fiber_summary(r, conn))
        print()
    conn.close()

def cmd_get(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fibers WHERE UPPER(code) = UPPER(?)", (code,))
    row = cur.fetchone()
    if not row:
        # 尝试通过中文名精准匹配
        cur.execute("SELECT * FROM fibers WHERE name_zh LIKE ?", (f"%{code}%",))
        row = cur.fetchone()
    if not row:
        # 尝试通过别名反查
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
        print(f"\033[31m未找到代码、名称或别名为 '{code}' 的纤维。\033[0m")
    conn.close()

def cmd_textile(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fibers WHERE UPPER(code) = UPPER(?)", (code,))
    row = cur.fetchone()
    if not row:
        cur.execute("SELECT * FROM fibers WHERE name_zh LIKE ?", (f"%{code}%",))
        row = cur.fetchone()
    if not row:
        cur.execute("""
            SELECT f.* FROM fibers f JOIN fiber_aliases a ON f.id = a.fiber_id
            WHERE UPPER(a.alias) = UPPER(?) LIMIT 1
        """, (code,))
        row = cur.fetchone()

    if row:
        print_textile_card(row, conn)
    else:
        print(f"\033[31m未找到代码或名称为 '{code}' 的纤维。\033[0m")
    conn.close()

def cmd_blend(query=None):
    conn = get_db()
    cur = conn.cursor()
    if query:
        pattern = f"%{query}%"
        cur.execute("""
            SELECT * FROM textile_blends_matrix 
            WHERE blend_name LIKE ? OR fiber_components LIKE ? OR synergy_advantages LIKE ? OR typical_fabrics LIKE ?
            ORDER BY id
        """, (pattern, pattern, pattern, pattern))
    else:
        cur.execute("SELECT * FROM textile_blends_matrix ORDER BY id")
    rows = cur.fetchall()

    print("\n" + "="*85)
    print("🎨 现代纺织经典混纺配伍与协同方案矩阵 (Classic Textile Blends Matrix)")
    print("="*85)
    if not rows:
        print(f"未找到与 '{query}' 相关的混纺方案。")
    for r in rows:
        print(f"\n\033[1;32m【方案 {r['id']}】{r['blend_name']}\033[0m")
        print(f"  ├─ 纤维组分: \033[37m{r['fiber_components']}\033[0m")
        print(f"  ├─ 黄金配比: \033[1;36m{r['classic_ratio']}\033[0m")
        print(f"  ├─ 协同优势: \033[33m{r['synergy_advantages']}\033[0m")
        print(f"  ├─ 典型面料与服饰: {r['typical_fabrics']}")
        print(f"  └─ 染整工艺与注意事项: {r['dyeing_finishing_notes']}")
    print("\n" + "="*85 + "\n")
    conn.close()

def cmd_filter(args):
    conn = get_db()
    cur = conn.cursor()
    conditions = []
    params = []

    if args.domain:
        conditions.append("f.textile_domain LIKE ?")
        params.append(f"%{args.domain}%")

    if args.cross_section:
        conditions.append("tp.cross_section_shape LIKE ?")
        params.append(f"%{args.cross_section}%")

    if args.dye:
        conditions.append("tp.dyeing_characteristics LIKE ?")
        params.append(f"%{args.dye}%")

    if args.wicking:
        conditions.append("(tp.moisture_thermal_comfort LIKE '%导湿%' OR tp.moisture_thermal_comfort LIKE '%排汗%' OR tp.cross_section_shape LIKE '%十字%')")

    if args.high_regain:
        conditions.append("f.moisture_regain_pct >= 8.0")

    if args.flame_retardant:
        conditions.append("(f.loi_pct >= 28.0 OR tp.moisture_thermal_comfort LIKE '%阻燃%')")

    if args.eco:
        conditions.append("(f.is_bio_based = 1 OR f.is_biodegradable = 1 OR tp.eco_certifications LIKE '%OEKO%' OR tp.eco_certifications LIKE '%GRS%')")

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

    sql = """
        SELECT f.* FROM fibers f 
        LEFT JOIN textile_profiles tp ON f.id = tp.fiber_id
    """
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY f.id"

    cur.execute(sql, params)
    rows = cur.fetchall()
    print(f"\n🎯 纺织多维属性筛选完成，共匹配到 \033[1;32m{len(rows)}\033[0m 项化学纤维:\n")
    for r in rows:
        print(format_fiber_summary(r, conn))
        print()
    conn.close()

def cmd_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM fibers")
    total_fibers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM textile_blends_matrix")
    total_blends = cur.fetchone()[0]

    print("\n" + "="*80)
    print("📊 现代纺织化学纤维与工程知识库全景统计仪表盘 (Textile Dashboard)")
    print("="*80)
    print(f"  • 总收录纤维品种: \033[1;32m{total_fibers}\033[0m 种")
    print(f"  • 经典纺织混纺协同方案: \033[1;36m{total_blends}\033[0m 套黄金配比")

    # 纺织门类分布
    print("\n【纺织产业应用门类分布】:")
    cur.execute("""
        SELECT textile_domain, COUNT(*) as cnt 
        FROM fibers 
        GROUP BY textile_domain 
        ORDER BY cnt DESC
    """)
    for r in cur.fetchall():
        pct = round(r["cnt"] / total_fibers * 100, 1)
        bar = "█" * int(pct / 4)
        print(f"  {r['textile_domain'][:25]:<26} : {r['cnt']:>3} 种 ({pct:>4}%) \033[35m{bar}\033[0m")

    # 回潮率与服用舒适度分布
    print("\n【公定回潮率与湿热舒适度区间分布】:")
    cur.execute("SELECT COUNT(*) FROM fibers WHERE moisture_regain_pct >= 10.0")
    c_high = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fibers WHERE moisture_regain_pct >= 2.0 AND moisture_regain_pct < 10.0")
    c_med = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fibers WHERE moisture_regain_pct < 2.0")
    c_low = cur.fetchone()[0]
    print(f"  高吸湿亲肤舒适群 (回潮率 >= 10.0%，如粘胶/莫代尔/天丝/海藻/铜氨): {c_high} 种 ({round(c_high/total_fibers*100, 1)}%)")
    print(f"  适度吸湿平滑群   (回潮率 2.0% - 9.9%，如锦纶/芳纶/腈纶/大豆蛋白):   {c_med} 种 ({round(c_med/total_fibers*100, 1)}%)")
    print(f"  疏水极速快干群   (回潮率 < 2.0%，如涤纶/丙纶/超高分子量聚乙烯):     {c_low} 种 ({round(c_low/total_fibers*100, 1)}%)")

    # 绿色可持续与生态认证
    print("\n【绿色与可持续环保特征】:")
    cur.execute("SELECT COUNT(*) FROM fibers WHERE is_bio_based = 1")
    bio_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fibers WHERE is_biodegradable = 1")
    degr_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fibers WHERE is_high_performance = 1")
    hp_count = cur.fetchone()[0]
    print(f"  🌱 生物基原料来源纤维:     {bio_count:>3} 种 ({round(bio_count/total_fibers*100, 1)}%)")
    print(f"  ♻️ 自然环境可生物降解纤维: {degr_count:>3} 种 ({round(degr_count/total_fibers*100, 1)}%)")
    print(f"  🛡️ 战略与尖端高性能纤维:   {hp_count:>3} 种 ({round(hp_count/total_fibers*100, 1)}%)")

    # 典型截面形态统计
    print("\n【主要微观异形与复合截面形态收录】:")
    for kw, name in [("十字", "十字形/四槽形吸湿排汗截面"), ("中空", "单孔/多孔中空轻量蓄热截面"), 
                     ("海岛", "海岛超微细开纤复合截面"), ("橘瓣", "橘瓣裂片型超细开纤截面"),
                     ("并列", "PTT/PET双组分并列自卷曲截面"), ("锯齿", "锯齿多微孔吸液亲水截面"),
                     ("三叶", "三叶形/三角异形闪光仿丝截面")]:
        cur.execute("SELECT COUNT(*) FROM textile_profiles WHERE cross_section_shape LIKE ?", (f"%{kw}%",))
        cnt = cur.fetchone()[0]
        print(f"  • {name:<28}: {cnt:>2} 个主要品种")

    print("="*80 + "\n")
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="现代纺织化学纤维与纺织工程知识库 CLI 智能检索系统 (截至2026年)")
    subparsers = parser.add_subparsers(dest="subcommand", help="可选操作子命令")

    # 1. 关键词全文检索
    p_search = subparsers.add_parser("search", help="全文智能模糊检索（支持纤维名称、商标、别名、截面、染料、混纺等）")
    p_search.add_argument("keyword", help="搜索关键词 (如: 吸湿排汗, 凉感, 莫代尔, 分散染料, 德绒, 麂皮绒)")

    # 2. 单品种技术白皮书
    p_get = subparsers.add_parser("get", help="查看指定纤维品种的完整物理化学与纺织工程白皮书卡片")
    p_get.add_argument("code", help="纤维代码、通用名或商标别名 (如: COOLMAX, PET, Tencel, 凯夫拉)")

    # 3. 专项纺织技术卡片
    p_textile = subparsers.add_parser("textile", help="专项查看指定纤维的纺织工程面料深度档案")
    p_textile.add_argument("code", help="纤维代码或通用名 (如: COOLMAX, MICRO-CMD, T400)")

    # 4. 经典混纺配伍查询
    p_blend = subparsers.add_parser("blend", help="查询纺织经典混纺配伍与协同效应矩阵")
    p_blend.add_argument("query", nargs="?", default=None, help="混纺关键词 (如: 涤棉, 羊毛, 莫代尔, 阻燃, 或留空查看全量矩阵)")

    # 5. 多维属性筛选
    p_filter = subparsers.add_parser("filter", help="根据纺织门类、微观截面、染料及力学热学指标进行多维过滤筛选")
    p_filter.add_argument("--domain", help="纺织应用门类 (服装, 家纺, 产业用)")
    p_filter.add_argument("--cross-section", help="微观截面形态 (十字, 中空, 海岛, 橘瓣, 三叶)")
    p_filter.add_argument("--dye", help="印染适用染料 (分散染料, 活性染料, 阳离子, 酸性)")
    p_filter.add_argument("--wicking", action="store_true", help="筛选吸湿排汗速干纤维")
    p_filter.add_argument("--high-regain", action="store_true", help="筛选高回潮率吸湿亲肤纤维 (回潮率>=8%)")
    p_filter.add_argument("--flame-retardant", action="store_true", help="筛选阻燃防火纤维 (LOI>=28%)")
    p_filter.add_argument("--eco", action="store_true", help="筛选绿色生态环保认证纤维")
    p_filter.add_argument("--category", help="按分类代号过滤 (如: SYN_DIFF_PET, REG_CELL, SYN_MICRO)")
    p_filter.add_argument("--min-strength", type=float, help="最低断裂强度 (GPa)")
    p_filter.add_argument("--min-temp", type=float, help="最低连续耐热温度 (℃)")
    p_filter.add_argument("--bio-based", action="store_true", help="仅筛选生物基纤维")
    p_filter.add_argument("--biodegradable", action="store_true", help="仅筛选可生物降解纤维")
    p_filter.add_argument("--high-perf", action="store_true", help="仅筛选战略级高性能纤维")

    # 6. 统计大盘
    p_stats = subparsers.add_parser("stats", help="查看纺织化学纤维与工程数据库全景统计大盘")

    args = parser.parse_args()

    if args.subcommand == "search":
        cmd_search(args.keyword)
    elif args.subcommand == "get":
        cmd_get(args.code)
    elif args.subcommand == "textile":
        cmd_textile(args.code)
    elif args.subcommand == "blend":
        cmd_blend(args.query)
    elif args.subcommand == "filter":
        cmd_filter(args)
    elif args.subcommand == "stats":
        cmd_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
