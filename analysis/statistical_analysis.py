#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计分析与相似度计算脚本 - 作业四 成员4

职责：
  1. 计算各组核心统计指标（学生数、课程数、选课数、共享比、性别比、学分分布、学号编码特征）
  2. 构建多维特征向量，对每组进行特征画像
  3. 设计相似度计算方法（余弦相似度、欧氏距离），计算组间相似度矩阵
  4. 找到与本组（16号）最相似的组，分析相似原因
  5. 拓展：聚类分析（K-Means / Hierarchical），发现组的自然分类

输出：
  - 可视化图表（保存至 figures/）
  - 最相似组分析报告（保存至 similarity_report.md）
"""

import os
# 修复 Windows 上 threadpoolctl 的已知问题：monkey-patch _ThreadpoolInfo
import threadpoolctl as _tpctl
_orig_init = _tpctl._ThreadpoolInfo.__init__
def _safe_init(self, *, prefixes=None, user_api=None, modules=None):
    try:
        _orig_init(self, prefixes=prefixes, user_api=user_api, modules=modules)
    except AttributeError:
        self._prefixes = prefixes
        self._user_api = user_api
        self._modules = []
_tpctl._ThreadpoolInfo.__init__ = _safe_init

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import re
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.cluster import KMeans, AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform

# ============================================================
# 全局设置
# ============================================================
DATA_DIR = './data'
CLEANED_DIR = os.path.join(DATA_DIR, 'cleaned')
FIGURES_DIR = './figures'
REPORT_PATH = './similarity_report.md'

# Use English labels to avoid CJK font rendering issues
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# 本组组号
OWN_GROUP = 16

# 不完整组（异常检测报告中标记的）
EXCLUDED_GROUPS = {9, 19, 25}  # 缺少关键表的组


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def load_data():
    """加载清洗后的数据"""
    print("=" * 70)
    print("加载数据...")
    students = pd.read_csv(os.path.join(CLEANED_DIR, 'students_cleaned.csv'))
    courses = pd.read_csv(os.path.join(CLEANED_DIR, 'courses_cleaned.csv'))
    sc = pd.read_csv(os.path.join(CLEANED_DIR, 'sc_cleaned.csv'))

    print(f"  学生表: {len(students)} 条")
    print(f"  课程表: {len(courses)} 条")
    print(f"  选课表: {len(sc)} 条")

    return students, courses, sc


# ============================================================
# 1. 计算各组核心统计指标
# ============================================================
def compute_group_statistics(students, courses, sc):
    """
    计算各组核心统计指标，返回一个 DataFrame，每行一个组。
    指标涵盖：规模特征、结构特征、内容特征、共享特征、性别特征、成绩特征。
    """
    print("\n" + "=" * 70)
    print("1. 计算各组核心统计指标")
    print("=" * 70)

    # 只分析三表齐全的组
    s_groups = set(students['group_no'].unique())
    c_groups = set(courses['group_no'].unique())
    sc_groups = set(sc['group_no'].unique())
    full_groups = sorted(s_groups & c_groups & sc_groups)

    # 排除不完整组
    full_groups = [g for g in full_groups if g not in EXCLUDED_GROUPS]

    print(f"  三表齐全且可分析的组: {len(full_groups)} 个 — {full_groups}")

    records = []
    for g in full_groups:
        g_s = students[students['group_no'] == g]
        g_c = courses[courses['group_no'] == g]
        g_sc = sc[sc['group_no'] == g]

        # ---- 规模特征 ----
        student_count = len(g_s)
        course_count = len(g_c)
        sc_count = len(g_sc)
        sc_per_student = sc_count / student_count if student_count > 0 else 0
        course_per_student = course_count / student_count if student_count > 0 else 0

        # ---- 结构特征：各院系分布比例 ----
        s_dept_counts = g_s['dept_no'].value_counts()
        c_dept_counts = g_c['dept_no'].value_counts()
        s_dept_A_ratio = s_dept_counts.get('A', 0) / student_count if student_count > 0 else 0
        s_dept_B_ratio = s_dept_counts.get('B', 0) / student_count if student_count > 0 else 0
        s_dept_C_ratio = s_dept_counts.get('C', 0) / student_count if student_count > 0 else 0
        c_dept_A_ratio = c_dept_counts.get('A', 0) / course_count if course_count > 0 else 0
        c_dept_B_ratio = c_dept_counts.get('B', 0) / course_count if course_count > 0 else 0
        c_dept_C_ratio = c_dept_counts.get('C', 0) / course_count if course_count > 0 else 0

        # 院系数（学生表覆盖的院系数量）
        s_dept_n = g_s['dept_no'].nunique()
        c_dept_n = g_c['dept_no'].nunique()

        # ---- 内容特征：学号编码模式 ----
        sid_samples = g_s['student_id'].astype(str)
        sid_mean_len = sid_samples.str.len().mean()

        # 学号前缀模式：提取首字母前缀
        sid_prefixes = sid_samples.str.extract(r'^([A-Za-z]*)')[0]
        # 判断学号是否以数字开头
        sid_starts_with_digit = sid_samples.str.match(r'^\d').mean()

        # 课程编号模式
        cid_samples = g_c['course_id'].astype(str)
        cid_mean_len = cid_samples.str.len().mean()
        cid_starts_with_digit = cid_samples.str.match(r'^\d').mean()

        # 学分分布
        credit_mean = g_c['credit'].mean() if 'credit' in g_c.columns else 0
        credit_std = g_c['credit'].std() if 'credit' in g_c.columns else 0
        credit_median = g_c['credit'].median() if 'credit' in g_c.columns else 0
        credit_nunique = g_c['credit'].nunique() if 'credit' in g_c.columns else 0

        # ---- 共享特征 ----
        if 'share_flag' in g_c.columns:
            share_y_count = (g_c['share_flag'] == 'Y').sum()
            share_flag_total = g_c['share_flag'].isin(['Y', 'N']).sum()
            share_ratio = share_y_count / share_flag_total if share_flag_total > 0 else 0
            # 各院共享比例
            share_by_dept = {}
            for dept in ['A', 'B', 'C']:
                dept_courses = g_c[g_c['dept_no'] == dept]
                dept_total = dept_courses['share_flag'].isin(['Y', 'N']).sum()
                dept_share_y = (dept_courses['share_flag'] == 'Y').sum()
                share_by_dept[f'share_ratio_dept_{dept}'] = dept_share_y / dept_total if dept_total > 0 else 0
        else:
            share_ratio = 0
            share_by_dept = {f'share_ratio_dept_{d}': 0 for d in ['A', 'B', 'C']}

        # ---- 性别特征 ----
        if 'gender' in g_s.columns:
            gender_counts = g_s['gender'].value_counts()
            male_count = gender_counts.get('M', 0)
            female_count = gender_counts.get('F', 0)
            gender_total = male_count + female_count
            male_ratio = male_count / gender_total if gender_total > 0 else 0.5
            # 各院男女比
            male_ratio_by_dept = {}
            for dept in ['A', 'B', 'C']:
                dept_s = g_s[g_s['dept_no'] == dept]
                dept_m = (dept_s['gender'] == 'M').sum()
                dept_f = (dept_s['gender'] == 'F').sum()
                dept_total = dept_m + dept_f
                male_ratio_by_dept[f'male_ratio_dept_{dept}'] = dept_m / dept_total if dept_total > 0 else 0.5
        else:
            male_ratio = 0.5
            male_ratio_by_dept = {f'male_ratio_dept_{d}': 0.5 for d in ['A', 'B', 'C']}

        # ---- 成绩特征 ----
        if 'score' in g_sc.columns:
            non_null_scores = g_sc['score'].dropna()
            score_non_null_ratio = len(non_null_scores) / len(g_sc) if len(g_sc) > 0 else 0
            score_mean = non_null_scores.mean() if len(non_null_scores) > 0 else np.nan
            score_std = non_null_scores.std() if len(non_null_scores) > 0 else np.nan
            score_min = non_null_scores.min() if len(non_null_scores) > 0 else np.nan
            score_max = non_null_scores.max() if len(non_null_scores) > 0 else np.nan

            # 检查成绩是否全0
            if len(non_null_scores) > 0 and (non_null_scores == 0).all():
                score_all_zero = 1
            else:
                score_all_zero = 0
        else:
            score_non_null_ratio = 0
            score_mean = np.nan
            score_std = np.nan
            score_min = np.nan
            score_max = np.nan
            score_all_zero = 0

        rec = {
            'group_no': g,
            # 规模
            'student_count': student_count,
            'course_count': course_count,
            'sc_count': sc_count,
            'sc_per_student': round(sc_per_student, 2),
            'course_per_student': round(course_per_student, 3),
            # 结构
            's_dept_A_ratio': round(s_dept_A_ratio, 3),
            's_dept_B_ratio': round(s_dept_B_ratio, 3),
            's_dept_C_ratio': round(s_dept_C_ratio, 3),
            'c_dept_A_ratio': round(c_dept_A_ratio, 3),
            'c_dept_B_ratio': round(c_dept_B_ratio, 3),
            'c_dept_C_ratio': round(c_dept_C_ratio, 3),
            's_dept_n': s_dept_n,
            'c_dept_n': c_dept_n,
            # 内容
            'sid_mean_len': round(sid_mean_len, 1),
            'sid_starts_with_digit': round(sid_starts_with_digit, 3),
            'cid_mean_len': round(cid_mean_len, 1),
            'cid_starts_with_digit': round(cid_starts_with_digit, 3),
            'credit_mean': round(credit_mean, 2),
            'credit_std': round(credit_std, 2) if not np.isnan(credit_std) else 0,
            'credit_nunique': credit_nunique,
            # 共享
            'share_ratio': round(share_ratio, 3),
            **share_by_dept,
            # 性别
            'male_ratio': round(male_ratio, 3),
            **male_ratio_by_dept,
            # 成绩
            'score_non_null_ratio': round(score_non_null_ratio, 3),
            'score_mean': round(score_mean, 2) if not np.isnan(score_mean) else np.nan,
            'score_std': round(score_std, 2) if not np.isnan(score_std) else np.nan,
            'score_all_zero': score_all_zero,
        }
        records.append(rec)

    stats_df = pd.DataFrame(records)
    print(f"  统计指标计算完成，共 {len(stats_df)} 个组，{len(stats_df.columns)-1} 个指标")

    # 打印本组概览
    own = stats_df[stats_df['group_no'] == OWN_GROUP]
    if len(own) > 0:
        print(f"\n  本组({OWN_GROUP})概览:")
        for col in ['student_count', 'course_count', 'sc_count', 'sc_per_student',
                     'share_ratio', 'male_ratio', 'credit_mean', 'score_non_null_ratio']:
            val = own[col].values[0]
            print(f"    {col}: {val}")

    return stats_df


# ============================================================
# 2. 构建特征向量与特征画像
# ============================================================
def build_feature_vectors(stats_df):
    """
    从统计指标中选取合适特征构建特征向量，用于相似度计算。
    需要处理：
      - 量纲归一化（StandardScaler）
      - 成绩缺失组的成绩特征跳过（用全局均值填充）
      - 选取对组间差异有区分度的特征
    """
    print("\n" + "=" * 70)
    print("2. 构建特征向量与特征画像")
    print("=" * 70)

    # 选取用于相似度计算的特征列
    feature_cols = [
        # 规模特征
        'student_count', 'course_count', 'sc_count', 'sc_per_student',
        # 结构特征
        's_dept_A_ratio', 's_dept_B_ratio', 's_dept_C_ratio',
        'c_dept_A_ratio', 'c_dept_B_ratio', 'c_dept_C_ratio',
        # 内容特征
        'sid_mean_len', 'sid_starts_with_digit',
        'cid_mean_len', 'cid_starts_with_digit',
        'credit_mean', 'credit_nunique',
        # 共享特征
        'share_ratio',
        # 性别特征
        'male_ratio',
        # 成绩特征
        'score_non_null_ratio',
    ]

    # 成绩全0或全NULL的组，score_mean 和 score_std 不可用
    # 对有成绩的组，额外添加成绩均值和标准差
    has_score = stats_df['score_non_null_ratio'] > 0.5
    if has_score.sum() > 0:
        feature_cols_extended = feature_cols + ['score_mean', 'score_std']
    else:
        feature_cols_extended = feature_cols

    # 提取特征矩阵
    feature_matrix = stats_df[feature_cols_extended].copy()

    # 处理缺失值：成绩相关特征用该列中位数填充
    for col in feature_cols_extended:
        if feature_matrix[col].isnull().any():
            median_val = feature_matrix[col].median()
            feature_matrix[col].fillna(median_val, inplace=True)
            print(f"  特征 '{col}' 有缺失值，已用中位数 {median_val:.2f} 填充")

    # 保存组号
    group_nos = stats_df['group_no'].values

    # 标准化
    scaler = StandardScaler()
    feature_scaled = scaler.fit_transform(feature_matrix)
    feature_scaled_df = pd.DataFrame(feature_scaled, columns=feature_cols_extended)
    feature_scaled_df.insert(0, 'group_no', group_nos)

    print(f"  特征向量构建完成: {len(feature_cols_extended)} 维特征, {len(group_nos)} 个组")
    print(f"  特征列表: {feature_cols_extended}")

    # 打印特征画像（原始值）
    print("\n  各组特征画像（关键维度）:")
    print(f"  {'组号':>4s} | {'学生数':>5s} | {'课程数':>5s} | {'选课数':>5s} | "
          f"{'选课/学生':>8s} | {'共享率':>6s} | {'男生率':>6s} | {'学分均值':>6s} | "
          f"{'成绩非空率':>8s}")
    print("  " + "-" * 80)
    for _, row in stats_df.iterrows():
        g = int(row['group_no'])
        mark = " ← 本组" if g == OWN_GROUP else ""
        print(f"  {g:4d} | {int(row['student_count']):5d} | {int(row['course_count']):5d} | "
              f"{int(row['sc_count']):5d} | {row['sc_per_student']:8.2f} | "
              f"{row['share_ratio']:6.1%} | {row['male_ratio']:6.1%} | "
              f"{row['credit_mean']:6.2f} | {row['score_non_null_ratio']:8.1%}{mark}")

    return feature_scaled, feature_scaled_df, feature_cols_extended, group_nos, scaler


# ============================================================
# 3. 相似度矩阵计算
# ============================================================
def compute_similarity_matrix(feature_scaled, group_nos):
    """
    计算组间相似度矩阵：
      - 余弦相似度
      - 欧氏距离（归一化后转换为相似度）
    综合两种度量，取加权平均。
    """
    print("\n" + "=" * 70)
    print("3. 计算组间相似度矩阵")
    print("=" * 70)

    n = len(group_nos)

    # 余弦相似度
    cos_sim = cosine_similarity(feature_scaled)
    cos_sim_df = pd.DataFrame(cos_sim, index=group_nos, columns=group_nos)
    print("  余弦相似度矩阵计算完成")

    # 欧氏距离 → 转换为相似度：sim = 1 / (1 + dist)
    euc_dist = euclidean_distances(feature_scaled)
    euc_sim = 1.0 / (1.0 + euc_dist)
    euc_sim_df = pd.DataFrame(euc_sim, index=group_nos, columns=group_nos)
    print("  欧氏距离相似度矩阵计算完成")

    # 综合相似度（余弦 0.5 + 欧氏 0.5）
    combined_sim = 0.5 * cos_sim + 0.5 * euc_sim
    combined_sim_df = pd.DataFrame(combined_sim, index=group_nos, columns=group_nos)
    print("  综合相似度矩阵计算完成")

    # 找本组最相似的组
    own_idx = list(group_nos).index(OWN_GROUP)
    own_cos = cos_sim[own_idx]
    own_euc = euc_sim[own_idx]
    own_combined = combined_sim[own_idx]

    # 排除自身
    other_indices = [i for i in range(n) if group_nos[i] != OWN_GROUP]

    # 按综合相似度排序
    sim_ranking = []
    for i in other_indices:
        sim_ranking.append({
            'group_no': int(group_nos[i]),
            'cosine_sim': round(own_cos[i], 4),
            'euclidean_sim': round(own_euc[i], 4),
            'combined_sim': round(own_combined[i], 4),
        })
    sim_ranking_df = pd.DataFrame(sim_ranking).sort_values('combined_sim', ascending=False)

    print(f"\n  本组({OWN_GROUP})与其他组的相似度排名（Top 10）:")
    print(f"  {'排名':>4s} | {'组号':>4s} | {'余弦相似度':>10s} | {'欧氏相似度':>10s} | {'综合相似度':>10s}")
    print("  " + "-" * 50)
    for rank, (_, row) in enumerate(sim_ranking_df.head(10).iterrows(), 1):
        print(f"  {rank:4d} | {int(row['group_no']):4d} | {row['cosine_sim']:10.4f} | "
              f"{row['euclidean_sim']:10.4f} | {row['combined_sim']:10.4f}")

    most_similar_group = int(sim_ranking_df.iloc[0]['group_no'])
    most_similar_score = sim_ranking_df.iloc[0]['combined_sim']
    print(f"\n  ★ 本组({OWN_GROUP})最相似的组: 组{most_similar_group} (综合相似度: {most_similar_score:.4f})")

    return cos_sim_df, euc_sim_df, combined_sim_df, sim_ranking_df, most_similar_group


# ============================================================
# 4. 最相似组深度分析
# ============================================================
def analyze_most_similar_group(stats_df, students, courses, sc,
                                most_similar_group, feature_cols_extended):
    """
    深度分析本组与最相似组的差异和共同点
    """
    print("\n" + "=" * 70)
    print(f"4. 本组({OWN_GROUP})与最相似组({most_similar_group})的深度对比分析")
    print("=" * 70)

    own = stats_df[stats_df['group_no'] == OWN_GROUP].iloc[0]
    similar = stats_df[stats_df['group_no'] == most_similar_group].iloc[0]

    comparison = []
    for col in feature_cols_extended:
        own_val = own[col]
        sim_val = similar[col]
        diff = own_val - sim_val if not (np.isnan(own_val) or np.isnan(sim_val)) else np.nan
        comparison.append({
            'feature': col,
            f'group_{OWN_GROUP}': round(own_val, 4) if not np.isnan(own_val) else 'N/A',
            f'group_{most_similar_group}': round(sim_val, 4) if not np.isnan(sim_val) else 'N/A',
            'difference': round(diff, 4) if not np.isnan(diff) else 'N/A',
        })

    comp_df = pd.DataFrame(comparison)
    print("\n  特征逐项对比:")
    print(comp_df.to_string(index=False))

    # 找出差异最大和最小的特征
    numeric_comp = comp_df[comp_df['difference'] != 'N/A'].copy()
    numeric_comp['diff_abs'] = numeric_comp['difference'].astype(float).abs()
    most_similar_features = numeric_comp.nsmallest(5, 'diff_abs')['feature'].tolist()
    most_different_features = numeric_comp.nlargest(5, 'diff_abs')['feature'].tolist()

    print(f"\n  最相似的特征（差异最小）: {most_similar_features}")
    print(f"  差异最大的特征: {most_different_features}")

    # 原始数据级对比
    print(f"\n  --- 原始数据级对比 ---")
    for g, label in [(OWN_GROUP, "本组"), (most_similar_group, "最相似组")]:
        g_s = students[students['group_no'] == g]
        g_c = courses[courses['group_no'] == g]
        g_sc = sc[sc['group_no'] == g]
        print(f"\n  [{label} — 组{g}]")
        print(f"    学号示例: {g_s['student_id'].head(5).tolist()}")
        print(f"    课程编号示例: {g_c['course_id'].head(5).tolist()}")
        if 'credit' in g_c.columns:
            print(f"    学分分布: {g_c['credit'].value_counts().to_dict()}")
        if 'share_flag' in g_c.columns:
            print(f"    共享标志分布: {g_c['share_flag'].value_counts().to_dict()}")
        if 'gender' in g_s.columns:
            print(f"    性别分布: {g_s['gender'].value_counts().to_dict()}")
        if 'score' in g_sc.columns:
            non_null = g_sc['score'].dropna()
            if len(non_null) > 0:
                print(f"    成绩: 均值={non_null.mean():.1f}, 标准差={non_null.std():.1f}, "
                      f"范围=[{non_null.min():.0f}, {non_null.max():.0f}]")
            else:
                print(f"    成绩: 全部NULL")

    return comp_df, most_similar_features, most_different_features


# ============================================================
# 5. 聚类分析
# ============================================================
def perform_clustering(feature_scaled, group_nos, stats_df):
    """
    对各组进行聚类分析：
      - K-Means 聚类
      - 层次聚类 + 树状图
    """
    print("\n" + "=" * 70)
    print("5. 聚类分析")
    print("=" * 70)

    # ---- 5a. K-Means ----
    # 使用肘部法选择最佳 K
    inertias = []
    K_range = range(2, min(10, len(group_nos)))
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(feature_scaled)
        inertias.append(km.inertia_)

    # 自动选择 K：寻找拐点（二阶差分最大的点）
    if len(inertias) >= 3:
        diffs = np.diff(inertias)
        diffs2 = np.diff(diffs)
        best_k_idx = np.argmax(diffs2) + 2  # +2 因为二阶差分比原序列短2
        best_k = list(K_range)[best_k_idx] if best_k_idx < len(list(K_range)) else 3
    else:
        best_k = 3

    # 限制 K 在合理范围
    best_k = max(2, min(best_k, 6))
    print(f"  K-Means 最佳簇数（肘部法）: K={best_k}")

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    km_labels = km_final.fit_predict(feature_scaled)

    cluster_result = pd.DataFrame({
        'group_no': group_nos,
        'kmeans_cluster': km_labels,
    })

    print(f"\n  K-Means 聚类结果 (K={best_k}):")
    for c in range(best_k):
        members = cluster_result[cluster_result['kmeans_cluster'] == c]['group_no'].tolist()
        own_mark = " ← 本组" if OWN_GROUP in members else ""
        print(f"    簇 {c}: 组 {members}{own_mark}")

    # ---- 5b. 层次聚类 ----
    # 使用 Ward 连接法
    linkage_matrix = linkage(feature_scaled, method='ward')

    # 用与 K-Means 相同的簇数进行切割
    hc = AgglomerativeClustering(n_clusters=best_k, linkage='ward')
    hc_labels = hc.fit_predict(feature_scaled)

    cluster_result['hc_cluster'] = hc_labels

    print(f"\n  层次聚类结果 (K={best_k}):")
    for c in range(best_k):
        members = cluster_result[cluster_result['hc_cluster'] == c]['group_no'].tolist()
        own_mark = " ← 本组" if OWN_GROUP in members else ""
        print(f"    簇 {c}: 组 {members}{own_mark}")

    # 本组所在的簇
    own_km_cluster = cluster_result[cluster_result['group_no'] == OWN_GROUP]['kmeans_cluster'].values[0]
    own_hc_cluster = cluster_result[cluster_result['group_no'] == OWN_GROUP]['hc_cluster'].values[0]

    km_cluster_members = cluster_result[cluster_result['kmeans_cluster'] == own_km_cluster]['group_no'].tolist()
    hc_cluster_members = cluster_result[cluster_result['hc_cluster'] == own_hc_cluster]['group_no'].tolist()

    print(f"\n  本组({OWN_GROUP})所在簇:")
    print(f"    K-Means 簇 {own_km_cluster}: 组 {km_cluster_members}")
    print(f"    层次聚类 簇 {own_hc_cluster}: 组 {hc_cluster_members}")

    return cluster_result, linkage_matrix, best_k, inertias, K_range


# ============================================================
# 6. 可视化
# ============================================================
def create_visualizations(stats_df, combined_sim_df, cos_sim_df, group_nos,
                          most_similar_group, comp_df, feature_cols_extended,
                          feature_scaled, cluster_result, linkage_matrix,
                          best_k, inertias, K_range):
    """
    生成所有可视化图表
    """
    print("\n" + "=" * 70)
    print("生成可视化图表...")
    print("=" * 70)

    ensure_dir(FIGURES_DIR)

    # 配色
    OWN_COLOR = '#2ecc71'  # 本组绿色
    SIMILAR_COLOR = '#e67e22'  # 最相似组橙色
    OTHER_COLOR = '#3498db'  # 其他组蓝色

    # ---- 图7: 各组核心指标对比柱状图 ----
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    # 学生数
    ax = axes[0, 0]
    colors = [OWN_COLOR if g == OWN_GROUP else SIMILAR_COLOR if g == most_similar_group else OTHER_COLOR
              for g in stats_df['group_no']]
    ax.bar(stats_df['group_no'].astype(str), stats_df['student_count'], color=colors, alpha=0.85)
    ax.set_title('Student Count by Group', fontsize=12, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Student Count')
    ax.tick_params(axis='x', rotation=45)

    # 课程数
    ax = axes[0, 1]
    ax.bar(stats_df['group_no'].astype(str), stats_df['course_count'], color=colors, alpha=0.85)
    ax.set_title('Course Count by Group', fontsize=12, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Course Count')
    ax.tick_params(axis='x', rotation=45)

    # 选课数
    ax = axes[1, 0]
    ax.bar(stats_df['group_no'].astype(str), stats_df['sc_count'], color=colors, alpha=0.85)
    ax.set_title('SC Record Count by Group', fontsize=12, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('SC Count')
    ax.tick_params(axis='x', rotation=45)

    # 选课/学生比
    ax = axes[1, 1]
    ax.bar(stats_df['group_no'].astype(str), stats_df['sc_per_student'], color=colors, alpha=0.85)
    ax.set_title('SC per Student by Group', fontsize=12, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('SC / Student')
    ax.tick_params(axis='x', rotation=45)

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=OWN_COLOR, label=f'Own (G{OWN_GROUP})'),
        Patch(facecolor=SIMILAR_COLOR, label=f'Most Similar (G{most_similar_group})'),
        Patch(facecolor=OTHER_COLOR, label='Others'),
    ]
    fig.legend(handles=legend_elements, loc='upper right', fontsize=10,
               bbox_to_anchor=(0.98, 0.98))

    fig.suptitle('Group Core Scale Metrics Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig7_group_scale_comparison.png'))
    plt.close(fig)
    print("  [OK] 图7: 各组核心规模指标对比")

    # ---- 图8: 各组院系分布堆叠柱状图 ----
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 学生院系分布
    ax = axes[0]
    depts = ['A', 'B', 'C']
    dept_colors = ['#3498db', '#e74c3c', '#2ecc71']
    bottom = np.zeros(len(stats_df))
    for dept, color in zip(depts, dept_colors):
        col = f's_dept_{dept}_ratio'
        vals = stats_df[col].values * stats_df['student_count'].values
        ax.bar(stats_df['group_no'].astype(str), vals, bottom=bottom,
               label=f'Dept {dept}', color=color, alpha=0.85)
        bottom += vals
    ax.set_title('Student Dept Distribution by Group', fontsize=12, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Student Count')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    # 课程院系分布
    ax = axes[1]
    bottom = np.zeros(len(stats_df))
    for dept, color in zip(depts, dept_colors):
        col = f'c_dept_{dept}_ratio'
        vals = stats_df[col].values * stats_df['course_count'].values
        ax.bar(stats_df['group_no'].astype(str), vals, bottom=bottom,
               label=f'Dept {dept}', color=color, alpha=0.85)
        bottom += vals
    ax.set_title('Course Dept Distribution by Group', fontsize=12, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Course Count')
    ax.tick_params(axis='x', rotation=45)
    ax.legend()

    fig.suptitle('Group Dept Distribution Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig8_dept_distribution.png'))
    plt.close(fig)
    print("  [OK] 图8: 各组院系分布堆叠柱状图")

    # ---- 图9: 共享课程比例对比 ----
    fig, ax = plt.subplots(figsize=(14, 5))
    colors_share = [OWN_COLOR if g == OWN_GROUP else SIMILAR_COLOR if g == most_similar_group else OTHER_COLOR
                    for g in stats_df['group_no']]
    ax.bar(stats_df['group_no'].astype(str), stats_df['share_ratio'] * 100,
           color=colors_share, alpha=0.85)
    ax.set_title('Shared Course Ratio by Group', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Shared Course Ratio (%)')
    ax.tick_params(axis='x', rotation=45)

    # 标注数值
    for i, (g, r) in enumerate(zip(stats_df['group_no'], stats_df['share_ratio'])):
        ax.text(i, r * 100 + 1, f'{r*100:.0f}%', ha='center', fontsize=7)

    fig.legend(handles=legend_elements, loc='upper right', fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig9_share_ratio_comparison.png'))
    plt.close(fig)
    print("  [OK] 图9: 各组共享课程比例对比")

    # ---- 图10: 各组性别比例对比 ----
    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(len(stats_df))
    width = 0.35
    bars_m = ax.bar(x - width/2, stats_df['male_ratio'] * 100, width,
                    label='Male Ratio', color='#3498db', alpha=0.85)
    bars_f = ax.bar(x + width/2, (1 - stats_df['male_ratio']) * 100, width,
                    label='Female Ratio', color='#e74c3c', alpha=0.85)
    # 高亮本组
    own_idx = list(stats_df['group_no']).index(OWN_GROUP)
    bars_m[own_idx].set_color(OWN_COLOR)
    bars_f[own_idx].set_color('#27ae60')

    ax.set_title('Gender Ratio by Group', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Ratio (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(stats_df['group_no'].astype(str), rotation=45)
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig10_gender_ratio_comparison.png'))
    plt.close(fig)
    print("  [OK] 图10: 各组性别比例对比")

    # ---- 图11: 组间相似度热力图 ----
    fig, ax = plt.subplots(figsize=(14, 12))
    # 使用综合相似度
    mask = np.zeros_like(combined_sim_df, dtype=bool)
    # 不做mask，展示完整矩阵
    sns.heatmap(combined_sim_df, annot=True, fmt='.2f', cmap='RdYlGn',
                linewidths=0.5, linecolor='white', ax=ax,
                vmin=-0.5, vmax=1.0, cbar_kws={'label': 'Combined Similarity'})
    ax.set_title('Inter-Group Combined Similarity Heatmap', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Group No.')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig11_similarity_heatmap.png'))
    plt.close(fig)
    print("  [OK] 图11: 组间相似度热力图")

    # ---- 图12: 本组与最相似组的雷达图对比 ----
    own = stats_df[stats_df['group_no'] == OWN_GROUP].iloc[0]
    similar = stats_df[stats_df['group_no'] == most_similar_group].iloc[0]

    # 选取雷达图的特征（选取可解释性强的）
    radar_features = [
        ('student_count', 'Students'),
        ('course_count', 'Courses'),
        ('sc_per_student', 'SC/Student'),
        ('share_ratio', 'Share Ratio'),
        ('male_ratio', 'Male Ratio'),
        ('credit_mean', 'Avg Credit'),
        ('score_non_null_ratio', 'Score Non-Null'),
    ]

    # 归一化到 [0, 1]
    radar_labels = [f[1] for f in radar_features]
    radar_cols = [f[0] for f in radar_features]

    own_vals = []
    sim_vals = []
    for col in radar_cols:
        col_min = stats_df[col].min()
        col_max = stats_df[col].max()
        col_range = col_max - col_min if col_max != col_min else 1
        own_vals.append((own[col] - col_min) / col_range)
        sim_vals.append((similar[col] - col_min) / col_range)

    # 闭合雷达图
    N = len(radar_labels)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    own_vals += own_vals[:1]
    sim_vals += sim_vals[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, own_vals, 'o-', linewidth=2, color=OWN_COLOR,
            label=f'G{OWN_GROUP} (Own)')
    ax.fill(angles, own_vals, alpha=0.15, color=OWN_COLOR)
    ax.plot(angles, sim_vals, 'o-', linewidth=2, color=SIMILAR_COLOR,
            label=f'G{most_similar_group} (Most Similar)')
    ax.fill(angles, sim_vals, alpha=0.15, color=SIMILAR_COLOR)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(radar_labels, fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.set_title(f'G{OWN_GROUP} vs G{most_similar_group} Feature Radar Comparison',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig12_radar_comparison.png'))
    plt.close(fig)
    print("  [OK] 图12: 本组与最相似组雷达图对比")

    # ---- 图13: K-Means肘部图 ----
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(list(K_range), inertias, 'bo-', linewidth=2, markersize=8)
    ax.axvline(x=best_k, color='red', linestyle='--', alpha=0.7, label=f'Selected K={best_k}')
    ax.set_title('K-Means Elbow Method', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Clusters K')
    ax.set_ylabel('Inertia')
    ax.legend()
    ax.set_xticks(list(K_range))
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig13_kmeans_elbow.png'))
    plt.close(fig)
    print("  [OK] 图13: K-Means肘部图")

    # ---- 图14: 层次聚类树状图 ----
    fig, ax = plt.subplots(figsize=(16, 8))
    dendrogram(linkage_matrix, labels=[str(g) for g in group_nos],
               ax=ax, leaf_font_size=10, leaf_rotation=45)
    ax.set_title('Hierarchical Clustering Dendrogram (Ward)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Distance')
    # 高亮本组
    for lbl in ax.get_xticklabels():
        if lbl.get_text() == str(OWN_GROUP):
            lbl.set_color('green')
            lbl.set_fontweight('bold')
        if lbl.get_text() == str(most_similar_group):
            lbl.set_color('orange')
            lbl.set_fontweight('bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig14_dendrogram.png'))
    plt.close(fig)
    print("  [OK] 图14: 层次聚类树状图")

    # ---- 图15: 聚类结果散点图（前两个主成分） ----
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    features_2d = pca.fit_transform(feature_scaled)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # K-Means
    ax = axes[0]
    km_labels = cluster_result['kmeans_cluster'].values
    scatter_colors = sns.color_palette("Set2", best_k)
    for c in range(best_k):
        mask = km_labels == c
        ax.scatter(features_2d[mask, 0], features_2d[mask, 1],
                   c=[scatter_colors[c]], label=f'Cluster {c}', s=100, alpha=0.8, edgecolors='gray')
    # 标注组号
    for i, g in enumerate(group_nos):
        fontweight = 'bold' if g == OWN_GROUP else 'normal'
        fontsize = 11 if g == OWN_GROUP else 8
        ax.annotate(str(int(g)), (features_2d[i, 0], features_2d[i, 1]),
                    fontsize=fontsize, fontweight=fontweight, ha='center', va='bottom')
    ax.set_title(f'K-Means Clustering (K={best_k})', fontsize=12, fontweight='bold')
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax.legend()

    # 层次聚类
    ax = axes[1]
    hc_labels = cluster_result['hc_cluster'].values
    for c in range(best_k):
        mask = hc_labels == c
        ax.scatter(features_2d[mask, 0], features_2d[mask, 1],
                   c=[scatter_colors[c]], label=f'Cluster {c}', s=100, alpha=0.8, edgecolors='gray')
    for i, g in enumerate(group_nos):
        fontweight = 'bold' if g == OWN_GROUP else 'normal'
        fontsize = 11 if g == OWN_GROUP else 8
        ax.annotate(str(int(g)), (features_2d[i, 0], features_2d[i, 1]),
                    fontsize=fontsize, fontweight=fontweight, ha='center', va='bottom')
    ax.set_title(f'Hierarchical Clustering (K={best_k})', fontsize=12, fontweight='bold')
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax.legend()

    fig.suptitle('Clustering Results (PCA Reduced)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig15_cluster_scatter.png'))
    plt.close(fig)
    print("  [OK] 图15: 聚类结果散点图")

    # ---- 图16: 相似度排名条形图 ----
    fig, ax = plt.subplots(figsize=(14, 6))
    sim_ranking_sorted = stats_df.copy()
    sim_ranking_sorted['sim_to_own'] = combined_sim_df.loc[OWN_GROUP].values
    sim_ranking_sorted = sim_ranking_sorted[sim_ranking_sorted['group_no'] != OWN_GROUP]
    sim_ranking_sorted = sim_ranking_sorted.sort_values('sim_to_own', ascending=True)

    bar_colors = [SIMILAR_COLOR if g == most_similar_group else OTHER_COLOR
                  for g in sim_ranking_sorted['group_no']]
    ax.barh(sim_ranking_sorted['group_no'].astype(str), sim_ranking_sorted['sim_to_own'],
            color=bar_colors, alpha=0.85)
    ax.set_title(f'Combined Similarity to G{OWN_GROUP} (Own Group)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Combined Similarity')
    ax.set_ylabel('Group No.')

    # 标注数值
    for i, (g, sim) in enumerate(zip(sim_ranking_sorted['group_no'], sim_ranking_sorted['sim_to_own'])):
        ax.text(sim + 0.005, i, f'{sim:.3f}', va='center', fontsize=8)

    ax.legend(handles=legend_elements[:2], loc='lower right', fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig16_similarity_ranking.png'))
    plt.close(fig)
    print("  [OK] 图16: 相似度排名条形图")

    figure_count = 10  # 图7-图16
    print(f"\n  所有图表已保存至 {FIGURES_DIR}/")
    return figure_count


# ============================================================
# 7. 生成最相似组分析报告
# ============================================================
def generate_report(stats_df, combined_sim_df, cos_sim_df, sim_ranking_df,
                    most_similar_group, comp_df, most_similar_features,
                    most_different_features, cluster_result, best_k,
                    feature_cols_extended, figure_count, group_nos):
    """
    生成综合分析Markdown报告
    """
    print("\n" + "=" * 70)
    print("生成最相似组分析报告...")
    print("=" * 70)

    own = stats_df[stats_df['group_no'] == OWN_GROUP].iloc[0]
    similar = stats_df[stats_df['group_no'] == most_similar_group].iloc[0]

    report = []
    report.append("# 统计分析与相似度计算报告")
    report.append(f"\n> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"> 分析组数: {len(group_nos)} 个组（排除不完整组 9, 19, 25）")
    report.append(f"> 本组组号: {OWN_GROUP}")
    report.append("")

    # ---- 一、特征画像 ----
    report.append("## 一、各组特征画像")
    report.append("")
    report.append("### 1.1 核心统计指标汇总")
    report.append("")
    report.append("| 组号 | 学生数 | 课程数 | 选课数 | 人均选课 | 共享率 | 男生率 | 学分均值 | 成绩非空率 |")
    report.append("|------|--------|--------|--------|----------|--------|--------|----------|------------|")
    for _, row in stats_df.iterrows():
        g = int(row['group_no'])
        mark = " **←本组**" if g == OWN_GROUP else ""
        report.append(f"| {g} | {int(row['student_count'])} | {int(row['course_count'])} | "
                      f"{int(row['sc_count'])} | {row['sc_per_student']:.2f} | "
                      f"{row['share_ratio']:.1%} | {row['male_ratio']:.1%} | "
                      f"{row['credit_mean']:.2f} | {row['score_non_null_ratio']:.1%} |{mark}")
    report.append("")

    report.append("### 1.2 特征维度说明")
    report.append("")
    report.append(f"共选取 **{len(feature_cols_extended)}** 维特征用于相似度计算，涵盖：")
    report.append("")
    report.append("| 特征类别 | 具体特征 | 说明 |")
    report.append("|----------|----------|------|")
    report.append("| 规模特征 | student_count, course_count, sc_count, sc_per_student | 数据规模与密度 |")
    report.append("| 结构特征 | s_dept_A/B/C_ratio, c_dept_A/B/C_ratio | 各院系分布比例 |")
    report.append("| 内容特征 | sid_mean_len, sid_starts_with_digit, cid_mean_len, cid_starts_with_digit, credit_mean, credit_nunique | 编码风格与学分设计 |")
    report.append("| 共享特征 | share_ratio | 共享课程占比 |")
    report.append("| 性别特征 | male_ratio | 男生比例 |")
    report.append("| 成绩特征 | score_non_null_ratio, score_mean, score_std | 成绩数据质量与分布 |")
    report.append("")

    # ---- 二、相似度分析 ----
    report.append("## 二、组间相似度分析")
    report.append("")
    report.append("### 2.1 相似度计算方法")
    report.append("")
    report.append("采用两种度量方法，并计算综合相似度：")
    report.append("")
    report.append("1. **余弦相似度**: 衡量特征向量方向的一致性，对绝对量纲不敏感，适合比较组的\"结构模式\"是否相似")
    report.append("2. **欧氏距离相似度**: `sim = 1/(1+dist)`，衡量特征空间中的绝对距离，对量纲敏感")
    report.append("3. **综合相似度**: `combined = 0.5 × cosine + 0.5 × euclidean`，兼顾方向和距离")
    report.append("")
    report.append("所有特征在计算前经过 StandardScaler 标准化（零均值、单位方差），以消除量纲差异。")
    report.append("")

    report.append("### 2.2 本组相似度排名")
    report.append("")
    report.append(f"本组（组{OWN_GROUP}）与其他组的综合相似度排名：")
    report.append("")
    report.append("| 排名 | 组号 | 余弦相似度 | 欧氏相似度 | 综合相似度 |")
    report.append("|------|------|------------|------------|------------|")
    for rank, (_, row) in enumerate(sim_ranking_df.iterrows(), 1):
        g = int(row['group_no'])
        mark = " **★最相似**" if g == most_similar_group else ""
        report.append(f"| {rank} | {g} | {row['cosine_sim']:.4f} | "
                      f"{row['euclidean_sim']:.4f} | {row['combined_sim']:.4f} |{mark}")
    report.append("")

    # ---- 三、最相似组分析 ----
    report.append("## 三、最相似组深度分析")
    report.append("")
    report.append(f"本组（组{OWN_GROUP}）的最相似组为 **组{most_similar_group}**。")
    report.append("")

    report.append("### 3.1 特征逐项对比")
    report.append("")
    report.append("| 特征 | 本组(16) | 最相似组 | 差异 |")
    report.append("|------|----------|----------|------|")
    for _, row in comp_df.iterrows():
        report.append(f"| {row['feature']} | {row[f'group_{OWN_GROUP}']} | "
                      f"{row[f'group_{most_similar_group}']} | {row['difference']} |")
    report.append("")

    report.append("### 3.2 相似原因分析")
    report.append("")
    report.append(f"**最相似的特征（差异最小）**: {', '.join(most_similar_features)}")
    report.append("")
    report.append(f"**差异最大的特征**: {', '.join(most_different_features)}")
    report.append("")

    # 具体分析
    report.append("#### 相似点详解")
    report.append("")
    # 逐项分析最相似的特征
    for feat in most_similar_features:
        own_val = own[feat]
        sim_val = similar[feat]
        if 'ratio' in feat:
            report.append(f"- **{feat}**: 本组={own_val:.1%}, 组{most_similar_group}={sim_val:.1%}")
        else:
            report.append(f"- **{feat}**: 本组={own_val:.2f}, 组{most_similar_group}={sim_val:.2f}")

    report.append("")
    report.append("#### 差异点详解")
    report.append("")
    for feat in most_different_features:
        own_val = own[feat]
        sim_val = similar[feat]
        if 'ratio' in feat:
            report.append(f"- **{feat}**: 本组={own_val:.1%}, 组{most_similar_group}={sim_val:.1%}")
        else:
            report.append(f"- **{feat}**: 本组={own_val:.2f}, 组{most_similar_group}={sim_val:.2f}")
    report.append("")

    # ---- 四、聚类分析 ----
    report.append("## 四、聚类分析")
    report.append("")
    report.append(f"### 4.1 K-Means 聚类 (K={best_k})")
    report.append("")
    for c in range(best_k):
        members = cluster_result[cluster_result['kmeans_cluster'] == c]['group_no'].tolist()
        own_mark = " ← **本组所在簇**" if OWN_GROUP in members else ""
        report.append(f"- 簇 {c}: 组 {members}{own_mark}")
    report.append("")

    report.append(f"### 4.2 层次聚类 (K={best_k})")
    report.append("")
    for c in range(best_k):
        members = cluster_result[cluster_result['hc_cluster'] == c]['group_no'].tolist()
        own_mark = " ← **本组所在簇**" if OWN_GROUP in members else ""
        report.append(f"- 簇 {c}: 组 {members}{own_mark}")
    report.append("")

    report.append("### 4.3 聚类解读")
    report.append("")
    # 分析本组所在簇的特征
    own_km_cluster = cluster_result[cluster_result['group_no'] == OWN_GROUP]['kmeans_cluster'].values[0]
    km_members = cluster_result[cluster_result['kmeans_cluster'] == own_km_cluster]['group_no'].tolist()
    cluster_stats = stats_df[stats_df['group_no'].isin(km_members)]

    report.append(f"本组（组{OWN_GROUP}）在 K-Means 聚类中属于 **簇{own_km_cluster}**，")
    report.append(f"该簇包含组 {km_members}。")
    report.append("")
    report.append("该簇的共性特征：")
    report.append(f"- 平均学生数: {cluster_stats['student_count'].mean():.0f}")
    report.append(f"- 平均课程数: {cluster_stats['course_count'].mean():.0f}")
    report.append(f"- 平均选课数: {cluster_stats['sc_count'].mean():.0f}")
    report.append(f"- 平均共享率: {cluster_stats['share_ratio'].mean():.1%}")
    report.append(f"- 平均男生率: {cluster_stats['male_ratio'].mean():.1%}")
    report.append(f"- 平均学分: {cluster_stats['credit_mean'].mean():.2f}")
    report.append("")

    # ---- 五、结论 ----
    report.append("## 五、结论")
    report.append("")
    report.append(f"1. **最相似组**: 组{most_similar_group}与本组（组{OWN_GROUP}）的综合相似度最高，")
    top3 = sim_ranking_df.head(3)
    report.append(f"   综合相似度为 {top3.iloc[0]['combined_sim']:.4f}。")
    report.append(f"   排名前三的相似组为：组{int(top3.iloc[0]['group_no'])}、"
                  f"组{int(top3.iloc[1]['group_no'])}、组{int(top3.iloc[2]['group_no'])}。")
    report.append("")
    report.append(f"2. **相似原因**: 本组与组{most_similar_group}在")
    report.append(f"   {', '.join(most_similar_features[:3])} 等特征上高度一致，")
    report.append(f"   说明两组在数据设计上采用了类似的规模和结构模式。")
    report.append("")
    report.append(f"3. **主要差异**: 在 {', '.join(most_different_features[:3])} 等维度存在差异，")
    report.append(f"   这可能反映了编码风格或具体参数设置的不同。")
    report.append("")
    report.append(f"4. **聚类归属**: 本组属于 K-Means 簇{own_km_cluster}，")
    report.append(f"   与组 {km_members} 被归为同一类别，这些组在数据特征上具有自然聚集性。")
    report.append("")

    # ---- 图表清单 ----
    report.append("## 六、可视化图表清单")
    report.append("")
    report.append("| 编号 | 图表名称 | 文件 | 说明 |")
    report.append("|------|----------|------|------|")
    report.append("| 图7 | 各组核心规模指标对比 | fig7_group_scale_comparison.png | 学生数/课程数/选课数/人均选课 |")
    report.append("| 图8 | 各组院系分布堆叠柱状图 | fig8_dept_distribution.png | 学生和课程院系分布 |")
    report.append("| 图9 | 各组共享课程比例对比 | fig9_share_ratio_comparison.png | 共享率柱状图 |")
    report.append("| 图10 | 各组性别比例对比 | fig10_gender_ratio_comparison.png | 男女比例分组条形图 |")
    report.append("| 图11 | 组间相似度热力图 | fig11_similarity_heatmap.png | 综合相似度矩阵 |")
    report.append("| 图12 | 本组与最相似组雷达图 | fig12_radar_comparison.png | 多维特征雷达图对比 |")
    report.append("| 图13 | K-Means肘部图 | fig13_kmeans_elbow.png | 选择最佳簇数 |")
    report.append("| 图14 | 层次聚类树状图 | fig14_dendrogram.png | Ward连接层次聚类 |")
    report.append("| 图15 | 聚类结果散点图 | fig15_cluster_scatter.png | PCA降维后的聚类可视化 |")
    report.append("| 图16 | 相似度排名条形图 | fig16_similarity_ranking.png | 各组与本组相似度排名 |")
    report.append(f"\n> 共 {figure_count} 张图表，保存于 `figures/` 目录。")
    report.append("")

    # 写入文件
    report_text = "\n".join(report)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"  [OK] 报告已保存至: {REPORT_PATH}")
    return report_text


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 70)
    print("  统计分析与相似度计算脚本 - 作业四 成员4")
    print(f"  执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    ensure_dir(FIGURES_DIR)

    # 加载数据
    students, courses, sc = load_data()

    # 1. 计算各组核心统计指标
    stats_df = compute_group_statistics(students, courses, sc)

    # 2. 构建特征向量与特征画像
    feature_scaled, feature_scaled_df, feature_cols_extended, group_nos, scaler = \
        build_feature_vectors(stats_df)

    # 3. 计算相似度矩阵
    cos_sim_df, euc_sim_df, combined_sim_df, sim_ranking_df, most_similar_group = \
        compute_similarity_matrix(feature_scaled, group_nos)

    # 4. 最相似组深度分析
    comp_df, most_similar_features, most_different_features = \
        analyze_most_similar_group(stats_df, students, courses, sc,
                                    most_similar_group, feature_cols_extended)

    # 5. 聚类分析
    cluster_result, linkage_matrix, best_k, inertias, K_range = \
        perform_clustering(feature_scaled, group_nos, stats_df)

    # 6. 可视化
    figure_count = create_visualizations(
        stats_df, combined_sim_df, cos_sim_df, group_nos,
        most_similar_group, comp_df, feature_cols_extended,
        feature_scaled, cluster_result, linkage_matrix,
        best_k, inertias, K_range,
    )

    # 7. 生成报告
    report = generate_report(
        stats_df, combined_sim_df, cos_sim_df, sim_ranking_df,
        most_similar_group, comp_df, most_similar_features,
        most_different_features, cluster_result, best_k,
        feature_cols_extended, figure_count, group_nos,
    )

    # 汇总输出
    print("\n" + "=" * 70)
    print("  统计分析与相似度计算完成！")
    print(f"  - 分析组数: {len(group_nos)}")
    print(f"  - 特征维度: {len(feature_cols_extended)}")
    print(f"  - 最相似组: 组{most_similar_group}")
    print(f"  - 生成 {figure_count} 张可视化图表")
    print(f"  - 报告: {REPORT_PATH}")
    print(f"  - 图表: {FIGURES_DIR}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
