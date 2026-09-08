# -*- coding: utf-8 -*-
"""
Generator for chemical_fibers_encyclopedia.md
人类化学纤维全景大百科与多维索引全集 (截至2026年)
"""
import sqlite3
import os

DB_PATH = "chemical_fibers.db"
OUTPUT_MD = "chemical_fibers_encyclopedia.md"

def generate_markdown():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM fibers")
    total_fibers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NULL")
    top_cat_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NOT NULL")
    sub_cat_count = cur.fetchone()[0]

    md = []
    md.append("# 人类化学纤维全景大百科与多维索引全集 (截至2026年)\n")
    md.append("> **权威性与全景视野**：收录人类工业革命至今（截至2026年）已发现、规模化量产及前沿处于颠覆性研发阶段的全部化学纤维体系（涵盖再生人造纤维、常规合成纤维、生物基生物降解纤维、高性能有机特种纤维、碳基纤维、无机非金属与陶瓷金属纤维、前沿智能仿生光电纤维）。\n")
    md.append(f"- **收录核心纤维品种**：`{total_fibers}` 种化学纤维大类及亚型")
    md.append(f"- **分类层级架构**：`{top_cat_count}` 个一级顶级门类，`{sub_cat_count}` 个专业细分子类")
    md.append("- **底层存储与索引引擎**：SQLite3 + B-Tree 复合索引 + FTS5 全文倒排检索引擎\n")
    md.append("---\n")

    # 目录导航
    md.append("## 目录导航 (Table of Contents)\n")
    cur.execute("SELECT id, code, name_zh, name_en FROM categories WHERE parent_id IS NULL ORDER BY id")
    top_cats = cur.fetchall()
    for tc in top_cats:
        anchor = tc['code'].lower()
        md.append(f"- [{tc['name_zh']} ({tc['name_en']})](#{anchor})")
        cur.execute("SELECT id, code, name_zh, name_en FROM categories WHERE parent_id = ? ORDER BY id", (tc["id"],))
        sub_cats = cur.fetchall()
        for sc in sub_cats:
            sub_anchor = sc['code'].lower().replace('_', '-')
            md.append(f"  - [{sc['name_zh']} ({sc['code']})](#{sub_anchor})")
    md.append("- [人类化学纤维性能极限排行榜 (Top Rankings)](#extreme-rankings)")
    md.append("- [多维检索与索引调用指南 (Query Guide)](#query-guide)\n")
    md.append("---\n")

    # 分大类输出
    for tc in top_cats:
        md.append(f"<a id=\"{tc['code'].lower()}\"></a>\n")
        md.append(f"## 🏛️ {tc['name_zh']} ({tc['name_en']})\n")
        
        cur.execute("SELECT id, code, name_zh, name_en, description FROM categories WHERE parent_id = ? ORDER BY id", (tc["id"],))
        sub_cats = cur.fetchall()

        for sc in sub_cats:
            md.append(f"<a id=\"{sc['code'].lower().replace('_', '-')}\"></a>\n")
            md.append(f"### 📂 {sc['name_zh']} ({sc['code']})\n")
            if sc["description"]:
                md.append(f"> *子类释义*：{sc['description']}\n")

            cur.execute("""
                SELECT * FROM fibers 
                WHERE category_id = ? 
                ORDER BY id
            """, (sc["id"],))
            fibers = cur.fetchall()

            if not fibers:
                md.append("*本子类暂无条目*\n")
                continue

            for f in fibers:
                fid = f["id"]
                # Aliases
                cur.execute("SELECT alias, alias_type FROM fiber_aliases WHERE fiber_id = ?", (fid,))
                aliases = cur.fetchall()
                alias_str = "、".join([f"`{a['alias']}`" for a in aliases]) if aliases else "无"

                # Standards
                cur.execute("SELECT standard_org, standard_code, standard_title FROM fiber_standards WHERE fiber_id = ?", (fid,))
                stds = cur.fetchall()
                std_str = "; ".join([f"**[{s['standard_org']}]** `{s['standard_code']}`" for s in stds]) if stds else "参考通用化学品规范"

                # Tags
                tags = []
                if f["is_bio_based"]:
                    tags.append("🌱 生物基 (Bio-based)")
                if f["is_biodegradable"]:
                    tags.append("♻️ 生物降解 (Biodegradable)")
                if f["is_high_performance"]:
                    tags.append("🛡️ 战略高性能 (High-Performance)")
                tag_str = " | ".join(tags) if tags else "常规合成/通用纤维"

                md.append(f"#### 🧬 [{f['code']}] {f['name_zh']} ({f['name_en']})\n")
                md.append(f"- **特征标识**：{tag_str}")
                md.append(f"- **历史年表**：{f['generation']} | 发明年代: `{f['discovery_year'] or '未知'}` | 商业化年代: `{f['commercial_year'] or '未知'}`")
                md.append(f"- **先驱研发**：{f['pioneering_entity'] or '未记载'}")
                md.append(f"- **化学命名/分子式**：`{f['chemical_name'] or 'N/A'}` | `{f['chemical_formula'] or 'N/A'}` | CAS: `{f['cas_number'] or 'N/A'}`")
                md.append(f"- **纺丝成型技术**：{f['spinning_method'] or '未明确'}")
                md.append("\n**物理力学与热学典型常数指标**：\n")
                md.append("| 物理量指标 | 基准参考值 | 物理量指标 | 基准参考值 |")
                md.append("| :--- | :--- | :--- | :--- |")
                
                density = f"{f['density_g_cm3']} g/cm³" if f['density_g_cm3'] is not None else "N/A"
                strength = f"{f['tensile_strength_gpa']} GPa ({f['tensile_strength_cn_dtex']} cN/dtex)" if f['tensile_strength_gpa'] is not None else "N/A"
                modulus = f"{f['tensile_modulus_gpa']} GPa" if f['tensile_modulus_gpa'] is not None else "N/A"
                elong = f"{f['elongation_at_break_pct']} %" if f['elongation_at_break_pct'] is not None else "N/A"
                regain = f"{f['moisture_regain_pct']} %" if f['moisture_regain_pct'] is not None else "N/A"
                loi = f"{f['loi_pct']} %" if f['loi_pct'] is not None else "N/A"
                melt = f"{f['melting_point_c']} ℃" if f['melting_point_c'] is not None else "不熔/热解"
                service = f"{f['max_service_temp_c']} ℃" if f['max_service_temp_c'] is not None else "常温"

                md.append(f"| **密度 (Density)** | {density} | **断裂拉伸强度 (Strength)** | {strength} |")
                md.append(f"| **拉伸模量 (Modulus)** | {modulus} | **断裂伸长率 (Elongation)** | {elong} |")
                md.append(f"| **公定回潮率 (Moisture Regain)** | {regain} | **极限氧指数 (LOI)** | {loi} |")
                md.append(f"| **熔点/转变温度 (Melting Point)** | {melt} | **连续耐服役温度 (Max Temp)** | {service} |")

                md.append(f"\n- **商标与别名索引**：{alias_str}")
                md.append(f"- **代表性品牌**：{f['representative_brands'] or '通用大宗品'}")
                md.append(f"- **典型应用领域**：{f['typical_applications'] or 'N/A'}")
                md.append(f"- **2026年最新技术成熟度与产业进展**：\n  > {f['tech_status_2026'] or '工业规模成熟运行。'}")
                md.append(f"- **标准与技术规范**：{std_str}\n")
                md.append("---\n")

    # 极限榜单
    md.append("<a id=\"extreme-rankings\"></a>\n")
    md.append("## 🏆 人类化学纤维性能极限排行榜 (Top Rankings)\n")
    
    md.append("### 1. 极端抗拉强度之王 (Tensile Strength Top 10)\n")
    md.append("| 排名 | 纤维代码 | 纤维名称 | 拉伸强度 (GPa) | 密度 (g/cm³) | 比强度 (GPa/(g/cm³)) | 关键应用领域 |")
    md.append("| :---: | :--- | :--- | :---: | :---: | :---: | :--- |")
    cur.execute("""
        SELECT code, name_zh, tensile_strength_gpa, density_g_cm3, typical_applications
        FROM fibers 
        WHERE tensile_strength_gpa IS NOT NULL 
        ORDER BY tensile_strength_gpa DESC LIMIT 10
    """)
    rank = 1
    for r in cur.fetchall():
        ratio = round(r["tensile_strength_gpa"] / r["density_g_cm3"], 2) if r["density_g_cm3"] else "N/A"
        app_brief = r["typical_applications"].split("、")[0] if r["typical_applications"] else ""
        md.append(f"| {rank} | `{r['code']}` | **{r['name_zh']}** | `{r['tensile_strength_gpa']}` | `{r['density_g_cm3']}` | `{ratio}` | {app_brief} |")
        rank += 1

    md.append("\n### 2. 极端抗超高温服役之王 (Continuous Thermal Resistance Top 10)\n")
    md.append("| 排名 | 纤维代码 | 纤维名称 | 长期服役极限 (℃) | 熔点/分解点 (℃) | LOI 极限氧指数 (%) | 特征材料属性 |")
    md.append("| :---: | :--- | :--- | :---: | :---: | :---: | :--- |")
    cur.execute("""
        SELECT code, name_zh, max_service_temp_c, melting_point_c, loi_pct
        FROM fibers 
        WHERE max_service_temp_c IS NOT NULL 
        ORDER BY max_service_temp_c DESC LIMIT 10
    """)
    rank = 1
    for r in cur.fetchall():
        melt = f"{r['melting_point_c']} ℃" if r["melting_point_c"] else "不熔/高温热解"
        loi = f"{r['loi_pct']} %" if r["loi_pct"] else "N/A"
        md.append(f"| {rank} | `{r['code']}` | **{r['name_zh']}** | `{r['max_service_temp_c']} ℃` | {melt} | {loi} | 极端热障材料 |")
        rank += 1

    md.append("\n<a id=\"query-guide\"></a>\n")
    md.append("## 🔍 多维检索与索引调用指南 (Query Guide)\n")
    md.append("本数据库随附原生命令行检索工具 `fiber_query.py`，支持多条件即时检索：\n")
    md.append("```bash")
    md.append("# 1. 全文关键词智能检索 (支持搜索别名、中英文名称、应用场景、商标)")
    md.append("python3 fiber_query.py search 凯夫拉")
    md.append("python3 fiber_query.py search 航天防热")
    md.append("python3 fiber_query.py search 导电")
    md.append("")
    md.append("# 2. 查询指定纤维的完整技术白皮书卡片")
    md.append("python3 fiber_query.py get PPTA")
    md.append("python3 fiber_query.py get PBO")
    md.append("")
    md.append("# 3. 高级性能指标过滤 (例如: 强度>=3.0 GPa 且耐温>=300℃ 的战略特种纤维)")
    md.append("python3 fiber_query.py filter --high-perf --min-strength 3.0 --min-temp 300")
    md.append("")
    md.append("# 4. 筛选生物基且可降解绿色环保纤维")
    md.append("python3 fiber_query.py filter --bio-based --biodegradable")
    md.append("")
    md.append("# 5. 查看全景统计仪表盘")
    md.append("python3 fiber_query.py stats")
    md.append("```\n")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"Encyclopedia generated successfully: {OUTPUT_MD}")
    conn.close()

if __name__ == "__main__":
    generate_markdown()
