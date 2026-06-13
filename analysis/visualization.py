#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化脚本 - 作业四 成员5

职责：
  1. 设计并制作全套分析可视化图表（≥12张，300dpi PNG）
  2. 统一图表配色方案与中文字体适配
  3. 输出图表标题与说明清单（charts_catalog.md）

图表覆盖：
  - 各组数据规模对比（分组柱状图）
  - 各组院系分布（堆叠柱状图）
  - 各组共享课程比例（条形图）
  - 各组男女比例对比（分组条形图 + 饼图）
  - 组间相似度热力图
  - 本组与最相似组雷达图
  - 各组学号/课程编号格式对比
  - 各组学分分布对比
  - 各组成绩缺失与分布
  - 相似度排名条形图
  - 各组综合特征画像热力图
  - 数据异常总览仪表盘

依赖：pandas, numpy, matplotlib, seaborn, scikit-learn, scipy
"""

import os
import sys
import io
import re
import warnings
from datetime import datetime

# 修复 Windows GBK 终端下 emoji 输出问题
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, OSError):
        pass

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch, FancyBboxPatch
import seaborn as sns
from collections import defaultdict

# 尝试导入相似度计算所需库
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[WARN] scikit-learn 未安装，相似度相关图表将跳过")

# ============================================================
# 全局设置
# ============================================================
# 路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
CLEANED_DIR = os.path.join(DATA_DIR, 'cleaned')
FIGURES_DIR = os.path.join(SCRIPT_DIR, 'figures')
CATALOG_PATH = os.path.join(SCRIPT_DIR, 'charts_catalog.md')

# 本组组号
OWN_GROUP = 16

# 排除的不完整组
EXCLUDED_GROUPS = {9, 19, 25}

# ============================================================
# 字体设置（统一使用英文 DejaVu Sans，避免 CJK 渲染兼容性问题）
# ============================================================
CN_FONT = None
USE_CN = False

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
print("[INFO] Using DejaVu Sans font (English labels)")

matplotlib.rcParams['axes.unicode_minus'] = False

# 抑制 matplotlib 字体回退警告（Windows 有字体链接机制，即使有警告中文也能正常渲染）
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
logging.getLogger('matplotlib.text').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*Glyph.*missing from font.*')

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# ============================================================
# 统一配色方案
# ============================================================
# 主色调
COLOR_OWN = '#27ae60'        # 本组 — 翠绿
COLOR_SIMILAR = '#e67e22'    # 最相似组 — 橙色
COLOR_OTHER = '#5dade2'      # 其他组 — 浅蓝
COLOR_ANOMALY = '#e74c3c'    # 异常 — 红色
COLOR_WARN = '#f39c12'       # 警告 — 黄色
COLOR_NORMAL = '#2ecc71'     # 正常 — 绿色

# 院系配色
DEPT_COLORS = {'A': '#3498db', 'B': '#e74c3c', 'C': '#2ecc71'}
DEPT_COLORS_LIGHT = {'A': '#aed6f1', 'B': '#f5b7b1', 'C': '#a9dfbf'}

# 性别配色
GENDER_COLORS = {'M': '#3498db', 'F': '#e74c3c'}

# 调色板
PALETTE_10 = sns.color_palette("tab10", 10)
PALETTE_SET2 = sns.color_palette("Set2", 8)
PALETTE_SET3 = sns.color_palette("Set3", 12)

# 标签语言切换
def L(cn_text, en_text):
    """返回英文标签（统一使用英文，避免中文字体渲染问题）"""
    return en_text


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


# ============================================================
# 数据加载
# ============================================================
def load_data():
    """加载清洗后的数据"""
    print("=" * 70)
    print(L("📂 加载数据...", "[INFO] Loading data..."))

    students = pd.read_csv(os.path.join(CLEANED_DIR, 'students_cleaned.csv'))
    courses = pd.read_csv(os.path.join(CLEANED_DIR, 'courses_cleaned.csv'))
    sc = pd.read_csv(os.path.join(CLEANED_DIR, 'sc_cleaned.csv'))

    print(f"  学生表: {len(students)} 条, {students['group_no'].nunique()} 个组")
    print(f"  课程表: {len(courses)} 条, {courses['group_no'].nunique()} 个组")
    print(f"  选课表: {len(sc)} 条, {sc['group_no'].nunique()} 个组")

    return students, courses, sc


# ============================================================
# 统计计算（自包含，不依赖其他成员脚本）
# ============================================================
def compute_group_stats(students, courses, sc):
    """计算各组核心统计指标"""
    print(L("\n📊 计算各组统计指标...", "\n[INFO] Computing group statistics..."))

    all_groups = sorted(set(students['group_no'].unique())
                        | set(courses['group_no'].unique())
                        | set(sc['group_no'].unique()))

    s_g = set(students['group_no'].unique())
    c_g = set(courses['group_no'].unique())
    sc_g = set(sc['group_no'].unique())

    records = []
    for g in all_groups:
        g_s = students[students['group_no'] == g] if g in s_g else pd.DataFrame()
        g_c = courses[courses['group_no'] == g] if g in c_g else pd.DataFrame()
        g_sc = sc[sc['group_no'] == g] if g in sc_g else pd.DataFrame()

        student_count = len(g_s)
        course_count = len(g_c)
        sc_count = len(g_sc)

        # 院系分布
        s_dept = g_s['dept_no'].value_counts().to_dict() if len(g_s) > 0 else {}
        c_dept = g_c['dept_no'].value_counts().to_dict() if len(g_c) > 0 else {}

        # 共享比例
        if len(g_c) > 0 and 'share_flag' in g_c.columns:
            share_y = (g_c['share_flag'] == 'Y').sum()
            share_total = g_c['share_flag'].isin(['Y', 'N']).sum()
            share_ratio = share_y / share_total if share_total > 0 else 0
        else:
            share_ratio = 0

        # 性别比例
        if len(g_s) > 0 and 'gender' in g_s.columns:
            male_count = (g_s['gender'] == 'M').sum()
            female_count = (g_s['gender'] == 'F').sum()
            total_gender = male_count + female_count
            male_ratio = male_count / total_gender if total_gender > 0 else 0.5
        else:
            male_ratio = 0.5

        # 学分
        if len(g_c) > 0 and 'credit' in g_c.columns:
            credit_mean = g_c['credit'].mean()
            credit_std = g_c['credit'].std()
        else:
            credit_mean = 0
            credit_std = 0

        # 成绩
        if len(g_sc) > 0 and 'score' in g_sc.columns:
            non_null = g_sc['score'].dropna()
            score_non_null_ratio = len(non_null) / len(g_sc)
            score_mean = non_null.mean() if len(non_null) > 0 else np.nan
        else:
            score_non_null_ratio = 0
            score_mean = np.nan

        # 学号/课程编号格式
        if len(g_s) > 0:
            sids = g_s['student_id'].astype(str)
            sid_mean_len = sids.str.len().mean()
            sid_has_alpha = sids.str.contains(r'[A-Za-z]').mean()
        else:
            sid_mean_len = 0
            sid_has_alpha = 0

        if len(g_c) > 0:
            cids = g_c['course_id'].astype(str)
            cid_mean_len = cids.str.len().mean()
        else:
            cid_mean_len = 0

        # 数据完整性
        completeness = sum([g in s_g, g in c_g, g in sc_g])

        # 异常评分
        anomaly_score = 0
        if completeness < 3:
            anomaly_score += 2
        if student_count > 0 and abs(student_count - 150) > 30:
            anomaly_score += 1
        if course_count > 0 and abs(course_count - 30) > 6:
            anomaly_score += 1
        if sc_count > 0 and abs(sc_count - 750) > 150:
            anomaly_score += 1
        if score_non_null_ratio == 0 and sc_count > 0:
            anomaly_score += 1

        records.append({
            'group_no': int(g),
            'student_count': student_count,
            'course_count': course_count,
            'sc_count': sc_count,
            'sc_per_student': round(sc_count / student_count, 2) if student_count > 0 else 0,
            's_dept_A': s_dept.get('A', 0),
            's_dept_B': s_dept.get('B', 0),
            's_dept_C': s_dept.get('C', 0),
            'c_dept_A': c_dept.get('A', 0),
            'c_dept_B': c_dept.get('B', 0),
            'c_dept_C': c_dept.get('C', 0),
            'share_ratio': round(share_ratio, 3),
            'male_ratio': round(male_ratio, 3),
            'credit_mean': round(credit_mean, 2),
            'credit_std': round(credit_std, 2) if not np.isnan(credit_std) else 0,
            'score_non_null_ratio': round(score_non_null_ratio, 3),
            'score_mean': round(score_mean, 1) if not np.isnan(score_mean) else np.nan,
            'sid_mean_len': round(sid_mean_len, 1),
            'sid_has_alpha': round(sid_has_alpha, 3),
            'cid_mean_len': round(cid_mean_len, 1),
            'completeness': completeness,
            'anomaly_score': anomaly_score,
        })

    stats_df = pd.DataFrame(records)
    print(f"  完成: {len(stats_df)} 个组, {len(stats_df.columns)-1} 个指标")
    return stats_df, all_groups


def compute_similarity(stats_df):
    """计算组间相似度矩阵"""
    if not SKLEARN_AVAILABLE:
        print("[WARN] 跳过相似度计算（scikit-learn未安装）")
        return None, None, None, None, None

    print(L("\n🔢 计算相似度矩阵...", "\n[INFO] Computing similarity matrix..."))

    # 筛选可分析组
    analyzable = stats_df[
        (stats_df['student_count'] > 0) &
        (stats_df['course_count'] > 0) &
        (~stats_df['group_no'].isin(EXCLUDED_GROUPS))
    ].copy()

    feature_cols = [
        'student_count', 'course_count', 'sc_count', 'sc_per_student',
        'share_ratio', 'male_ratio', 'credit_mean',
        'sid_mean_len', 'sid_has_alpha', 'cid_mean_len',
        'score_non_null_ratio',
    ]

    # 添加入院系分布比例
    for dept in ['A', 'B', 'C']:
        analyzable[f's_dept_{dept}_ratio'] = (
            analyzable[f's_dept_{dept}'] / analyzable['student_count']
        ).fillna(0)
        analyzable[f'c_dept_{dept}_ratio'] = (
            analyzable[f'c_dept_{dept}'] / analyzable['course_count']
        ).fillna(0)
        feature_cols.extend([f's_dept_{dept}_ratio', f'c_dept_{dept}_ratio'])

    # 处理缺失值
    feature_matrix = analyzable[feature_cols].copy()
    for col in feature_matrix.columns:
        if feature_matrix[col].isnull().any():
            feature_matrix[col].fillna(feature_matrix[col].median(), inplace=True)

    group_nos = analyzable['group_no'].values

    # 标准化
    scaler = StandardScaler()
    feature_scaled = scaler.fit_transform(feature_matrix)

    # 余弦相似度
    cos_sim = cosine_similarity(feature_scaled)
    # 欧氏距离转相似度
    euc_dist = euclidean_distances(feature_scaled)
    euc_sim = 1.0 / (1.0 + euc_dist)
    # 综合
    combined_sim = 0.5 * cos_sim + 0.5 * euc_sim

    combined_df = pd.DataFrame(combined_sim, index=group_nos, columns=group_nos)

    # 找最相似组
    if OWN_GROUP in group_nos:
        own_idx = list(group_nos).index(OWN_GROUP)
        own_sim = combined_sim[own_idx]

        sim_ranking = []
        for i, g in enumerate(group_nos):
            if g != OWN_GROUP:
                sim_ranking.append({
                    'group_no': int(g),
                    'combined_sim': round(own_sim[i], 4),
                    'cosine_sim': round(cos_sim[own_idx][i], 4),
                    'euclidean_sim': round(euc_sim[own_idx][i], 4),
                })
        sim_ranking_df = pd.DataFrame(sim_ranking).sort_values('combined_sim', ascending=False)
        most_similar = int(sim_ranking_df.iloc[0]['group_no'])

        print(f"  最相似组: {most_similar} "
              f"(综合相似度: {sim_ranking_df.iloc[0]['combined_sim']:.4f})")
    else:
        sim_ranking_df = None
        most_similar = None

    return combined_df, cos_sim, sim_ranking_df, most_similar, group_nos, feature_scaled, analyzable


# ============================================================
# 图表生成函数
# ============================================================
def save_figure(fig, filename):
    """保存图表到 figures 目录"""
    filepath = os.path.join(FIGURES_DIR, filename)
    fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  ✅ {filename}")
    return filepath


def get_group_colors(stats_df, most_similar=None):
    """为各组分配颜色"""
    colors = []
    for g in stats_df['group_no']:
        if g == OWN_GROUP:
            colors.append(COLOR_OWN)
        elif most_similar is not None and g == most_similar:
            colors.append(COLOR_SIMILAR)
        elif g in EXCLUDED_GROUPS:
            colors.append('#bdc3c7')  # 灰色 = 不完整
        else:
            colors.append(COLOR_OTHER)
    return colors


# ---- 图1: 各组数据规模4合1仪表盘 ----
def plot_scale_dashboard(stats_df, most_similar):
    """各组学生数/课程数/选课数/人均选课 四合一对比"""
    fig, axes = plt.subplots(2, 2, figsize=(18, 11))
    colors = get_group_colors(stats_df, most_similar)
    groups_str = stats_df['group_no'].astype(str)

    # 1.1 学生数
    ax = axes[0, 0]
    bars = ax.bar(groups_str, stats_df['student_count'], color=colors, alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.axhline(y=150, color='gray', linestyle='--', alpha=0.5, linewidth=1, label=L('参考值 150', 'Ref: 150'))
    ax.set_title(L('① 各组学生数量', '① Student Count by Group'), fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=10)
    ax.set_ylabel(L('学生数', 'Student Count'), fontsize=10)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    # 标注数值
    for bar, val in zip(bars, stats_df['student_count']):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    str(int(val)), ha='center', fontsize=6.5, fontweight='bold')
    ax.set_ylim(0, stats_df['student_count'].max() * 1.18)

    # 1.2 课程数
    ax = axes[0, 1]
    bars = ax.bar(groups_str, stats_df['course_count'], color=colors, alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.axhline(y=30, color='gray', linestyle='--', alpha=0.5, linewidth=1, label=L('参考值 30', 'Ref: 30'))
    ax.set_title(L('② 各组课程数量', '② Course Count by Group'), fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=10)
    ax.set_ylabel(L('课程数', 'Course Count'), fontsize=10)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    for bar, val in zip(bars, stats_df['course_count']):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(int(val)), ha='center', fontsize=6.5, fontweight='bold')
    ax.set_ylim(0, stats_df['course_count'].max() * 1.18)

    # 1.3 选课数
    ax = axes[1, 0]
    bars = ax.bar(groups_str, stats_df['sc_count'], color=colors, alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.axhline(y=750, color='gray', linestyle='--', alpha=0.5, linewidth=1, label=L('参考值 750', 'Ref: 750'))
    ax.set_title(L('③ 各组选课记录数', '③ SC Record Count by Group'), fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=10)
    ax.set_ylabel(L('选课记录数', 'SC Count'), fontsize=10)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    for bar, val in zip(bars, stats_df['sc_count']):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
                    str(int(val)), ha='center', fontsize=6.5, fontweight='bold')
    ax.set_ylim(0, stats_df['sc_count'].max() * 1.18)

    # 1.4 人均选课
    ax = axes[1, 1]
    valid = stats_df[stats_df['sc_per_student'] > 0]
    colors_valid = get_group_colors(valid, most_similar)
    bars = ax.bar(valid['group_no'].astype(str), valid['sc_per_student'],
                  color=colors_valid, alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.axhline(y=5, color='gray', linestyle='--', alpha=0.5, linewidth=1, label=L('参考值 5', 'Ref: 5'))
    ax.set_title(L('④ 各组人均选课数', '④ SC per Student by Group'), fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=10)
    ax.set_ylabel(L('人均选课', 'SC / Student'), fontsize=10)
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    for bar, val in zip(bars, valid['sc_per_student']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.1f}', ha='center', fontsize=6.5, fontweight='bold')
    ax.set_ylim(0, valid['sc_per_student'].max() * 1.18)

    # 图例
    legend_elements = [
        Patch(facecolor=COLOR_OWN, label=L(f'本组 (G{OWN_GROUP})', f'Own (G{OWN_GROUP})')),
        Patch(facecolor=COLOR_OTHER, label=L('其他组', 'Others')),
        Patch(facecolor='#bdc3c7', label=L('不完整组', 'Incomplete')),
    ]
    if most_similar:
        legend_elements.insert(1, Patch(facecolor=COLOR_SIMILAR,
                                        label=L(f'最相似组 (G{most_similar})',
                                                f'Most Similar (G{most_similar})')))
    fig.legend(handles=legend_elements, loc='upper right', fontsize=9,
               bbox_to_anchor=(0.99, 0.99), framealpha=0.9)

    fig.suptitle(L('各组数据规模全景对比', 'Group Data Scale Overview'),
                 fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    return save_figure(fig, 'fig_v1_scale_dashboard.png')


# ---- 图2: 各组院系分布堆叠柱状图 ----
def plot_dept_distribution(stats_df, most_similar):
    """学生和课程在各院系的分布"""
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    valid = stats_df[stats_df['student_count'] > 0]
    groups_str = valid['group_no'].astype(str)
    x = np.arange(len(valid))

    # 学生院系分布
    ax = axes[0]
    depts = ['A', 'B', 'C']
    bottom = np.zeros(len(valid))
    for dept in depts:
        vals = valid[f's_dept_{dept}'].values
        ax.bar(x, vals, bottom=bottom, label=L(f'{dept}院', f'Dept {dept}'),
               color=DEPT_COLORS[dept], alpha=0.85, edgecolor='white', linewidth=0.5)
        # 标注数值
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(i, bottom[i] + v/2, str(int(v)), ha='center', va='center',
                       fontsize=6, fontweight='bold', color='white')
        bottom += vals
    ax.set_title(L('学生院系分布', 'Student Department Distribution'),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('学生数', 'Student Count'))
    ax.set_xticks(x)
    ax.set_xticklabels(groups_str, rotation=45, fontsize=8)
    ax.legend(fontsize=8)
    # 高亮本组
    for i, g in enumerate(valid['group_no']):
        if g == OWN_GROUP:
            ax.axvline(x=i, color=COLOR_OWN, linewidth=2, alpha=0.5, linestyle='--')

    # 课程院系分布
    ax = axes[1]
    bottom = np.zeros(len(valid))
    for dept in depts:
        vals = valid[f'c_dept_{dept}'].values
        ax.bar(x, vals, bottom=bottom, label=L(f'{dept}院', f'Dept {dept}'),
               color=DEPT_COLORS[dept], alpha=0.85, edgecolor='white', linewidth=0.5)
        for i, v in enumerate(vals):
            if v > 0:
                ax.text(i, bottom[i] + v/2, str(int(v)), ha='center', va='center',
                       fontsize=6, fontweight='bold', color='white')
        bottom += vals
    ax.set_title(L('课程院系分布', 'Course Department Distribution'),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('课程数', 'Course Count'))
    ax.set_xticks(x)
    ax.set_xticklabels(groups_str, rotation=45, fontsize=8)
    ax.legend(fontsize=8)
    for i, g in enumerate(valid['group_no']):
        if g == OWN_GROUP:
            ax.axvline(x=i, color=COLOR_OWN, linewidth=2, alpha=0.5, linestyle='--')

    fig.suptitle(L('各组院系数据分布对比', 'Department Distribution by Group'),
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    return save_figure(fig, 'fig_v2_dept_distribution.png')


# ---- 图3: 各组共享课程比例 ----
def plot_share_ratio(stats_df, most_similar):
    """共享课程比例水平条形图"""
    valid = stats_df[(stats_df['course_count'] > 0)].copy()
    valid = valid.sort_values('share_ratio', ascending=True)

    fig, ax = plt.subplots(figsize=(14, 8))
    groups_str = valid['group_no'].astype(str)
    colors = get_group_colors(valid, most_similar)

    bars = ax.barh(groups_str, valid['share_ratio'] * 100, color=colors,
                   alpha=0.88, edgecolor='white', linewidth=0.5, height=0.7)

    # 标注百分比
    for bar, val, g in zip(bars, valid['share_ratio'], valid['group_no']):
        label = f'{val*100:.0f}%'
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
                label, va='center', fontsize=9, fontweight='bold')

    # 标注本组参考线
    own_share = valid[valid['group_no'] == OWN_GROUP]['share_ratio']
    if len(own_share) > 0:
        own_val = own_share.values[0] * 100
        ax.axvline(x=own_val, color=COLOR_OWN, linestyle='--', alpha=0.6, linewidth=1.5,
                   label=L(f'本组 ({own_val:.0f}%)', f'Own G{OWN_GROUP} ({own_val:.0f}%)'))

    ax.set_title(L('各组共享课程比例对比', 'Shared Course Ratio by Group'),
                 fontsize=15, fontweight='bold')
    ax.set_xlabel(L('共享课程比例 (%)', 'Shared Course Ratio (%)'), fontsize=11)
    ax.set_ylabel(L('组号', 'Group No.'), fontsize=11)
    ax.set_xlim(0, 110)
    ax.legend(fontsize=9, loc='lower right')
    plt.tight_layout()
    return save_figure(fig, 'fig_v3_share_ratio.png')


# ---- 图4: 各组男女比例对比（分组条形图） ----
def plot_gender_ratio(stats_df, most_similar):
    """男女比例分组条形图"""
    valid = stats_df[stats_df['student_count'] > 0].copy()

    fig, ax = plt.subplots(figsize=(16, 6))
    x = np.arange(len(valid))
    width = 0.35

    male_pct = valid['male_ratio'] * 100
    female_pct = (1 - valid['male_ratio']) * 100

    bars1 = ax.bar(x - width/2, male_pct, width, label=L('男生', 'Male'),
                   color='#3498db', alpha=0.85, edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, female_pct, width, label=L('女生', 'Female'),
                   color='#e74c3c', alpha=0.85, edgecolor='white', linewidth=0.5)

    # 高亮本组
    own_idx = list(valid['group_no']).index(OWN_GROUP) if OWN_GROUP in valid['group_no'].values else None
    if own_idx is not None:
        bars1[own_idx].set_color('#1a6ecc')
        bars1[own_idx].set_edgecolor(COLOR_OWN)
        bars1[own_idx].set_linewidth(2)
        bars2[own_idx].set_color('#cc2c1a')
        bars2[own_idx].set_edgecolor(COLOR_OWN)
        bars2[own_idx].set_linewidth(2)

    ax.set_title(L('各组学生性别比例对比', 'Gender Ratio by Group'),
                 fontsize=15, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=11)
    ax.set_ylabel(L('比例 (%)', 'Ratio (%)'), fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(valid['group_no'].astype(str), rotation=45, fontsize=9)
    ax.set_ylim(0, 105)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.4, linewidth=0.8)
    ax.legend(fontsize=10)

    # 标注本组
    if own_idx is not None:
        ax.annotate(L('← 本组', '← Own'),
                    xy=(own_idx, male_pct.iloc[own_idx]),
                    xytext=(own_idx - 0.5, male_pct.iloc[own_idx] + 12),
                    fontsize=10, fontweight='bold', color=COLOR_OWN,
                    arrowprops=dict(arrowstyle='->', color=COLOR_OWN, lw=1.5))

    plt.tight_layout()
    return save_figure(fig, 'fig_v4_gender_ratio.png')


# ---- 图5: 各组男女比例饼图阵列 ----
def plot_gender_pie_grid(stats_df):
    """选取代表性组展示男女比例饼图"""
    valid = stats_df[stats_df['student_count'] > 0].copy()
    # 选本组 + 前8个其他组
    own_row = valid[valid['group_no'] == OWN_GROUP]
    others = valid[valid['group_no'] != OWN_GROUP].head(8)
    selected = pd.concat([own_row, others])

    n = len(selected)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4.5))
    axes = axes.flatten() if n > 1 else [axes]

    for idx, (_, row) in enumerate(selected.iterrows()):
        ax = axes[idx]
        g = int(row['group_no'])
        male = row['male_ratio']
        female = 1 - male
        sizes = [male * 100, female * 100]
        labels = [L('男生', 'Male'), L('女生', 'Female')]
        colors_pie = ['#3498db', '#e74c3c']
        explode = (0.03, 0.03)

        wedges, texts, autotexts = ax.pie(
            sizes, explode=explode, labels=labels, colors=colors_pie,
            autopct='%1.1f%%', startangle=90, pctdistance=0.6,
            textprops={'fontsize': 9}
        )
        for at in autotexts:
            at.set_fontweight('bold')
            at.set_fontsize(10)

        title = L(f'组{g} (本组)', f'G{g} (Own)') if g == OWN_GROUP else f'G{g}'
        title_color = COLOR_OWN if g == OWN_GROUP else 'black'
        ax.set_title(title, fontsize=12, fontweight='bold', color=title_color)

    # 隐藏多余的子图
    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle(L('各组男女比例饼图', 'Gender Ratio Pie Charts by Group'),
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    return save_figure(fig, 'fig_v5_gender_pie.png')


# ---- 图6: 组间相似度热力图 ----
def plot_similarity_heatmap(combined_df, most_similar):
    """相似度热力图"""
    if combined_df is None:
        print("  [SKIP] 相似度热力图 — 缺少相似度数据")
        return None

    fig, ax = plt.subplots(figsize=(16, 14))
    mask = np.zeros_like(combined_df, dtype=bool)
    np.fill_diagonal(mask, True)

    sns.heatmap(combined_df, annot=True, fmt='.2f', cmap='RdYlGn',
                mask=mask, linewidths=0.5, linecolor='white',
                ax=ax, vmin=0.0, vmax=1.0, center=0.5,
                cbar_kws={'label': L('综合相似度', 'Combined Similarity'),
                          'shrink': 0.8},
                annot_kws={'fontsize': 7})

    # 高亮本组行/列
    if str(OWN_GROUP) in combined_df.index:
        own_pos = list(combined_df.index).index(str(OWN_GROUP)) \
            if str(OWN_GROUP) in [str(x) for x in combined_df.index] else \
            list(combined_df.index).index(OWN_GROUP) \
            if OWN_GROUP in combined_df.index else None

    ax.set_title(L('组间综合相似度热力图', 'Inter-Group Combined Similarity Heatmap'),
                 fontsize=16, fontweight='bold', pad=15)
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=11)
    ax.set_ylabel(L('组号', 'Group No.'), fontsize=11)
    plt.tight_layout()
    return save_figure(fig, 'fig_v6_similarity_heatmap.png')


# ---- 图7: 本组与最相似组雷达图 ----
def plot_radar_comparison(stats_df, most_similar):
    """雷达图多维对比"""
    if most_similar is None:
        print("  [SKIP] 雷达图 — 未找到最相似组")
        return None

    own = stats_df[stats_df['group_no'] == OWN_GROUP]
    sim = stats_df[stats_df['group_no'] == most_similar]
    if len(own) == 0 or len(sim) == 0:
        return None
    own = own.iloc[0]
    sim = sim.iloc[0]

    # 选取雷达图特征
    radar_items = [
        ('student_count', L('学生数', 'Students'), 'scale'),
        ('course_count', L('课程数', 'Courses'), 'scale'),
        ('sc_per_student', L('人均选课', 'SC/Student'), 'density'),
        ('share_ratio', L('共享率', 'Share Ratio'), 'ratio'),
        ('male_ratio', L('男生率', 'Male Ratio'), 'ratio'),
        ('credit_mean', L('平均学分', 'Avg Credit'), 'value'),
        ('score_non_null_ratio', L('成绩非空率', 'Score Available'), 'ratio'),
        ('sid_mean_len', L('学号长度', 'ID Length'), 'format'),
    ]

    labels = [item[1] for item in radar_items]
    cols = [item[0] for item in radar_items]

    N = len(labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

    # 归一化到 [0, 1]
    own_vals = []
    sim_vals = []
    for col in cols:
        col_data = stats_df[col].dropna()
        col_min = col_data.min()
        col_max = col_data.max()
        col_range = col_max - col_min if col_max != col_min else 1
        own_v = (own[col] - col_min) / col_range if not np.isnan(own[col]) else 0.5
        sim_v = (sim[col] - col_min) / col_range if not np.isnan(sim[col]) else 0.5
        own_vals.append(own_v)
        sim_vals.append(sim_v)

    # 闭合
    own_vals += own_vals[:1]
    sim_vals += sim_vals[:1]
    angles_closed = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.plot(angles_closed, own_vals, 'o-', linewidth=2.5, color=COLOR_OWN,
            label=L(f'组{OWN_GROUP} (本组)', f'G{OWN_GROUP} (Own)'), markersize=8)
    ax.fill(angles_closed, own_vals, alpha=0.15, color=COLOR_OWN)
    ax.plot(angles_closed, sim_vals, 's-', linewidth=2.5, color=COLOR_SIMILAR,
            label=L(f'组{most_similar} (最相似)', f'G{most_similar} (Most Similar)'), markersize=8)
    ax.fill(angles_closed, sim_vals, alpha=0.15, color=COLOR_SIMILAR)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1.08)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8, color='gray')
    ax.set_title(L(f'组{OWN_GROUP} vs 组{most_similar} 多维特征雷达图',
                   f'G{OWN_GROUP} vs G{most_similar} Feature Radar'),
                 fontsize=15, fontweight='bold', pad=25)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=11, framealpha=0.9)
    plt.tight_layout()
    return save_figure(fig, 'fig_v7_radar_comparison.png')


# ---- 图8: 相似度排名条形图 ----
def plot_similarity_ranking(sim_ranking_df, most_similar):
    """各组与本组的相似度排名"""
    if sim_ranking_df is None:
        print("  [SKIP] 相似度排名 — 缺少数据")
        return None

    df = sim_ranking_df.sort_values('combined_sim', ascending=True)

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = [COLOR_SIMILAR if g == most_similar else COLOR_OTHER
              for g in df['group_no']]

    bars = ax.barh(df['group_no'].astype(str), df['combined_sim'],
                   color=colors, alpha=0.88, edgecolor='white', linewidth=0.5, height=0.7)

    # 标注数值
    for bar, val in zip(bars, df['combined_sim']):
        ax.text(bar.get_width() + 0.008, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9, fontweight='bold')

    # 标注"最相似"
    top_g = df.iloc[-1]  # 最高相似度
    ax.annotate(L(f'★ 最相似: 组{int(top_g["group_no"])}\n  相似度: {top_g["combined_sim"]:.4f}',
                  f'★ Most Similar: G{int(top_g["group_no"])}\n  Sim: {top_g["combined_sim"]:.4f}'),
                xy=(top_g['combined_sim'], len(df) - 1),
                xytext=(top_g['combined_sim'] + 0.15, len(df) - 2),
                fontsize=11, fontweight='bold', color=COLOR_SIMILAR,
                arrowprops=dict(arrowstyle='->', color=COLOR_SIMILAR, lw=2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#fff9e6', alpha=0.9))

    ax.set_title(L(f'各组与组{OWN_GROUP} (本组) 的相似度排名',
                   f'Similarity Ranking to G{OWN_GROUP} (Own Group)'),
                 fontsize=15, fontweight='bold')
    ax.set_xlabel(L('综合相似度', 'Combined Similarity'), fontsize=11)
    ax.set_ylabel(L('组号', 'Group No.'), fontsize=11)
    ax.set_xlim(0, 1.05)
    plt.tight_layout()
    return save_figure(fig, 'fig_v8_similarity_ranking.png')


# ---- 图9: 各组学号/课程编号格式对比 ----
def plot_id_format_comparison(students, courses):
    """学号和课程编号长度/格式对比"""
    # 收集每组数据
    sid_data = {}
    cid_data = {}
    for g in sorted(students['group_no'].unique()):
        g_s = students[students['group_no'] == g]
        sid_data[g] = g_s['student_id'].astype(str).str.len()

    for g in sorted(courses['group_no'].unique()):
        g_c = courses[courses['group_no'] == g]
        cid_data[g] = g_c['course_id'].astype(str).str.len()

    fig, axes = plt.subplots(2, 1, figsize=(18, 10))

    # 学号长度箱线图
    ax = axes[0]
    sorted_groups = sorted(sid_data.keys())
    bp_data = [sid_data[g] for g in sorted_groups]
    labels = [f'G{g}' for g in sorted_groups]

    bp = ax.boxplot(bp_data, tick_labels=labels, patch_artist=True, showfliers=True,
                    widths=0.6, medianprops=dict(color='black', linewidth=1.5))
    for i, (patch, g) in enumerate(zip(bp['boxes'], sorted_groups)):
        if g == OWN_GROUP:
            patch.set_facecolor(COLOR_OWN)
            patch.set_alpha(0.7)
        else:
            patch.set_facecolor('#3498db')
            patch.set_alpha(0.5)
    ax.set_title(L('各组学号长度分布箱线图', 'Student ID Length Distribution by Group'),
                 fontsize=14, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('学号长度 (字符)', 'Student ID Length (chars)'))
    ax.tick_params(axis='x', rotation=45)
    ax.axhline(y=4, color='gray', linestyle='--', alpha=0.4, linewidth=0.8, label='len=4')
    ax.legend(fontsize=8)

    # 课程编号长度箱线图
    ax = axes[1]
    sorted_groups = sorted(cid_data.keys())
    bp_data = [cid_data[g] for g in sorted_groups]
    labels = [f'G{g}' for g in sorted_groups]

    bp = ax.boxplot(bp_data, tick_labels=labels, patch_artist=True, showfliers=True,
                    widths=0.6, medianprops=dict(color='black', linewidth=1.5))
    for i, (patch, g) in enumerate(zip(bp['boxes'], sorted_groups)):
        if g == OWN_GROUP:
            patch.set_facecolor(COLOR_OWN)
            patch.set_alpha(0.7)
        else:
            patch.set_facecolor('#e67e22')
            patch.set_alpha(0.5)
    ax.set_title(L('各组课程编号长度分布箱线图', 'Course ID Length Distribution by Group'),
                 fontsize=14, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('课程编号长度 (字符)', 'Course ID Length (chars)'))
    ax.tick_params(axis='x', rotation=45)

    fig.suptitle(L('各组ID编码格式差异分析', 'Group ID Format Difference Analysis'),
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    return save_figure(fig, 'fig_v9_id_format.png')


# ---- 图10: 各组学分分布对比 ----
def plot_credit_distribution(courses, stats_df):
    """各组学分均值与标准差对比"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    valid = stats_df[stats_df['course_count'] > 0].copy()
    groups_str = valid['group_no'].astype(str)
    colors = get_group_colors(valid)

    # 学分均值
    ax = axes[0]
    bars = ax.bar(groups_str, valid['credit_mean'], color=colors,
                  alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5, label=L('参考值 3', 'Ref: 3'))
    ax.set_title(L('各组平均学分对比', 'Average Credit by Group'),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('平均学分', 'Average Credit'))
    ax.tick_params(axis='x', rotation=45)
    for bar, val in zip(bars, valid['credit_mean']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{val:.1f}', ha='center', fontsize=7, fontweight='bold')

    # 学分标准差
    ax = axes[1]
    bars = ax.bar(groups_str, valid['credit_std'], color=colors,
                  alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.set_title(L('各组学分标准差对比', 'Credit Std Dev by Group'),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('学分标准差', 'Credit Std Dev'))
    ax.tick_params(axis='x', rotation=45)
    for bar, val in zip(bars, valid['credit_std']):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.2f}', ha='center', fontsize=7, fontweight='bold')

    fig.suptitle(L('各组学分设计对比分析', 'Credit Distribution Analysis by Group'),
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    return save_figure(fig, 'fig_v10_credit_distribution.png')


# ---- 图11: 各组成绩缺失与分布 ----
def plot_score_analysis(sc, stats_df):
    """成绩缺失率 + 有成绩组的成绩分布"""
    fig, axes = plt.subplots(1, 2, figsize=(17, 6))

    valid = stats_df[stats_df['sc_count'] > 0].copy()

    # 成绩非空率
    ax = axes[0]
    colors_score = []
    for _, row in valid.iterrows():
        if row['score_non_null_ratio'] == 0:
            colors_score.append(COLOR_ANOMALY)
        elif row['score_non_null_ratio'] < 1:
            colors_score.append(COLOR_WARN)
        else:
            colors_score.append(COLOR_NORMAL)

    bars = ax.bar(valid['group_no'].astype(str), valid['score_non_null_ratio'] * 100,
                  color=colors_score, alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.set_title(L('各组成绩非空率', 'Score Non-Null Rate by Group'),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('成绩非空率 (%)', 'Score Non-Null Rate (%)'))
    ax.set_ylim(0, 115)
    ax.tick_params(axis='x', rotation=45)
    for bar, val in zip(bars, valid['score_non_null_ratio']):
        label = f'{val*100:.0f}%'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                label, ha='center', fontsize=7, fontweight='bold')

    # 图例
    legend_elements = [
        Patch(facecolor=COLOR_NORMAL, label=L('全部有成绩', 'All Scored')),
        Patch(facecolor=COLOR_WARN, label=L('部分缺失', 'Partial Null')),
        Patch(facecolor=COLOR_ANOMALY, label=L('全部缺失', 'All Null')),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc='upper right')

    # 有成绩的组 — 成绩均值与范围
    ax = axes[1]
    scored_groups = valid[valid['score_non_null_ratio'] > 0].copy()
    if len(scored_groups) > 0:
        # 计算每组成绩的统计
        score_stats = []
        for g in scored_groups['group_no']:
            g_sc = sc[(sc['group_no'] == g) & (sc['score'].notna())]
            if len(g_sc) > 0:
                score_stats.append({
                    'group_no': int(g),
                    'mean': g_sc['score'].mean(),
                    'std': g_sc['score'].std(),
                    'min': g_sc['score'].min(),
                    'max': g_sc['score'].max(),
                })
        ss_df = pd.DataFrame(score_stats)

        if len(ss_df) > 0:
            x = np.arange(len(ss_df))
            colors_ss = get_group_colors(ss_df, None)
            # 均值+误差棒
            ax.errorbar(x, ss_df['mean'], yerr=ss_df['std'], fmt='o',
                        color='#2c3e50', capsize=4, markersize=8, linewidth=1.5,
                        label=L('均值±标准差', 'Mean±Std'), alpha=0.7)
            # 范围
            ax.vlines(x, ss_df['min'], ss_df['max'], colors=colors_ss,
                      linewidth=3, alpha=0.5, label=L('最小-最大范围', 'Min-Max Range'))
            ax.scatter(x, ss_df['mean'], c=colors_ss, s=80, zorder=5, edgecolors='white', linewidth=1)

            ax.set_xticks(x)
            ax.set_xticklabels(ss_df['group_no'].astype(str), rotation=45)
            ax.set_title(L('各组成绩分布 (均值与范围)', 'Score Distribution by Group (Mean & Range)'),
                         fontsize=13, fontweight='bold')
            ax.set_xlabel(L('组号', 'Group No.'))
            ax.set_ylabel(L('成绩', 'Score'))
            ax.legend(fontsize=8)
            ax.axhline(y=60, color='gray', linestyle='--', alpha=0.3)

    fig.suptitle(L('各组成绩数据质量与分布分析', 'Score Data Quality & Distribution'),
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    return save_figure(fig, 'fig_v11_score_analysis.png')


# ---- 图12: 各组数据异常评分总览 ----
def plot_anomaly_overview(stats_df):
    """各组异常评分总览仪表盘"""
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    valid = stats_df.copy()
    colors = []
    for _, row in valid.iterrows():
        if row['anomaly_score'] >= 3:
            colors.append(COLOR_ANOMALY)
        elif row['anomaly_score'] >= 1:
            colors.append(COLOR_WARN)
        elif row['group_no'] == OWN_GROUP:
            colors.append(COLOR_OWN)
        else:
            colors.append(COLOR_NORMAL)

    # 异常评分柱状图
    ax = axes[0]
    bars = ax.bar(valid['group_no'].astype(str), valid['anomaly_score'],
                  color=colors, alpha=0.88, edgecolor='white', linewidth=0.5)
    ax.set_title(L('各组数据异常评分', 'Anomaly Score by Group'),
                 fontsize=13, fontweight='bold')
    ax.set_xlabel(L('组号', 'Group No.'))
    ax.set_ylabel(L('异常评分', 'Anomaly Score'))
    ax.tick_params(axis='x', rotation=45)
    for bar, val in zip(bars, valid['anomaly_score']):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                    str(int(val)), ha='center', fontsize=8, fontweight='bold')

    legend_elements = [
        Patch(facecolor=COLOR_NORMAL, label=L('正常 (0分)', 'Normal (0)')),
        Patch(facecolor=COLOR_WARN, label=L('轻微异常 (1-2分)', 'Minor (1-2)')),
        Patch(facecolor=COLOR_ANOMALY, label=L('严重异常 (≥3分)', 'Severe (≥3)')),
        Patch(facecolor=COLOR_OWN, label=L('本组', 'Own Group')),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc='upper left')

    # 数据完整度饼图
    ax = axes[1]
    completeness_counts = valid['completeness'].value_counts().sort_index()
    labels_map = {
        0: L('无数据', 'No Tables'),
        1: L('仅1张表', '1 Table'),
        2: L('2张表', '2 Tables'),
        3: L('三表齐全', 'All 3 Tables'),
    }
    labels = [labels_map.get(k, str(k)) for k in completeness_counts.index]
    colors_pie = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    explode = [0.05] * len(completeness_counts)

    wedges, texts, autotexts = ax.pie(
        completeness_counts.values, explode=explode,
        labels=labels, colors=colors_pie[:len(completeness_counts)],
        autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 10}
    )
    for at in autotexts:
        at.set_fontweight('bold')
        at.set_fontsize(11)
    ax.set_title(L('各组数据完整度分布', 'Data Completeness Distribution'),
                 fontsize=13, fontweight='bold')

    fig.suptitle(L('数据异常与完整度总览', 'Data Anomaly & Completeness Overview'),
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    return save_figure(fig, 'fig_v12_anomaly_overview.png')


# ---- 图13: 各组综合特征画像热力图 ----
def plot_feature_heatmap(stats_df):
    """各组特征标准化后的热力图"""
    # 选择特征
    feature_cols = [
        'student_count', 'course_count', 'sc_count', 'sc_per_student',
        'share_ratio', 'male_ratio', 'credit_mean',
        'sid_mean_len', 'cid_mean_len', 'score_non_null_ratio',
    ]
    feature_labels_cn = [
        '学生数', '课程数', '选课数', '人均选课',
        '共享率', '男生率', '学分均值',
        '学号长度', '课程号长度', '成绩非空率',
    ]
    feature_labels_en = [
        'Students', 'Courses', 'SC', 'SC/Stu',
        'Share', 'Male%', 'Credit',
        'SID Len', 'CID Len', 'Score%',
    ]

    # 筛选可分析组
    valid = stats_df[
        (stats_df['student_count'] > 0) &
        (~stats_df['group_no'].isin(EXCLUDED_GROUPS))
    ].copy()

    matrix = valid[feature_cols].copy()
    # 标准化
    for col in matrix.columns:
        col_min = matrix[col].min()
        col_max = matrix[col].max()
        if col_max > col_min:
            matrix[col] = (matrix[col] - col_min) / (col_max - col_min)
        else:
            matrix[col] = 0.5

    fig, ax = plt.subplots(figsize=(16, 10))
    matrix_t = matrix.set_index(valid['group_no'].astype(int)).T

    feature_labels = feature_labels_cn if USE_CN else feature_labels_en
    matrix_t.index = feature_labels

    sns.heatmap(matrix_t, annot=True, fmt='.2f', cmap='YlOrRd',
                linewidths=0.5, linecolor='white', ax=ax,
                cbar_kws={'label': L('归一化值', 'Normalized Value'), 'shrink': 0.8})

    # 高亮本组列
    if OWN_GROUP in valid['group_no'].values:
        own_col_idx = list(valid['group_no']).index(OWN_GROUP)
        for i in range(len(feature_labels)):
            ax.add_patch(plt.Rectangle((own_col_idx, i), 1, 1,
                                       fill=False, edgecolor=COLOR_OWN, lw=3))

    ax.set_title(L('各组特征画像热力图（归一化对比）',
                   'Group Feature Profile Heatmap (Normalized)'),
                 fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel(L('组号', 'Group No.'), fontsize=11)
    plt.tight_layout()
    return save_figure(fig, 'fig_v13_feature_heatmap.png')


# ---- 图14: 各组数据规模气泡图 ----
def plot_scale_bubble(stats_df, most_similar):
    """学生数 vs 课程数 气泡图（气泡大小=选课数）"""
    valid = stats_df[stats_df['student_count'] > 0].copy()

    fig, ax = plt.subplots(figsize=(14, 8))

    # 缩放气泡大小
    bubble_size = np.sqrt(valid['sc_count']) * 15

    colors = get_group_colors(valid, most_similar)

    scatter = ax.scatter(valid['student_count'], valid['course_count'],
                         s=bubble_size, c=colors, alpha=0.75,
                         edgecolors='white', linewidth=1.5)

    # 标注组号
    for _, row in valid.iterrows():
        g = int(row['group_no'])
        fontweight = 'bold' if g == OWN_GROUP else 'normal'
        fontsize = 10 if g == OWN_GROUP else 7
        color = 'black' if g == OWN_GROUP else '#555555'
        ax.annotate(str(g), (row['student_count'], row['course_count']),
                    fontsize=fontsize, fontweight=fontweight, color=color,
                    ha='center', va='center')

    # 标注本组
    own = valid[valid['group_no'] == OWN_GROUP]
    if len(own) > 0:
        ax.annotate(L(f'← 本组 ({int(own.iloc[0]["student_count"])}学生, '
                      f'{int(own.iloc[0]["course_count"])}课程, '
                      f'{int(own.iloc[0]["sc_count"])}选课)',
                      f'← Own ({int(own.iloc[0]["student_count"])}S, '
                      f'{int(own.iloc[0]["course_count"])}C, '
                      f'{int(own.iloc[0]["sc_count"])}SC)'),
                    xy=(own.iloc[0]['student_count'], own.iloc[0]['course_count']),
                    xytext=(own.iloc[0]['student_count'] + 20, own.iloc[0]['course_count'] + 5),
                    fontsize=10, fontweight='bold', color=COLOR_OWN,
                    arrowprops=dict(arrowstyle='->', color=COLOR_OWN, lw=2))

    ax.set_title(L('各组数据规模气泡图 (气泡大小=选课数)',
                   'Group Scale Bubble Chart (Size=SC Count)'),
                 fontsize=15, fontweight='bold')
    ax.set_xlabel(L('学生数', 'Student Count'), fontsize=11)
    ax.set_ylabel(L('课程数', 'Course Count'), fontsize=11)

    # 图例
    legend_elements = [
        Patch(facecolor=COLOR_OWN, label=L(f'本组 (G{OWN_GROUP})', f'Own (G{OWN_GROUP})')),
        Patch(facecolor=COLOR_OTHER, label=L('其他组', 'Others')),
    ]
    if most_similar:
        legend_elements.insert(1, Patch(facecolor=COLOR_SIMILAR,
                                        label=L(f'最相似组 (G{most_similar})',
                                                f'Most Similar (G{most_similar})')))
    ax.legend(handles=legend_elements, fontsize=9, loc='lower right')
    plt.tight_layout()
    return save_figure(fig, 'fig_v14_scale_bubble.png')


# ============================================================
# 图表目录生成
# ============================================================
def generate_chart_catalog(figures_generated):
    """生成图表标题与说明清单"""
    print(L("\n📋 生成图表目录...", "\n[INFO] Generating chart catalog..."))

    chart_descriptions = [
        {
            'id': 'fig_v1_scale_dashboard',
            'title_cn': '各组数据规模全景对比',
            'title_en': 'Group Data Scale Overview Dashboard',
            'type': '2×2子图仪表盘（柱状图）',
            'description_cn': '四合一对比图，展示各组学生数、课程数、选课记录数及人均选课数。'
                              '绿色为本组(16)，橙色为最相似组，蓝色为其他组，灰色为不完整组。'
                              '灰色虚线标注参考值（150学生/30课程/750选课/人均5门）。',
            'description_en': '2×2 dashboard comparing student count, course count, '
                             'SC record count, and SC per student across all groups.',
            'category': '规模对比',
        },
        {
            'id': 'fig_v2_dept_distribution',
            'title_cn': '各组院系数据分布对比',
            'title_en': 'Department Distribution by Group',
            'type': '堆叠柱状图',
            'description_cn': '左右两图分别展示各组学生和课程在A/B/C三个院系的分布情况。'
                              '蓝色=A院，红色=B院，绿色=C院。本组位置用虚线标注。',
            'description_en': 'Stacked bar charts showing student and course distribution '
                             'across departments A/B/C for each group.',
            'category': '结构特征',
        },
        {
            'id': 'fig_v3_share_ratio',
            'title_cn': '各组共享课程比例对比',
            'title_en': 'Shared Course Ratio by Group',
            'type': '水平条形图',
            'description_cn': '展示各组的共享课程(Y标志)占比。虚线标注本组共享率水平。'
                              '大部分组共享率维持在~70%左右。',
            'description_en': 'Horizontal bar chart showing the proportion of shared courses '
                             '(Y flag) per group.',
            'category': '共享特征',
        },
        {
            'id': 'fig_v4_gender_ratio',
            'title_cn': '各组学生性别比例对比',
            'title_en': 'Gender Ratio by Group',
            'type': '分组条形图',
            'description_cn': '蓝色=男生比例，红色=女生比例。本组柱子有加粗边框和箭头标注。'
                              '大部分组男女比例接近1:1。',
            'description_en': 'Grouped bar chart showing male (blue) and female (red) ratio '
                             'per group. Own group highlighted.',
            'category': '性别特征',
        },
        {
            'id': 'fig_v5_gender_pie',
            'title_cn': '各组男女比例饼图',
            'title_en': 'Gender Ratio Pie Charts',
            'type': '多饼图阵列',
            'description_cn': '选取代表性组（含本组）绘制的男女性别比例饼图，直观展示性别均衡程度。',
            'description_en': 'Pie chart array for selected groups showing male/female split.',
            'category': '性别特征',
        },
        {
            'id': 'fig_v6_similarity_heatmap',
            'title_cn': '组间综合相似度热力图',
            'title_en': 'Inter-Group Similarity Heatmap',
            'type': '热力图',
            'description_cn': '基于余弦相似度+欧氏距离（各50%权重）计算的组间综合相似度矩阵。'
                              '颜色越深(绿)=越相似。对角线为本组自身(恒为1)。',
            'description_en': 'Heatmap of combined similarity (cosine 50% + euclidean 50%). '
                             'Greener = more similar.',
            'category': '相似度分析',
        },
        {
            'id': 'fig_v7_radar_comparison',
            'title_cn': '本组与最相似组多维特征雷达图',
            'title_en': 'Radar Chart: Own vs Most Similar Group',
            'type': '雷达图/蜘蛛图',
            'description_cn': '8维特征雷达图对比本组(绿色)与最相似组(橙色)。'
                              '维度包括：学生数、课程数、人均选课、共享率、男生率、平均学分、成绩非空率、学号长度。'
                              '所有值归一化到[0,1]以便比较。',
            'description_en': '8-dimension radar chart comparing own group (green) with '
                             'most similar group (orange).',
            'category': '相似度分析',
        },
        {
            'id': 'fig_v8_similarity_ranking',
            'title_cn': '各组与本组的相似度排名',
            'title_en': 'Similarity Ranking to Own Group',
            'type': '水平条形图',
            'description_cn': '各组与本组(16)的综合相似度降序排列。橙色=最相似组。'
                              '图中标注了最高相似度的组及具体数值。',
            'description_en': 'Horizontal bar chart ranking groups by combined similarity '
                             'to own group.',
            'category': '相似度分析',
        },
        {
            'id': 'fig_v9_id_format',
            'title_cn': '各组ID编码格式差异分析',
            'title_en': 'Group ID Format Difference Analysis',
            'type': '箱线图',
            'description_cn': '上图：各组学号长度分布箱线图。下图：各组课程编号长度分布箱线图。'
                              '绿色=本组。不同组之间编码长度和离散程度差异显著。',
            'description_en': 'Box plots of student ID length (top) and course ID length '
                             '(bottom) by group.',
            'category': '格式特征',
        },
        {
            'id': 'fig_v10_credit_distribution',
            'title_cn': '各组学分设计对比分析',
            'title_en': 'Credit Distribution Analysis by Group',
            'type': '柱状图',
            'description_cn': '左图：各组平均学分对比（虚线标注3学分参考值）。'
                              '右图：各组学分标准差对比（反映学分设计多样性）。',
            'description_en': 'Average credit (left) and credit std dev (right) by group.',
            'category': '内容特征',
        },
        {
            'id': 'fig_v11_score_analysis',
            'title_cn': '各组成绩数据质量与分布分析',
            'title_en': 'Score Data Quality & Distribution',
            'type': '组合图（柱状图+误差线）',
            'description_cn': '左图：各组成绩非空率（绿=全部有成绩，黄=部分缺失，红=全部缺失）。'
                              '右图：有成绩组的成绩均值±标准差及最小-最大范围。',
            'description_en': 'Score availability rate (left) and score distribution with '
                             'mean/std/range for scored groups (right).',
            'category': '成绩特征',
        },
        {
            'id': 'fig_v12_anomaly_overview',
            'title_cn': '数据异常与完整度总览',
            'title_en': 'Data Anomaly & Completeness Overview',
            'type': '组合图（柱状图+饼图）',
            'description_cn': '左图：各组综合异常评分（基于数据完整性、规模偏差、成绩缺失等）。'
                              '右图：各组数据完整度分布饼图（三表齐全/仅两张表/仅一张表）。',
            'description_en': 'Anomaly score bar chart + data completeness pie chart.',
            'category': '异常检测',
        },
        {
            'id': 'fig_v13_feature_heatmap',
            'title_cn': '各组综合特征画像热力图',
            'title_en': 'Group Feature Profile Heatmap',
            'type': '热力图',
            'description_cn': '10维特征归一化热力图，行=特征，列=组。绿色框=本组。'
                              '可直观比较各组在所有维度上的相对位置。',
            'description_en': 'Normalized feature heatmap with 10 dimensions across all '
                             'analyzable groups.',
            'category': '综合分析',
        },
        {
            'id': 'fig_v14_scale_bubble',
            'title_cn': '各组数据规模气泡图',
            'title_en': 'Group Scale Bubble Chart',
            'type': '气泡散点图',
            'description_cn': 'X轴=学生数，Y轴=课程数，气泡大小=选课数。'
                              '直观展示各组的三维规模关系，本组用箭头标注。',
            'description_en': 'Bubble scatter plot: students vs courses, bubble size = SC count.',
            'category': '综合分析',
        },
    ]

    # 生成Markdown
    lines = []
    lines.append("# 📊 数据可视化图表目录")
    lines.append("")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> 生成脚本: `visualization.py` (成员5)")
    lines.append(f"> 图表数量: {len(chart_descriptions)} 张")
    lines.append(f"> 输出目录: `analysis/figures/`")
    lines.append(f"> 格式: PNG, 300dpi")
    lines.append(f"> 中文字体: {CN_FONT if CN_FONT else '未找到（使用英文）'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 按类别分组
    lines.append("## 图表分类索引")
    lines.append("")
    categories = {}
    for cd in chart_descriptions:
        cat = cd['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(cd)

    for cat, items in categories.items():
        lines.append(f"### {cat} ({len(items)}张)")
        lines.append("")
        lines.append("| 编号 | 标题 | 类型 |")
        lines.append("|------|------|------|")
        for cd in items:
            title = cd['title_cn'] if USE_CN else cd['title_en']
            lines.append(f"| {cd['id']} | {title} | {cd['type']} |")
        lines.append("")

    lines.append("---")
    lines.append("")

    # 详细描述
    lines.append("## 图表详细说明")
    lines.append("")
    for i, cd in enumerate(chart_descriptions, 1):
        title = cd['title_cn'] if USE_CN else cd['title_en']
        desc = cd['description_cn'] if USE_CN else cd['description_en']
        lines.append(f"### {i}. {title}")
        lines.append("")
        lines.append(f"- **文件**: `{cd['id']}.png`")
        lines.append(f"- **类型**: {cd['type']}")
        lines.append(f"- **类别**: {cd['category']}")
        lines.append(f"- **说明**: {desc}")
        lines.append("")

    # 配色说明
    lines.append("---")
    lines.append("")
    lines.append("## 统一配色方案")
    lines.append("")
    lines.append("| 颜色 | 色值 | 用途 |")
    lines.append("|------|------|------|")
    lines.append(f"| 🟢 翠绿 | `{COLOR_OWN}` | 本组(16)标识 |")
    lines.append(f"| 🟠 橙色 | `{COLOR_SIMILAR}` | 最相似组标识 |")
    lines.append(f"| 🔵 浅蓝 | `{COLOR_OTHER}` | 其他正常组 |")
    lines.append(f"| 🔴 红色 | `{COLOR_ANOMALY}` | 异常/严重问题 |")
    lines.append(f"| 🟡 黄色 | `{COLOR_WARN}` | 轻微异常/警告 |")
    lines.append(f"| ⚪ 灰色 | `#bdc3c7` | 数据不完整组 |")
    lines.append("")
    lines.append("| 院系 | 颜色 | 色值 |")
    lines.append("|------|------|------|")
    lines.append(f"| A院 | 🔵 蓝色 | `{DEPT_COLORS['A']}` |")
    lines.append(f"| B院 | 🔴 红色 | `{DEPT_COLORS['B']}` |")
    lines.append(f"| C院 | 🟢 绿色 | `{DEPT_COLORS['C']}` |")
    lines.append("")

    # 使用说明
    lines.append("---")
    lines.append("")
    lines.append("## 使用说明")
    lines.append("")
    lines.append("### 运行方式")
    lines.append("")
    lines.append("```bash")
    lines.append("cd analysis/")
    lines.append("python visualization.py")
    lines.append("```")
    lines.append("")
    lines.append("### 依赖")
    lines.append("")
    lines.append("- pandas, numpy — 数据处理")
    lines.append("- matplotlib, seaborn — 可视化")
    lines.append("- scikit-learn — 相似度计算（可选，不影响基础图表）")
    lines.append("")
    lines.append("### 输入数据")
    lines.append("")
    lines.append("- `data/cleaned/students_cleaned.csv`")
    lines.append("- `data/cleaned/courses_cleaned.csv`")
    lines.append("- `data/cleaned/sc_cleaned.csv`")
    lines.append("")
    lines.append("### 输出")
    lines.append("")
    lines.append(f"- {len(chart_descriptions)} 张 PNG 图表 → `analysis/figures/`")
    lines.append("- 本目录文件 → `analysis/charts_catalog.md`")
    lines.append("")

    catalog_text = "\n".join(lines)
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        f.write(catalog_text)

    print(f"  ✅ 图表目录已保存: {CATALOG_PATH}")
    return catalog_text


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 70)
    print(L("  📊 数据可视化脚本 - 作业四 成员5",
            "  Data Visualization Script - HW4 Member 5"))
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    ensure_dir(FIGURES_DIR)

    # 1. 加载数据
    students, courses, sc = load_data()

    # 2. 计算统计指标
    stats_df, all_groups = compute_group_stats(students, courses, sc)

    # 3. 计算相似度
    similarity_result = compute_similarity(stats_df)
    if similarity_result[0] is not None:
        combined_df, cos_sim, sim_ranking_df, most_similar, group_nos, feature_scaled, analyzable = similarity_result
    else:
        combined_df = None
        sim_ranking_df = None
        most_similar = None

    # 打印本组概览
    print("\n" + "=" * 70)
    print(L(f"  📋 本组(组{OWN_GROUP})概览", f"  Group {OWN_GROUP} Overview"))
    print("=" * 70)
    own_row = stats_df[stats_df['group_no'] == OWN_GROUP]
    if len(own_row) > 0:
        r = own_row.iloc[0]
        print(f"  学生数: {int(r['student_count'])}  课程数: {int(r['course_count'])}  "
              f"选课数: {int(r['sc_count'])}")
        print(f"  人均选课: {r['sc_per_student']}  共享率: {r['share_ratio']*100:.0f}%  "
              f"男生率: {r['male_ratio']*100:.0f}%")
        print(f"  学分均值: {r['credit_mean']}  成绩非空率: {r['score_non_null_ratio']*100:.0f}%")
        print(f"  学号平均长度: {r['sid_mean_len']}  课程号平均长度: {r['cid_mean_len']}")
        print(f"  异常评分: {int(r['anomaly_score'])}  "
              f"数据完整度: {int(r['completeness'])}/3")
    if most_similar:
        print(f"\n  最相似组: 组{most_similar}")
        print(f"  Top 3 相似组: ", end="")
        if sim_ranking_df is not None:
            top3 = sim_ranking_df.head(3)['group_no'].astype(int).tolist()
            print(f"{top3}")

    # 4. 生成所有图表
    print("\n" + "=" * 70)
    print(L("  🎨 生成可视化图表...", "  Generating visualization charts..."))
    print("=" * 70)

    figures_generated = []

    # 图1: 数据规模仪表盘
    figures_generated.append(plot_scale_dashboard(stats_df, most_similar))

    # 图2: 院系分布
    figures_generated.append(plot_dept_distribution(stats_df, most_similar))

    # 图3: 共享课程比例
    figures_generated.append(plot_share_ratio(stats_df, most_similar))

    # 图4: 男女比例分组条形图
    figures_generated.append(plot_gender_ratio(stats_df, most_similar))

    # 图5: 男女比例饼图
    figures_generated.append(plot_gender_pie_grid(stats_df))

    # 图6: 相似度热力图
    figures_generated.append(plot_similarity_heatmap(combined_df, most_similar))

    # 图7: 雷达图
    figures_generated.append(plot_radar_comparison(stats_df, most_similar))

    # 图8: 相似度排名
    figures_generated.append(plot_similarity_ranking(sim_ranking_df, most_similar))

    # 图9: ID格式对比
    figures_generated.append(plot_id_format_comparison(students, courses))

    # 图10: 学分分布
    figures_generated.append(plot_credit_distribution(courses, stats_df))

    # 图11: 成绩分析
    figures_generated.append(plot_score_analysis(sc, stats_df))

    # 图12: 异常评分总览
    figures_generated.append(plot_anomaly_overview(stats_df))

    # 图13: 特征画像热力图
    figures_generated.append(plot_feature_heatmap(stats_df))

    # 图14: 规模气泡图
    figures_generated.append(plot_scale_bubble(stats_df, most_similar))

    # 过滤None
    figures_generated = [f for f in figures_generated if f is not None]

    # 5. 生成图表目录
    print("\n" + "=" * 70)
    generate_chart_catalog(figures_generated)

    # 6. 完成
    print("\n" + "=" * 70)
    print(L("  ✅ 可视化脚本执行完成！", "  Visualization Complete!"))
    print(f"  - {len(figures_generated)} 张图表 → {FIGURES_DIR}/")
    print(f"  - 图表目录 → {CATALOG_PATH}")
    print(f"  - 所有图表 300dpi PNG 格式，可直接用于报告和PPT")
    print("=" * 70)


if __name__ == "__main__":
    main()
