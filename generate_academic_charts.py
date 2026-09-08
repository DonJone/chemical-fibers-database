# -*- coding: utf-8 -*-
"""
Academic Chart Generator for Chemical Fibers & Textile Engineering Monograph
遵照学术图表设计规范与中文字形排版要求：
- 显式注册与配置跨平台 CJK 中文字体 (Ubuntu Linux CI / macOS / Windows)
- 自动化自检机制，杜绝方块字 (Tofu / Missing Glyphs)
- 去除顶部和右侧外边框 (Spines)
- 极简浅灰背景网格
- 严谨学术配色系统 (Oxford Navy, Slate Teal, Amber Crimson, Forest Green)
- 输出高精度 PDF 矢量图至 book/figures/
"""

import os
import glob
import sqlite3
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join("book", "figures")
DB_PATH = "chemical_fibers.db"

# 咨询/学术级品牌主色系
C_NAVY    = "#1A365D"  # 经典牛津藏青 (Oxford Navy)
C_BLUE    = "#2B6CB0"  # 科技蓝 (Tech Blue)
C_TEAL    = "#0D9488"  # 墨水青 (Slate Teal)
C_CRIMSON = "#9B2C2C"  # 砖红/警示 (Crimson Amber)
C_AMBER   = "#D69E2E"  # 琥珀橙 (Amber)
C_GREEN   = "#22543D"  # 常青绿 (Forest Green)
C_GRAY    = "#718096"  # 中性灰 (Slate Gray)
C_LIGHT   = "#F7FAFC"  # 浅灰底色
C_BORDER  = "#E2E8F0"  # 边框线

def init_academic_fonts():
    """
    配置 Matplotlib 中文字体支持，确保在 Ubuntu Linux (CI)、macOS 与 Windows 各环境下
    均能完整渲染汉字（如'连续氧化锆耐火陶瓷纤维'），杜绝字形缺失。
    """
    # 1. 显式添加 Linux, macOS, Windows 常见 CJK 字体物理文件
    candidate_font_paths = [
        # Ubuntu / Debian
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
        '/usr/share/fonts/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        # macOS
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/System/Library/Fonts/Supplemental/Songti.ttc',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
        # Windows
        r'C:\Windows\Fonts\msyh.ttc',
        r'C:\Windows\Fonts\simhei.ttf',
    ]

    # 递归扫描 Linux 系统字体目录 /usr/share/fonts 下所有可能的 CJK 字体
    if os.path.exists('/usr/share/fonts'):
        for fpath in glob.glob('/usr/share/fonts/**/*', recursive=True):
            if fpath.lower().endswith(('.ttc', '.ttf', '.otf')):
                fn = os.path.basename(fpath).lower()
                if any(k in fn for k in ['cjk', 'noto', 'wqy', 'hei', 'song', 'microhei', 'zenhei']):
                    candidate_font_paths.append(fpath)

    for font_path in candidate_font_paths:
        if os.path.isfile(font_path):
            try:
                fm.fontManager.addfont(font_path)
            except Exception:
                pass

    # 2. 候选字体家族优先级列表
    preferred_fonts = [
        'Noto Sans CJK SC',
        'Source Han Sans SC',
        'Source Han Sans CN',
        'WenQuanYi Micro Hei',
        'WenQuanYi Zen Hei',
        'PingFang SC',
        'Hiragino Sans GB',
        'Songti SC',
        'Heiti SC',
        'STHeiti',
        'SimHei',
        'Microsoft YaHei',
        'Arial Unicode MS',
    ]

    available_font_names = {f.name for f in fm.fontManager.ttflist}
    usable_fonts = [name for name in preferred_fonts if name in available_font_names]

    # 将系统中其他注册了的 CJK 字体也追加至备选链
    for f in fm.fontManager.ttflist:
        fn_lower = f.name.lower()
        if any(k in fn_lower for k in ['cjk', 'micro hei', 'zen hei', 'noto sans sc', 'pingfang', 'songti', 'heiti']):
            if f.name not in usable_fonts:
                usable_fonts.append(f.name)

    # 3. 设置 Matplotlib 字体全局参数
    plt.rcParams['font.sans-serif'] = usable_fonts + ['DejaVu Sans', 'sans-serif']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.autolayout'] = True
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42

    print(f"Font initialization completed. Active CJK font candidates: {usable_fonts[:5]}")
    verify_cjk_glyph_rendering()

def verify_cjk_glyph_rendering():
    """
    自检验证中文渲染与关键字符（特别是 '连续氧化锆耐火陶瓷纤维 (ZrO2纤维)'）
    杜绝方块字或字形缺失带入生成的 PDF。
    """
    test_str = "化学纤维研究：连续氧化锆耐火陶瓷纤维 (ZrO2纤维) 2200℃ 极限氧指数 LOI"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fig, ax = plt.subplots(figsize=(3, 1))
        ax.text(0.5, 0.5, test_str)
        fig.canvas.draw()
        plt.close(fig)
        glyph_warnings = [item for item in w if "Glyph" in str(item.message)]
        if glyph_warnings:
            err = f"FATAL: Missing CJK Glyphs detected in Matplotlib! Found {len(glyph_warnings)} warnings. First warning: {glyph_warnings[0].message}"
            raise RuntimeError(err)
    print("✓ CJK Glyph verification PASSED: zero missing glyphs.")

def setup_ax_style(ax, grid_axis='both'):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#A0AEC0')
    ax.spines['bottom'].set_color('#A0AEC0')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    if grid_axis != 'none':
        ax.grid(axis=grid_axis, linestyle='--', linewidth=0.5, color='#CBD5E0', alpha=0.7)
    ax.set_axisbelow(True)

def generate_chart1_distribution():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT p.name_zh, COUNT(f.id) as cnt
        FROM fibers f
        JOIN categories sub ON f.category_id = sub.id
        JOIN categories p ON sub.parent_id = p.id
        GROUP BY p.id
        ORDER BY cnt ASC
    """)
    rows = c.fetchall()
    conn.close()

    names = [r[0].split(" ")[0] for r in rows]
    counts = [r[1] for r in rows]
    total = sum(counts)
    pcts = [c / total * 100 for c in counts]

    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=300)
    setup_ax_style(ax, grid_axis='x')

    y_pos = np.arange(len(names))
    colors = [C_GRAY, C_TEAL, C_GREEN, C_AMBER, C_BLUE, C_CRIMSON, C_NAVY]

    bars = ax.barh(y_pos, counts, height=0.6, color=colors, edgecolor='none', alpha=0.9)

    for bar, count, pct in zip(bars, counts, pcts):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
                f"{count} 种 ({pct:.1f}%)", va='center', ha='left',
                fontsize=9.5, fontweight='bold', color='#2D3748')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=10, fontweight='medium', color='#1A202C')
    ax.set_xlim(0, max(counts) + 8)
    ax.set_xlabel("收录化学纤维品种数量 (种)", fontsize=10.5, fontweight='bold', color=C_NAVY, labelpad=8)
    ax.set_title("图 1-1  现代化学纤维数据库门类全景构成分布 (共计 117 种)", 
                 fontsize=12, fontweight='bold', color=C_NAVY, pad=12, loc='left')

    out_path = os.path.join(OUTPUT_DIR, "fig1_category_distribution.pdf")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Chart 1 saved: {out_path}")

def generate_chart2_ashby():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT f.code, f.name_zh, f.tensile_strength_gpa, f.tensile_modulus_gpa, c.parent_id
        FROM fibers f
        JOIN categories c ON f.category_id = c.id
        WHERE f.tensile_strength_gpa > 0 AND f.tensile_modulus_gpa > 0
    """)
    rows = c.fetchall()
    conn.close()

    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=300)
    setup_ax_style(ax, grid_axis='both')

    # 分组标注
    groups = {
        'CARBON': {'color': '#1A202C', 'marker': 's', 'label': '先进碳基长丝 (PAN/沥青/CNT/石墨烯)', 'x': [], 'y': [], 'codes': []},
        'HIGH_PERF': {'color': C_CRIMSON, 'marker': '^', 'label': '高性能有机纤维 (芳纶/PBO/UHMWPE/聚芳酯)', 'x': [], 'y': [], 'codes': []},
        'INORGANIC': {'color': C_AMBER, 'marker': 'D', 'label': '无机非金属与金属 (陶瓷SiC/石英/玻纤/金属)', 'x': [], 'y': [], 'codes': []},
        'CONV': {'color': C_BLUE, 'marker': 'o', 'label': '常规大宗与差别化合成 (PET/PA/PP/PAN/PU)', 'x': [], 'y': [], 'codes': []},
        'CELL': {'color': C_GREEN, 'marker': 'v', 'label': '纤维素与生物基 (粘胶/莫代尔/天丝/PLA/海藻)', 'x': [], 'y': [], 'codes': []},
    }

    for r in rows:
        code, name, str_gpa, mod_gpa, pid = r
        if pid == 5:
            grp = 'CARBON'
        elif pid == 4:
            grp = 'HIGH_PERF'
        elif pid == 6:
            grp = 'INORGANIC'
        elif pid in [1, 3]:
            grp = 'CELL'
        else:
            grp = 'CONV'
        
        groups[grp]['x'].append(str_gpa)
        groups[grp]['y'].append(mod_gpa)
        groups[grp]['codes'].append((code, name, str_gpa, mod_gpa))

    for gname, gdata in groups.items():
        ax.scatter(gdata['x'], gdata['y'], c=gdata['color'], marker=gdata['marker'],
                   s=45, alpha=0.75, edgecolors='none', label=gdata['label'])

    ax.set_xscale('log')
    ax.set_yscale('log')

    # 代表性纤维标注（微调坐标避免重叠）
    key_labels = [
        ('PBO', 5.8, 270, 'PBO (超级纤维)', 6.2, 230),
        ('T1000G', 6.37, 294, 'T1000G 碳纤维', 6.8, 320),
        ('M65J', 3.53, 640, 'M65J 超高模碳纤维', 3.8, 680),
        ('UHMWPE', 3.8, 120, 'UHMWPE 迪尼玛', 4.1, 115),
        ('PPTA', 3.2, 110, 'PPTA 对位芳纶', 3.5, 85),
        ('SIC-HI', 3.0, 390, 'SiC 陶瓷纤维', 3.3, 410),
        ('PET', 0.8, 14, '常规聚酯涤纶', 0.92, 15),
        ('MICRO-PA', 0.7, 4.5, '微细旦锦纶', 0.82, 4.0),
        ('LYOCELL', 0.65, 12, '天丝莱赛尔', 0.72, 10.5),
        ('SPANDEX', 0.08, 0.02, '氨纶 (高弹区)', 0.095, 0.022),
    ]

    for code, x, y, lbl, tx, ty in key_labels:
        ax.annotate(lbl, xy=(x, y), xytext=(tx, ty),
                    fontsize=8.5, fontweight='bold', color='#1A202C',
                    arrowprops=dict(arrowstyle='->', lw=0.6, color='#4A5568'))

    ax.set_xlabel("断裂拉伸强度 $\\sigma_{\\mathrm{b}}$ (GPa, 对数坐标)", fontsize=10.5, fontweight='bold', color=C_NAVY, labelpad=8)
    ax.set_ylabel("拉伸弹性模量 $E$ (GPa, 对数坐标)", fontsize=10.5, fontweight='bold', color=C_NAVY, labelpad=8)
    ax.set_title("图 1-2  化学纤维拉伸强度与初始模量 Ashby 材料性能图谱", 
                 fontsize=12, fontweight='bold', color=C_NAVY, pad=12, loc='left')
    ax.legend(loc='lower right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E0', fontsize=8.5)

    out_path = os.path.join(OUTPUT_DIR, "fig2_ashby_strength_modulus.pdf")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Chart 2 saved: {out_path}")

def generate_chart3_comfort_flame():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT code, name_zh, moisture_regain_pct, loi_pct, category_id
        FROM fibers
        WHERE moisture_regain_pct IS NOT NULL AND loi_pct IS NOT NULL
    """)
    rows = c.fetchall()
    conn.close()

    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=300)
    setup_ax_style(ax, grid_axis='both')

    regains = [r[2] for r in rows]
    lois = [r[3] for r in rows]

    # 象限背景色
    ax.axhspan(28, 70, 0, 4.5, color='#FEB2B2', alpha=0.15, label='特种防护阻燃区 (LOI $\\geq 28$, 回潮 $< 4.5\\%$)')
    ax.axhspan(28, 70, 4.5, 20, color='#C6F6D5', alpha=0.25, label='理想高舒适阻燃区 (LOI $\\geq 28$, 回潮 $\\geq 4.5\\%$)')
    ax.axhspan(14, 28, 4.5, 20, color='#EBF8FF', alpha=0.2, label='亲肤舒适服用区 (LOI $< 28$, 回潮 $\\geq 4.5\\%$)')
    ax.axhspan(14, 28, 0, 4.5, color='#EDF2F7', alpha=0.15, label='大宗常规合成区 (易燃/疏水低吸湿)')

    # 绘制基准阈值虚线
    ax.axvline(4.5, color='#718096', linestyle=':', linewidth=1.0)
    ax.axhline(28.0, color='#E53E3E', linestyle='--', linewidth=1.0)
    ax.text(0.3, 28.5, "阻燃安全阈值 (LOI = 28%)", color='#C53030', fontsize=8.5, fontweight='bold')
    ax.text(4.7, 15.0, "舒适亲肤回潮界线 (W = 4.5%)", color='#2B6CB0', fontsize=8.5, fontweight='bold', rotation=90)

    # 散点
    scatter = ax.scatter(regains, lois, c=lois, cmap='viridis', s=50, edgecolors='#2D3748', linewidths=0.5, alpha=0.85)

    # 重点纤维标注（微调坐标避免重叠）
    key_points = [
        ('FR-CV', 12.5, 30.0, 'FR-CV 阻燃粘胶 (舒适+阻燃兼备)', 12.8, 31.5),
        ('PSA', 5.5, 33.0, 'PSA 芳砜纶 (舒适耐火)', 5.8, 34.5),
        ('NOMEX', 5.0, 31.0, '间位芳纶 Nomex', 5.3, 31.2),
        ('PTFE', 0.0, 95.0, 'PTFE 氟纶 (极限难燃)', 0.3, 93.0),
        ('PBI', 15.0, 43.0, 'PBI 聚苯并咪唑 (超强吸湿耐火)', 15.2, 44.5),
        ('MODAL', 12.0, 19.0, '莫代尔 (纯舒适)', 12.2, 21.0),
        ('PET', 0.4, 21.0, '常规涤纶', 0.8, 23.2),
        ('PP', 0.05, 18.0, '常规丙纶', 0.3, 16.0),
        ('COOLMAX', 0.4, 20.5, 'Coolmax 导湿涤纶', 0.9, 19.8),
        ('ALGINATE', 16.0, 34.0, '海藻酸纤维 (难燃抑菌)', 16.2, 35.5),
    ]

    for code, x, y, lbl, tx, ty in key_points:
        ax.annotate(lbl, xy=(x, y), xytext=(tx, ty),
                    fontsize=8.5, fontweight='bold', color='#1A202C',
                    arrowprops=dict(arrowstyle='->', lw=0.6, color='#4A5568'))

    ax.set_xlim(-0.5, 18.5)
    ax.set_ylim(14, 70)
    ax.set_xlabel("公定回潮率 $W$ (%, 亲肤透湿舒适度指标)", fontsize=10.5, fontweight='bold', color=C_NAVY, labelpad=8)
    ax.set_ylabel("极限氧指数 LOI (%, 燃烧难易与阻燃安全性指标)", fontsize=10.5, fontweight='bold', color=C_NAVY, labelpad=8)
    ax.set_title("图 1-3  化学纤维公定回潮率 (舒适度) 与极限氧指数 LOI (阻燃安全性) 四象限定位", 
                 fontsize=12, fontweight='bold', color=C_NAVY, pad=12, loc='left')

    ax.legend(loc='upper left', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E0', fontsize=8)

    out_path = os.path.join(OUTPUT_DIR, "fig3_comfort_vs_flame.pdf")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Chart 3 saved: {out_path}")

def generate_chart4_service_temp():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT code, name_zh, max_service_temp_c, typical_applications
        FROM fibers
        WHERE max_service_temp_c IS NOT NULL
        ORDER BY max_service_temp_c DESC
        LIMIT 14
    """)
    rows = c.fetchall()
    conn.close()

    # 倒序排列以使最高温在上方
    rows = list(reversed(rows))
    names = [f"{r[1]} ({r[0]})" for r in rows]
    temps = [r[2] for r in rows]

    fig, ax = plt.subplots(figsize=(9.5, 6.0), dpi=300)
    setup_ax_style(ax, grid_axis='x')

    y_pos = np.arange(len(names))
    
    # 根据温度区间着色
    colors = []
    for t in temps:
        if t >= 1000:
            colors.append('#742A2A') # 深红棕 (极高温热障)
        elif t >= 500:
            colors.append('#C53030') # 烈焰红
        elif t >= 300:
            colors.append('#DD6B20') # 橙色
        elif t >= 200:
            colors.append('#3182CE') # 科技蓝
        else:
            colors.append('#2B6CB0')

    bars = ax.barh(y_pos, temps, height=0.6, color=colors, alpha=0.9)

    for bar, temp in zip(bars, temps):
        ax.text(bar.get_width() + 25, bar.get_y() + bar.get_height()/2,
                f"{temp:.1f} ℃" if isinstance(temp, float) else f"{temp} ℃",
                va='center', ha='left',
                fontsize=9.5, fontweight='bold', color='#1A202C')

    # 添加温度应用区间竖向参考带 (覆盖至 2450℃，确保 ZRO2-F 2200℃ 条形与文字完整容纳)
    ax.axvspan(0, 150, color='#E2E8F0', alpha=0.3, label='民用常规服用温度区 (<150℃)')
    ax.axvspan(150, 300, color='#BEE3F8', alpha=0.3, label='工业中高温服役区 (150-300℃)')
    ax.axvspan(300, 700, color='#FEEBC8', alpha=0.3, label='特种耐高温阻燃区 (300-700℃)')
    ax.axvspan(700, 2450, color='#FED7D7', alpha=0.3, label='超高温陶瓷/航空热障区 (>700℃)')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9.5, color='#2D3748')
    ax.set_xlim(0, 2450)
    ax.set_xlabel("最高连续服役耐温极限 ($^\\circ\\mathrm{C}$)", fontsize=10.5, fontweight='bold', color=C_NAVY, labelpad=8)
    ax.set_title("图 1-4  现代化学纤维耐温极限服役温度天花板梯队排行 (Top 14)", 
                 fontsize=12, fontweight='bold', color=C_NAVY, pad=12, loc='left')
    ax.legend(loc='lower right', frameon=True, facecolor='#FFFFFF', edgecolor='#CBD5E0', fontsize=8.5)

    out_path = os.path.join(OUTPUT_DIR, "fig4_service_temp_ladder.pdf")
    plt.savefig(out_path, bbox_inches='tight')
    plt.close()
    print(f"Chart 4 saved: {out_path}")

def generate_all_charts():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Initializing Academic Fonts...")
    init_academic_fonts()
    print("Generating Academic Charts...")
    generate_chart1_distribution()
    generate_chart2_ashby()
    generate_chart3_comfort_flame()
    generate_chart4_service_temp()
    print("All Academic Charts generated successfully in", OUTPUT_DIR)

if __name__ == "__main__":
    generate_all_charts()
