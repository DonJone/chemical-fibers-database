-- ====================================================================
-- 现代纺织化学纤维全景数据库与纺织工程知识库 (Textile Chemical Fibers Database)
-- 涵盖人类截至2026年的全部化学纤维体系，以纺织服装、家纺与产业用纺织品为核心重点
-- ====================================================================

DROP TABLE IF EXISTS fibers_fts;
DROP TABLE IF EXISTS textile_blends_matrix;
DROP TABLE IF EXISTS textile_profiles;
DROP TABLE IF EXISTS fiber_standards;
DROP TABLE IF EXISTS fiber_aliases;
DROP TABLE IF EXISTS fibers;
DROP TABLE IF EXISTS categories;

-- 1. 分类体系表 (支持两级树形结构)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name_zh VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT
);

-- 2. 化学纤维核心实体表 (物理、化学与基础属性)
CREATE TABLE fibers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    code VARCHAR(30) UNIQUE NOT NULL,             -- 常用代号/简写 (如 PET, PA66, CV, COOLMAX, PPTA)
    name_zh VARCHAR(100) NOT NULL,                -- 中文通用名称 (如 聚对苯二甲酸乙二醇酯纤维/涤纶)
    name_en VARCHAR(100) NOT NULL,                -- 英文名称 (如 Polyethylene Terephthalate Fiber / Polyester)
    chemical_name VARCHAR(150),                   -- 规范化学名
    chemical_formula VARCHAR(150),                -- 分子式 / 重复单元式
    cas_number VARCHAR(50),                       -- CAS登记号
    generation VARCHAR(50),                       -- 纤维代际 (第1代传统通用, 第2代差别化功能, 第3代高性能特种, 第4代前沿智能绿色)
    discovery_year VARCHAR(30),                   -- 实验室合成/发明年代
    commercial_year VARCHAR(30),                  -- 首次工业化商业应用年代
    pioneering_entity VARCHAR(150),               -- 原创发明人或首发企业机构
    spinning_method TEXT,                         -- 主要纺丝与成型工艺 (熔融/湿法/干法/凝胶/静电/液晶相/双组分复合等)
    
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
    
    -- 纺织产业终端与属性标签
    textile_domain VARCHAR(50) DEFAULT '服装用纺织品', -- 服装用纺织品 (Apparel), 家用纺织品 (Home), 产业用纺织品 (Technical), 综合全领域 (Universal)
    typical_applications TEXT,                    -- 典型工业/民用/尖端国防应用
    representative_brands TEXT,                   -- 代表性历史与现存商业品牌
    tech_status_2026 TEXT,                        -- 截至2026年最新产业化水平与前沿进展
    is_bio_based BOOLEAN DEFAULT 0,               -- 是否生物基原料来源
    is_biodegradable BOOLEAN DEFAULT 0,           -- 是否具有环境生物降解性
    is_high_performance BOOLEAN DEFAULT 0         -- 是否属于战略级高性能/特种纤维
);

-- 3. 纺织工程与面料深度知识表 (Textile Engineering Profile)
CREATE TABLE textile_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiber_id INTEGER NOT NULL REFERENCES fibers(id) ON DELETE CASCADE,
    cross_section_shape VARCHAR(100),              -- 截面微观形态 (圆形, 十字形吸湿排汗, 中空蓄热, 三叶形光泽, 海岛超细, 橘瓣裂片型, C型等)
    fineness_dtex_range VARCHAR(100),              -- 纺织细度范围 (如 0.05-0.3 dtex 超细旦, 1.0-3.3 dtex 常规民用, 5.0-20.0 dtex 工业丝)
    yarn_processing_types TEXT,                    -- 纱线加工规格 (POY, DTY低弹丝, FDY全牵伸丝, ATY空变丝, 短纤Staple, 膨体纱, 帘子线)
    hand_feel_drape TEXT,                          -- 触感悬垂风格 (如 "爽滑飘逸仿真丝", "蓬松软糯羊绒手感", "干爽棉麻质感", "亲肤细腻高弹贴身")
    dyeing_characteristics TEXT,                   -- 染色工艺与适用染料 (分散染料高温高压 130℃ / 阳离子常压染 / 活性染料 / 酸性染料 / 原液着色免染)
    colorfastness_rating VARCHAR(100),             -- 耐洗与耐日晒色牢度等级 (如 "耐水洗4-5级, 日晒4-5级")
    moisture_thermal_comfort TEXT,                 -- 热湿舒适性能 (吸湿排汗毛细效应 / 中空静止空气蓄热 / 高回潮亲肤透气 / 高导热接触凉感)
    pilling_abrasion_grade VARCHAR(100),           -- 抗起毛起球与耐磨性评级 (如 "4-5级抗起球", "高耐磨马丁代尔>50000次")
    elastic_recovery_feature TEXT,                 -- 弹性与保形抗皱特性 (急弹性恢复率, 沸水收缩率, 随身自如回弹, 抗皱免烫)
    recommended_blends TEXT,                       -- 黄金混纺配伍与协同效应 (如 "涤棉65/35挺括耐磨透气", "莫代尔棉50/50垂顺细腻", "羊毛/腈纶70/30抗缩绒蓬松")
    weaving_knitting_suitability TEXT,             -- 适用织造工艺 (圆机针织, 经编, 喷水/喷气织机机织, 水刺无纺布, 熔喷驻极, 针刺造纸毯)
    care_and_washing TEXT,                         -- 洗涤保养与熨烫要点 (最高洗涤水温, 熨烫耐受温度, 防缩水注意事项, 能否氯漂)
    eco_certifications TEXT                        -- 国际生态纺织认证 (OEKO-TEX 100 Class I 婴童级, GRS全球回收标准, Bluesign, ZDHC, 碳足迹)
);

-- 4. 纺织经典混纺配伍矩阵表 (Classic Blends Matrix)
CREATE TABLE textile_blends_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blend_name VARCHAR(100) NOT NULL,              -- 混纺组合名称 (如 "涤棉混纺 (T/C & CVC)")
    fiber_components VARCHAR(150) NOT NULL,        -- 混纺纤维构成 (如 "PET聚酯纤维 + 天然棉纤维")
    classic_ratio VARCHAR(100) NOT NULL,           -- 经典配比 (如 "T/C 65/35 或 CVC 60/40")
    synergy_advantages TEXT NOT NULL,              -- 协同互补优势 (如 "发挥涤纶高强耐磨与挺括免烫，融合棉纤维吸湿透气与抗静电舒适手感")
    typical_fabrics TEXT NOT NULL,                 -- 典型面料与服饰终端 (如 "高档衬衫面料、医护工作服、军训作训服、耐洗工装")
    dyeing_finishing_notes TEXT                    -- 染整加工核心难点与工艺策略 (如 "分散/活性染料一浴两步法或两浴法染色，控制热定型温度180-190℃")
);

-- 5. 别名与商标对照表 (多维度反查与智能检索)
CREATE TABLE fiber_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiber_id INTEGER NOT NULL REFERENCES fibers(id) ON DELETE CASCADE,
    alias VARCHAR(100) NOT NULL,
    alias_type VARCHAR(50) NOT NULL               -- trade_name(商标), abbreviation(缩写), colloquial(俗称), iso_code(国际代码)
);

-- 6. 关联标准化规范表 (GB/T, FZ/T, ISO, ASTM 等)
CREATE TABLE fiber_standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiber_id INTEGER NOT NULL REFERENCES fibers(id) ON DELETE CASCADE,
    standard_org VARCHAR(50) NOT NULL,            -- ISO, GB, FZ(纺织行标), ASTM, AATCC, DIN 等
    standard_code VARCHAR(100) NOT NULL,          -- 标准编号 (如 FZ/T 52010, GB/T 4146)
    standard_title TEXT                           -- 标准全称
);

-- 7. 建立高性能 B-Tree 索引
CREATE INDEX idx_fibers_code ON fibers(code);
CREATE INDEX idx_fibers_category ON fibers(category_id);
CREATE INDEX idx_fibers_textile_domain ON fibers(textile_domain);
CREATE INDEX idx_fibers_density ON fibers(density_g_cm3);
CREATE INDEX idx_fibers_strength_cn ON fibers(tensile_strength_cn_dtex);
CREATE INDEX idx_fibers_strength_gpa ON fibers(tensile_strength_gpa);
CREATE INDEX idx_fibers_modulus ON fibers(tensile_modulus_gpa);
CREATE INDEX idx_fibers_regain ON fibers(moisture_regain_pct);
CREATE INDEX idx_fibers_loi ON fibers(loi_pct);
CREATE INDEX idx_fibers_temp ON fibers(max_service_temp_c);
CREATE INDEX idx_fibers_tags ON fibers(is_bio_based, is_biodegradable, is_high_performance);

CREATE INDEX idx_textile_fiber_id ON textile_profiles(fiber_id);
CREATE INDEX idx_textile_cross_section ON textile_profiles(cross_section_shape);
CREATE INDEX idx_blends_name ON textile_blends_matrix(blend_name);
CREATE INDEX idx_aliases_lookup ON fiber_aliases(alias);

-- 8. 全文检索引擎 FTS5 (支持中英文、品牌与纺织特性微片段全文倒排检索)
CREATE VIRTUAL TABLE fibers_fts USING fts5(
    code,
    name_zh,
    name_en,
    chemical_name,
    spinning_method,
    typical_applications,
    representative_brands,
    tech_status_2026,
    textile_domain,
    cross_section_shape,
    hand_feel_drape,
    dyeing_characteristics,
    moisture_thermal_comfort,
    recommended_blends,
    eco_certifications,
    tokenize="trigram"
);