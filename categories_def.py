# -*- coding: utf-8 -*-
"""
Full Database Builder for Chemical Fibers (人类化学纤维全景数据库 - 截至2026年)
"""
import sqlite3
import json
import csv
import os

DB_NAME = "chemical_fibers.db"
JSON_NAME = "chemical_fibers_dataset.json"
CSV_NAME = "chemical_fibers_catalog.csv"

# 1. Categories Data
CATEGORIES = [
    # Top-level categories
    (1, "REG", "再生纤维与人造天然聚合物纤维", "Regenerated & Natural Polymer Fibers", None, "以天然多糖、天然蛋白质等天然高分子为原料，经化学溶解、衍生化或塑化后纺丝再生的纤维"),
    (2, "SYN_CONV", "常规与差别化通用合成纤维", "Conventional & Differentiated Synthetic Fibers", None, "以石油化工或煤化工等单体经聚合反应制备的高分子合成纤维，涵盖民用与工业通用大品种"),
    (3, "BIO_DEGR", "生物基与生物可降解聚合物纤维", "Bio-based & Biodegradable Synthetic Fibers", None, "利用可再生生物质制备单体或在自然环境中可降解的环保型合成纤维"),
    (4, "HIGH_PERF", "高性能与特种工程有机纤维", "High-Performance & Specialty Synthetic Fibers", None, "具备超高强高模、耐超高温、极端耐化学腐蚀等特征的战略级有机聚合物特种纤维"),
    (5, "CARBON", "碳纤维及先进碳基纤维", "Carbon & Advanced Carbon-based Fibers", None, "由前驱体经高温热解碳化形成的碳纤维，以及基于低维碳材料（碳管、石墨烯）制备的连续宏观纤维"),
    (6, "INORGANIC", "无机非金属与金属化学纤维", "Inorganic & Metallic Chemical Fibers", None, "以无机矿物氧化物、碳化物、氮化物或金属为原料，经熔体牵引、化学气相沉积或前驱体转化制成的纤维"),
    (7, "EMERGING", "前沿智能、仿生与生物工程化学纤维", "Emerging Smart, Biomimetic & Bioengineered Fibers (2026)", None, "融合合成生物学、柔性电子、微纳结构仿生与能源捕获的前沿下一代智能纤维体系"),

    # Sub-categories for REG
    (101, "REG_CELL", "再生纤维素纤维", "Regenerated Cellulose Fibers", 1, "包括传统粘胶法、铜氨法、环保NMMO溶剂法(莱赛尔)、离子液体法及醋酸纤维素"),
    (102, "REG_PROT", "再生蛋白质纤维", "Regenerated Protein Fibers", 1, "包括酪蛋白(牛奶)、大豆蛋白复合、再生蚕丝蛋白、玉米醇溶蛋白等"),
    (103, "REG_POLY", "其他多糖与天然聚合物基纤维", "Other Polysaccharide & Natural Polymer Fibers", 1, "海藻酸钠纤维、甲壳素/壳聚糖纤维、玻尿酸复合纤维、天然胶乳弹性纤维等"),
    (104, "REG_DIFF_CELL", "差别化与功能性再生纤维素纺织纤维", "Differentiated Regenerated Cellulose Textile Fibers", 1, "永久阻燃粘胶(Lenzing FR)、超细旦莫代尔(MicroModal)、低原纤化天丝(Lyocell LF/A100)及水刺无纺高纯短纤"),

    # Sub-categories for SYN_CONV
    (201, "SYN_PET", "聚酯系纤维", "Polyester Fibers", 2, "PET、PTT、PBT、PEN、阳离子可染聚酯CDP/ECDP及低熔点共聚酯"),
    (202, "SYN_PA", "脂肪族与半芳香族聚酰胺纤维", "Polyamide (Nylon) Fibers", 2, "PA6、PA66、PA610、PA11、PA12、PA46、PA56、长碳链尼龙及耐热半芳香PA"),
    (203, "SYN_PAN", "聚丙烯腈系纤维 (腈纶)", "Polyacrylonitrile (Acrylic) Fibers", 2, "标准三元共聚腈纶、改性腈纶(变性腈纶/阻燃腈纶Modacrylic)"),
    (204, "SYN_PO", "聚烯烃系纤维", "Polyolefin Fibers", 2, "聚丙烯纤维(丙纶PP)、普通聚乙烯纤维(乙纶PE)、聚4-甲基-1-戊烯纤维(PMP)"),
    (205, "SYN_PU", "聚氨酯与弹性聚合物纤维", "Polyurethane & Elastic Fibers", 2, "聚氨酯弹性纤维(氨纶Spandex/Elastane)、热塑性聚氨酯(TPU)弹性纤维"),
    (206, "SYN_PVA", "聚乙烯醇系纤维 (维纶)", "Polyvinyl Alcohol Fibers", 2, "聚乙烯醇缩甲醛纤维(维纶)、水溶性PVA纤维、高强高模PVA短纤与长丝"),
    (207, "SYN_HALO", "含卤素通用纤维", "Halogenated Vinyl Fibers", 2, "聚氯乙烯纤维(氯纶PVC)、聚偏二氯乙烯纤维(偏氯纶PVDC)"),
    (208, "SYN_DIFF_PET", "差别化与功能性聚酯纺织纤维", "Differentiated & Functional Polyester Textile Fibers", 2, "吸湿排汗(Coolmax)、中空蓄热保暖(Thermolite)、循环再生rPET、原液着色色丝、永久阻燃聚酯及T400自卷曲双组分高弹聚酯"),
    (209, "SYN_MICRO", "超细旦与双组分复合开纤纺织纤维", "Microfibers & Bi-component Conjugate Textile Fibers", 2, "定岛型海岛超细纤维(超纤皮革/麂皮绒)、橘瓣裂片型涤锦复合开纤超细纤维(高效洁净布)"),

    # Sub-categories for BIO_DEGR
    (301, "BIO_ALIPH", "脂肪族可降解聚酯纤维", "Aliphatic Biodegradable Polyester Fibers", 3, "聚乳酸(PLA)、聚羟基脂肪酸酯(PHA/PHBV/P34HB)、聚己内酯(PCL)、聚乙醇酸(PGA)、PBS/PBAT"),
    (302, "BIO_FDCA", "新型生物基呋喃与芳杂聚酯纤维", "Bio-based Furanic & Co-polyesters", 3, "聚呋喃二甲酸乙二醇酯(PEF)、生物基聚碳酸亚丙酯(PPC)"),

    # Sub-categories for HIGH_PERF
    (401, "HP_ARAMID", "芳香族聚酰胺类纤维 (芳纶家族)", "Aramid Fibers", 4, "对位芳纶(PPTA)、间位芳纶(PMIA)、杂环芳纶(芳纶III)、芳砜纶(PSA)、共聚对位芳纶(Technora)"),
    (402, "HP_UHMWPE", "超高分子量聚乙烯纤维", "Ultra-High Molecular Weight Polyethylene Fibers", 4, "凝胶纺丝-超倍拉伸制备的超高强模UHMWPE纤维"),
    (403, "HP_HETERO", "刚性链杂环与热致液晶聚合物纤维", "Rigid-rod Heterocyclic & Liquid Crystalline Polymer Fibers", 4, "PBO(聚苯并双恶唑)、PBZT(聚苯并双噻唑)、PBI(聚苯并咪唑)、PIPD/M5、TLCP/聚芳酯(Vectran)"),
    (404, "HP_ENG", "特种工程热塑性与耐高温纤维", "High-Performance Engineering Thermoplastic Fibers", 4, "聚苯硫醚(PPS)、聚醚醚酮(PEEK)、聚醚酮酮(PEKK)、聚酰亚胺(PI)、聚酰胺酰亚胺(PAI)"),
    (405, "HP_FLUORO", "含氟特种聚合物纤维", "Fluoropolymer Specialty Fibers", 4, "聚四氟乙烯(PTFE)、聚偏氟乙烯(PVDF)、乙烯-四氟乙烯共聚物(ETFE)"),
    (406, "HP_THERMO", "耐高温交联热固性树脂纤维", "Cross-linked Thermoset Specialty Fibers", 4, "酚醛树脂纤维(Novoloid/Kynol)、三聚氰胺甲醛纤维(Basofil)"),

    # Sub-categories for CARBON
    (501, "CF_PAN", "聚丙烯腈基碳纤维", "PAN-based Carbon Fibers", 5, "高强型(T300/T700/T800/T1000/T1100/T1200)与高模型(M40/M50/M55/M60/M65J)"),
    (502, "CF_PITCH", "沥青基碳纤维", "Pitch-based Carbon Fibers", 5, "各向同性通用级与中间相各向异性超高模量沥青基碳纤维"),
    (503, "CF_RAYON", "纤维素与生物基前驱体碳纤维", "Cellulose & Bio-based Precursor Carbon Fibers", 5, "粘胶基碳纤维(宇航烧蚀防热)、木质素基前驱体碳纤维"),
    (504, "CF_NANO", "先进低维碳连续纤维", "Advanced Low-Dimensional Carbon Fibers", 5, "碳纳米管(CNT)宏观连续纤维、石墨烯(Graphene)宏观长丝"),
    (505, "CF_ACT", "活性碳纤维材料", "Activated Carbon Fibers (ACF)", 5, "具有微孔超大比表面积的活性碳纤维"),

    # Sub-categories for INORGANIC
    (601, "INORG_GLASS", "高性能玻璃纤维系列", "Glass Fiber Series", 6, "无碱E玻纤、高强S/S-2玻纤、耐化学C玻纤、耐碱AR玻纤、高硅氧玻纤、超纯石英纤维、低介电Low-Dk玻纤"),
    (602, "INORG_MINERAL", "天然玄武岩熔融矿物纤维", "Basalt Continuous Fibers", 6, "100%天然玄武岩石料高温熔融直接拉丝绿色纤维"),
    (603, "INORG_CERAMIC", "先进连续陶瓷纤维", "Advanced Continuous Ceramic Fibers", 6, "碳化硅纤维(SiC 1/2/3代)、氧化铝纤维(Alumina)、氮化硅纤维(Si3N4)、莫来石纤维、硼纤维(Boron)"),
    (604, "INORG_METAL", "微细金属与智能液态金属纤维", "Metallic & Liquid Metal Fibers", 6, "不锈钢微丝、铜/银导电微纤、镍铬耐高温发热丝、镓铟液态合金柔性拉伸纤维"),

    # Sub-categories for EMERGING
    (701, "EMG_BIOENG", "合成生物工程与仿生结构蛋白纤维", "Synthetic Biology & Structural Protein Fibers", 7, "重组基因蜘蛛丝纤维(Recombinant Spider Silk)、工程化重组胶原蛋白纤维"),
    (702, "EMG_SMART", "智能响应与自适应调温变色纤维", "Intelligent Responsive & Adaptive Fibers", 7, "微胶囊相变储能纤维、力致变色/温致变色纤维、形状记忆聚合物纤维"),
    (703, "EMG_ENERGY", "纤维状储能、发电与光电探测器件", "Fiber Electronics, Energy Harvesters & Sensors", 7, "纤维锂离子电池、纤维摩擦纳米发电机(TENG)、纤维钙钛矿太阳能电池、发光纤维显示器件"),
    (704, "EMG_AERO", "仿生纳微多孔气凝胶超绝热纤维", "Biomimetic Aerogel Ultra-Insulating Fibers", 7, "仿北极熊毛发中空超绝热气凝胶纤维、凯夫拉气凝胶纤维"),
    (705, "EMG_2D", "二维晶体材料复合功能纤维", "2D Crystal Materials Functional Fibers", 7, "MXene基导电屏蔽纤维、石墨炔微纳光催化纤维"),
    (706, "EMG_TEXTILE_FUNC", "现代健康舒适与防护功能性纺织纤维", "Functional Health, Comfort & Protective Textile Fibers", 7, "石墨烯多功能纺织纤维、纳米银离子长效广谱抗菌纤维、高导热瞬凉UHMWPE纺织纤维、芳纶防电弧热防护纺织特种纱")
]

print(f"Total categories defined: {len(CATEGORIES)}")
