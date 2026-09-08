# -*- coding: utf-8 -*-
"""
Generator for chemical_fibers_encyclopedia.md
现代纺织化学纤维全景大百科与纺织工程知识库全集 (截至2026年)
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

    cur.execute("SELECT COUNT(*) FROM textile_blends_matrix")
    total_blends = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NULL")
    top_cat_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NOT NULL")
    sub_cat_count = cur.fetchone()[0]

    md = []
    md.append("# 现代纺织化学纤维全景大百科与纺织工程知识库全集 (截至2026年)\n")
    md.append("> **权威定位与全景视野**：本项目以**纺织服装（Apparel）、家用纺织品（Home Textiles）与产业用纺织品（Technical Textiles）三大现代纺织支柱为第一核心重点**，系统汇总人类工业革命至今（截至2026年）已商业化量产与处于前沿尖端阶段的全部化学纤维大系。\n")
    md.append(f"- **收录全系化学纤维品种**：`{total_fibers}` 种化学纤维大类、差别化亚型与功能品类")
    md.append(f"- **纺织经典混纺协同方案**：`{total_blends}` 套黄金混纺配比与染整指南")
    md.append(f"- **分类学层级架构**：`{top_cat_count}` 个一级顶级门类，`{sub_cat_count}` 个专业细分子类")
    md.append("- **底层存储与索引引擎**：SQLite3 + B-Tree 复合索引 + FTS5 全文倒排检索引擎 + JSON/CSV 跨平台全量交付\n")
    md.append("---\n")

    # ==================== 专题篇章 ====================
    md.append("## 📚 现代纺织工程与纤维学总论 (Textile Engineering Monograph)\n")
    
    # 专题一
    md.append("### 专题一：现代纺织三大终端应用领域全景体系\n")
    md.append("现代纺织工程将化学纤维的应用划分为三大支柱门类，各类纤维根据其微观聚集态结构与物理化学特性精准匹配不同使用场景：\n")
    md.append("| 纺织门类 | 核心需求指标 | 主力纤维品种 | 典型终端制品 |")
    md.append("| :--- | :--- | :--- | :--- |")
    md.append("| **服装用纺织品 (Apparel)** | 贴肤亲肤性、吸湿透湿、触感软糯/滑爽、悬垂抗皱、高弹活动自如、轻盈保暖、抗起球 | 莫代尔(CMD)、天丝(CLY)、粘胶(CV)、超细锦纶(MICRO-PA)、吸湿排汗涤纶(COOLMAX)、高膨体腈纶(BULK-PAN)、氨纶(EL)、T400自卷曲纤维 | 高级内衣、无痕内衣、防晒衣、速干运动服、羊绒感毛衣、瑜伽服、商务免烫衬衫、弹力牛仔裤 |")
    md.append("| **家用纺织品 (Home Textiles)** | 蓬松保暖、亲肤透气、耐洗耐磨、抗起球、色牢度高、抗菌防螨、阻燃防火 | 中空保暖涤纶(THERMOLITE)、天丝LF、竹浆纤维(BAMBOO)、大豆蛋白纤维(SPF)、永久阻燃涤纶(FR-PET)、超细开纤微纤(SPLIT-PET-PA) | 羽绒棉被芯、丝滑高密四件套、抗菌毛巾浴巾、酒店阻燃遮光窗帘、沙发沙发布艺、超细纤维干发巾 |")
    md.append("| **产业用纺织品 (Technical / Industrial)** | 超高断裂强力、高初始模量、耐超高温、极端耐化学腐蚀、高过滤拦截效率、抗撕裂防爆破 | 芳纶1414/1313、超高分子量聚乙烯(UHMWPE)、熔喷驻极聚丙烯(MB-PP)、高强锦纶66帘子线(CORD-PA66)、聚苯硫醚(PPS)、PTFE氟纶、碳纤维、连续陶瓷纤维 | 医用N95口罩滤材、汽车安全气囊、子午线轮胎帘子布、高温烟气除尘滤袋、军警防弹衣/防刺服、石化防电弧工装、风电复合材料 |")
    md.append("\n---\n")

    # 专题二
    md.append("### 专题二：现代纺织经典混纺配伍与协同效应矩阵 (12大黄金搭档)\n")
    md.append("单一纤维往往具有性能局限，现代面料工程通过多组分短纤混纺或长丝交织，实现优势互补、扬长避短：\n")
    cur.execute("SELECT * FROM textile_blends_matrix ORDER BY id")
    blends = cur.fetchall()
    for b in blends:
        md.append(f"#### 🎯 [{b['id']}] {b['blend_name']}\n")
        md.append(f"- **纤维组分构成**：{b['fiber_components']}")
        md.append(f"- **经典黄金配比**：`{b['classic_ratio']}`")
        md.append(f"- **协同互补优势**：{b['synergy_advantages']}")
        md.append(f"- **典型面料服饰**：{b['typical_fabrics']}")
        md.append(f"- **染整关键与工艺注意事项**：\n  > {b['dyeing_finishing_notes']}\n")
    md.append("---\n")

    # 专题三
    md.append("### 专题三：纺织微观截面工程与热湿舒适性机制\n")
    md.append("纤维的横截面微观形态对织物的导湿、保暖、光泽与手感起着决定性作用：\n")
    md.append("| 截面形态类别 | 代表纤维品种 | 几何微观结构 | 核心物理机制与服用功效 |")
    md.append("| :---: | :--- | :--- | :--- |")
    md.append("| **十字形 / 四槽形** | COOLMAX, 导湿涤纶 | 十字辐射微槽 | 表面微凹槽形成强大毛细管虹吸压力，导湿蒸发速度为纯棉的 2-3 倍，运动体表持久干爽 |")
    md.append("| **中空孔 / 多孔中空** | THERMOLITE, 中空棉 | 纤维内部连续单孔/四孔/七孔 (中空率20-40%) | 封闭微细静止空气层，绝热阻抗极高(克罗值CLO达1.5-2.5)，潮湿环境下不丧失保暖性 |")
    md.append("| **海岛型超微细** | SEA-ISLAND, 超纤微纤 | 几十至数百根超微细聚酯岛包覆于水溶海组分中 | 溶出海组分后单丝细度达 0.001-0.05 dtex，极度比表面积带来超越小羊皮的麂皮绒手感 |")
    md.append("| **橘瓣裂片型** | SPLIT-PET-PA, 涤锦微纤 | 8-16瓣交替辐射橘瓣相间复合截面 | 高压水刺或化学开纤裂解成楔形刀锋微丝，产生强大静电与毛细吸附，吸水达自重7倍 |")
    md.append("| **并列双组分自卷曲** | T400, PTT/PET 并列复合 | PTT与PET双组分并列偏心熔融复合 | 利用两组分热收缩率差异自发产生永久立体螺旋卷曲弹簧，耐氯漂暴晒，抗皱保形 |")
    md.append("| **哑铃形 / 狗骨形** | BULK-PAN (德绒), 醋酸CA | 中间凹陷、两端粗圆扁平状 | 纤维之间产生大量微小空气囊，手感蓬松软糯如克什米尔羊绒，保暖率比羊毛高15% |")
    md.append("| **平滑高取向超导热** | UHMWPE-COOL, 冰晶丝 | 分子链高度伸直高结晶规整圆形 | 轴向导热系数高达 20 W/(m·K)，接触瞬间凉感系数 q_max > 0.35 J/(cm²·s)，体感瞬降 2-3℃ |")
    md.append("\n---\n")

    # 专题四
    md.append("### 专题四：国际生态纺织品标准与绿色认证体系\n")
    md.append("现代纺织工业已进入全面绿色、低碳、可追溯的新纪元：\n")
    md.append("- **OEKO-TEX® Standard 100**：全球最权威的纺织品生态安全认证，涵盖300多项有害化学物质检测。分为 Product Class I（婴幼儿级，最严格要求）、Class II（直接接触皮肤级）、Class III（非直接接触皮肤级）、Class IV（装饰家纺级）。")
    md.append("- **GRS (Global Recycled Standard 全球回收标准)**：针对废旧塑料瓶（rPET）或废旧纺织品循环再生的国际自愿性全链条认证，强制要求全生命周期可追溯原料来源（TC交易证书）及环境社会责任。")
    md.append("- **Bluesign® 标准**：从纺织产业链源头（化学品管理）把控安全，消除对人类和环境存在风险的危险物质。")
    md.append("- **ZDHC (有害化学物质零排放)**：推进纺织印染供应链无害化化学品替代与污水洁净排放。")
    md.append("- **碳足迹核查 (ISO 14067)**：全生命周期量化纤维自单体制备、聚合、纺丝到织造染整的温室气体排放。\n")
    md.append("---\n")

    # 目录导航
    md.append("## 目录导航 (Table of Contents)\n")
    cur.execute("SELECT id, code, name_zh, name_en FROM categories WHERE parent_id IS NULL ORDER BY id")
    top_cats = cur.fetchall()
    for tc in top_cats:
        anchor = tc['code'].lower().replace('_', '-')
        md.append(f"- [{tc['name_zh']} ({tc['name_en']})](#{anchor})")
        cur.execute("SELECT id, code, name_zh, name_en FROM categories WHERE parent_id = ? ORDER BY id", (tc["id"],))
        sub_cats = cur.fetchall()
        for sc in sub_cats:
            sub_anchor = sc['code'].lower().replace('_', '-')
            md.append(f"  - [{sc['name_zh']} ({sc['code']})](#{sub_anchor})")
    md.append("- [现代纺织纤维性能极值与舒适度排行榜 (Top Rankings)](#extreme-rankings)")
    md.append("- [多维检索与命令行调用指南 (Query Guide)](#query-guide)\n")
    md.append("---\n")

    # 分大类输出条目
    for tc in top_cats:
        tc_anchor = tc['code'].lower().replace('_', '-')
        md.append(f"<a id=\"{tc_anchor}\"></a>\n")
        md.append(f"## 🏛️ {tc['name_zh']} ({tc['name_en']})\n")
        
        cur.execute("SELECT id, code, name_zh, name_en, description FROM categories WHERE parent_id = ? ORDER BY id", (tc["id"],))
        sub_cats = cur.fetchall()

        for sc in sub_cats:
            sc_anchor = sc['code'].lower().replace('_', '-')
            md.append(f"<a id=\"{sc_anchor}\"></a>\n")
            md.append(f"### 📂 {sc['name_zh']} ({sc['code']})\n")
            if sc["description"]:
                md.append(f"> *子类释义与纺织工程定位*：{sc['description']}\n")

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

                # Textile Profile
                cur.execute("SELECT * FROM textile_profiles WHERE fiber_id = ?", (fid,))
                tp = cur.fetchone()

                # Tags
                tags = [f"🏷️ 纺织门类: `{f['textile_domain'] or '综合纺织品'}`"]
                if f["is_bio_based"]:
                    tags.append("🌱 生物基 (Bio-based)")
                if f["is_biodegradable"]:
                    tags.append("♻️ 生物降解 (Biodegradable)")
                if f["is_high_performance"]:
                    tags.append("🛡️ 战略特种高性能 (High-Performance)")
                tag_str = " | ".join(tags)

                md.append(f"#### 🧬 [{f['code']}] {f['name_zh']} ({f['name_en']})\n")
                md.append(f"- **特征标签**：{tag_str}")
                md.append(f"- **工业历史**：{f['generation']} | 发明年代: `{f['discovery_year'] or '未知'}` | 商业化年代: `{f['commercial_year'] or '未知'}` | 先驱研发: `{f['pioneering_entity'] or '未记载'}`")
                md.append(f"- **化学命名与分子式**：`{f['chemical_name'] or 'N/A'}` | `{f['chemical_formula'] or 'N/A'}` | CAS号: `{f['cas_number'] or 'N/A'}`")
                md.append(f"- **成型纺丝技术**：{f['spinning_method'] or '未明确'}")
                
                # Table 1: 物化力学热学指标
                md.append("\n**物理力学与热学基准常数**：\n")
                md.append("| 物理量指标 | 基准参考值 | 物理量指标 | 基准参考值 |")
                md.append("| :--- | :--- | :--- | :--- |")
                density = f"{f['density_g_cm3']} g/cm³" if f['density_g_cm3'] is not None else "N/A"
                strength = f"{f['tensile_strength_gpa']} GPa ({f['tensile_strength_cn_dtex']} cN/dtex)" if f['tensile_strength_gpa'] is not None else "N/A"
                modulus = f"{f['tensile_modulus_gpa']} GPa" if f['tensile_modulus_gpa'] is not None else "N/A"
                elong = f"{f['elongation_at_break_pct']} %" if f['elongation_at_break_pct'] is not None else "N/A"
                regain = f"**{f['moisture_regain_pct']} %** (亲水舒适性)" if f['moisture_regain_pct'] is not None else "N/A"
                loi = f"**{f['loi_pct']} %** (阻燃极限)" if f['loi_pct'] is not None else "N/A"
                melt = f"{f['melting_point_c']} ℃" if f['melting_point_c'] is not None else "不熔/高温热解"
                service = f"{f['max_service_temp_c']} ℃" if f['max_service_temp_c'] is not None else "常温"

                md.append(f"| **密度 (Density)** | {density} | **断裂拉伸强度 (Strength)** | {strength} |")
                md.append(f"| **拉伸模量 (Modulus)** | {modulus} | **断裂伸长率 (Elongation)** | {elong} |")
                md.append(f"| **公定回潮率 (Moisture Regain)** | {regain} | **极限氧指数 (LOI)** | {loi} |")
                md.append(f"| **熔点/转变温度 (Melting Point)** | {melt} | **长期耐热服役温度 (Max Temp)** | {service} |")

                # Table 2: 纺织工程与面料深度知识卡
                if tp:
                    md.append("\n**🧵 纺织工程与面料应用深度档案**：\n")
                    md.append(f"- **微观截面形态**：`{tp['cross_section_shape'] or '常规'}`")
                    md.append(f"- **典型细度范围**：{tp['fineness_dtex_range'] or 'N/A'}")
                    md.append(f"- **纱线加工规格**：{tp['yarn_processing_types'] or 'N/A'}")
                    md.append(f"- **手感风格与悬垂触感**：\033[33m{tp['hand_feel_drape'] or 'N/A'}\033[0m")
                    md.append(f"- **染色特性与适用染料**：{tp['dyeing_characteristics'] or 'N/A'}")
                    md.append(f"- **色牢度表现**：`{tp['colorfastness_rating'] or '耐洗4级'}`")
                    md.append(f"- **热湿舒适机制**：{tp['moisture_thermal_comfort'] or 'N/A'}")
                    md.append(f"- **抗起球与耐磨评级**：`{tp['pilling_abrasion_grade'] or 'N/A'}`")
                    md.append(f"- **弹性与抗皱保形**：{tp['elastic_recovery_feature'] or 'N/A'}")
                    md.append(f"- **黄金混纺配伍方案**：\n  > 💡 **{tp['recommended_blends'] or '支持通用混纺'}**")
                    md.append(f"- **适用织造与成型工艺**：{tp['weaving_knitting_suitability'] or 'N/A'}")
                    md.append(f"- **洗涤保养与熨烫要点**：{tp['care_and_washing'] or 'N/A'}")
                    md.append(f"- **生态环保认证**：`{tp['eco_certifications'] or '符合通用行业规范'}`")

                md.append(f"\n- **商标与别名反查索引**：{alias_str}")
                md.append(f"- **代表性商业品牌**：{f['representative_brands'] or '通用大宗品'}")
                md.append(f"- **典型应用终端**：{f['typical_applications'] or 'N/A'}")
                md.append(f"- **2026年技术产业成熟度与前沿进展**：\n  > {f['tech_status_2026'] or '成熟量产运行。'}")
                md.append(f"- **标准与技术规范**：{std_str}\n")
                md.append("---\n")

    # ==================== 极限排行榜 ====================
    md.append("<a id=\"extreme-rankings\"></a>\n")
    md.append("## 🏆 现代纺织纤维性能极值与舒适度排行榜 (Top Rankings)\n")
    
    # 榜单 1: 回潮率亲肤舒适王
    md.append("### 1. 吸湿透气与服用亲肤舒适之王 (公定回潮率 Top 10)\n")
    md.append("| 排名 | 纤维代号 | 纤维中文名称 | 公定回潮率 (%) | 纺织应用门类 | 舒适感官特征与核心优势 |")
    md.append("| :---: | :--- | :--- | :---: | :--- | :--- |")
    cur.execute("""
        SELECT code, name_zh, moisture_regain_pct, textile_domain, typical_applications
        FROM fibers 
        WHERE moisture_regain_pct IS NOT NULL 
        ORDER BY moisture_regain_pct DESC LIMIT 10
    """)
    rank = 1
    for r in cur.fetchall():
        app_brief = r["typical_applications"].split("、")[0] if r["typical_applications"] else ""
        md.append(f"| {rank} | `{r['code']}` | **{r['name_zh']}** | `{r['moisture_regain_pct']} %` | {r['textile_domain']} | 呼吸吸汗透气、天然亲肤、消除静电积聚 |")
        rank += 1

    # 榜单 2: 极端抗拉强度之王
    md.append("\n### 2. 极端抗拉强度之王 (Tensile Strength Top 10)\n")
    md.append("| 排名 | 纤维代号 | 纤维中文名称 | 拉伸强度 (GPa) | 密度 (g/cm³) | 比强度 (GPa/(g/cm³)) | 关键应用场景 |")
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

    # 榜单 3: 极端抗超高温服役之王
    md.append("\n### 3. 极端抗超高温服役之王 (Continuous Thermal Resistance Top 10)\n")
    md.append("| 排名 | 纤维代号 | 纤维中文名称 | 长期服役温度极限 (℃) | 熔点/分解点 (℃) | LOI 极限氧指数 (%) | 特征材料属性 |")
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
        md.append(f"| {rank} | `{r['code']}` | **{r['name_zh']}** | `{r['max_service_temp_c']} ℃` | {melt} | {loi} | 极端工业/航空热障材料 |")
        rank += 1

    # 榜单 4: 阻燃防火极限氧指数 Top 10
    md.append("\n### 4. 极端难燃与阻燃防火之王 (LOI 极限氧指数 Top 10)\n")
    md.append("| 排名 | 纤维代号 | 纤维中文名称 | 极限氧指数 LOI (%) | 耐热极限 (℃) | 燃烧行为特征 | 关键应用领域 |")
    md.append("| :---: | :--- | :--- | :---: | :---: | :--- | :--- |")
    cur.execute("""
        SELECT code, name_zh, loi_pct, max_service_temp_c, typical_applications
        FROM fibers 
        WHERE loi_pct IS NOT NULL 
        ORDER BY loi_pct DESC LIMIT 10
    """)
    rank = 1
    for r in cur.fetchall():
        temp = f"{r['max_service_temp_c']} ℃" if r["max_service_temp_c"] else "N/A"
        app_brief = r["typical_applications"].split("、")[0] if r["typical_applications"] else ""
        md.append(f"| {rank} | `{r['code']}` | **{r['name_zh']}** | `{r['loi_pct']} %` | {temp} | 离火自熄、不延燃、无熔滴灼伤 | {app_brief} |")
        rank += 1

    # ==================== CLI 调用指南 ====================
    md.append("\n<a id=\"query-guide\"></a>\n")
    md.append("## 🔍 智能检索与命令行调用指南 (Query Guide)\n")
    md.append("本知识库附带原生终端命令行工具 [`fiber_query.py`](file:///Users/don/Documents/化学纤维研究/fiber_query.py)，支持多维纺织条件即时查询：\n")
    md.append("```bash")
    md.append("# 1. 纺织与化纤关键词全文模糊检索 (支持搜索纤维名称、截面、染料、手感、混纺等)")
    md.append("python3 fiber_query.py search 吸湿排汗")
    md.append("python3 fiber_query.py search 凉感")
    md.append("python3 fiber_query.py search 莫代尔")
    md.append("python3 fiber_query.py search 分散染料")
    md.append("python3 fiber_query.py search 德绒")
    md.append("python3 fiber_query.py search 麂皮绒")
    md.append("")
    md.append("# 2. 查询指定纤维的完整物理化学与纺织工程技术卡片")
    md.append("python3 fiber_query.py get COOLMAX")
    md.append("python3 fiber_query.py get T400")
    md.append("python3 fiber_query.py get MICRO-CMD")
    md.append("python3 fiber_query.py get 凯夫拉")
    md.append("")
    md.append("# 3. 专项查看纤维的纺织工程面料应用技术卡")
    md.append("python3 fiber_query.py textile COOLMAX")
    md.append("python3 fiber_query.py textile SEA-ISLAND")
    md.append("")
    md.append("# 4. 查询经典混纺配伍方案矩阵 (12大黄金配比)")
    md.append("python3 fiber_query.py blend 涤棉")
    md.append("python3 fiber_query.py blend 羊毛")
    md.append("python3 fiber_query.py blend 阻燃")
    md.append("python3 fiber_query.py blend           # 查看全部12套经典混纺矩阵")
    md.append("")
    md.append("# 5. 纺织特性多维指标过滤筛选")
    md.append("python3 fiber_query.py filter --wicking                      # 筛选吸湿排汗速干纤维")
    md.append("python3 fiber_query.py filter --high-regain                  # 筛选高回潮率舒适纤维 (回潮率>=8%)")
    md.append("python3 fiber_query.py filter --flame-retardant              # 筛选阻燃防火纤维 (LOI>=28%)")
    md.append("python3 fiber_query.py filter --eco                          # 筛选绿色环保生态认证纤维")
    md.append("python3 fiber_query.py filter --domain 服装 --cross-section 十字  # 筛选服装用十字异形导湿纤维")
    md.append("")
    md.append("# 6. 查看全景统计仪表盘")
    md.append("python3 fiber_query.py stats")
    md.append("```\n")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"Textile Encyclopedia generated successfully: {OUTPUT_MD}")
    conn.close()

if __name__ == "__main__":
    generate_markdown()
