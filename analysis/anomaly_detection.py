#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测脚本 - 作业四 成员3

对各组数据进行全面质量检查：
  1. 缺失值分析：哪些组缺少数据、哪些字段有空值
  2. 重复值检查：重复学号、重复课程编号、重复选课记录
  3. 格式异常：学号/课程编号格式不一致、字段长度超限
  4. 数量异常：学生数/课程数/选课数偏离预期的组
  5. 逻辑异常：选课记录指向不存在的学生或课程、跨组引用

输出：
  - 异常数据可视化图表（保存至 figures/）
  - 异常检测报告（保存至 anomaly_report.md）
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import sys
from datetime import datetime
from collections import defaultdict

# ============================================================
# 全局设置
# ============================================================
DATA_DIR = './data'
CLEANED_DIR = os.path.join(DATA_DIR, 'cleaned')
FIGURES_DIR = './figures'
REPORT_PATH = './anomaly_report.md'

# Use English labels to avoid CJK font rendering issues
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

# 本组组号
OWN_GROUP = 16

# 各组"标准"规模（最常见的模式：3院×50学生, 3院×10课程, 3院×250选课）
EXPECTED_STUDENTS = 150
EXPECTED_COURSES = 30
EXPECTED_SC = 750


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

    # 同时加载原始数据（用于对比清洗前后的差异）
    raw_students = pd.read_csv(os.path.join(DATA_DIR, 'students.csv'))
    raw_courses = pd.read_csv(os.path.join(DATA_DIR, 'courses.csv'))
    raw_sc = pd.read_csv(os.path.join(DATA_DIR, 'sc.csv'))

    print(f"  学生表: {len(students)} 条 (原始 {len(raw_students)} 条)")
    print(f"  课程表: {len(courses)} 条 (原始 {len(raw_courses)} 条)")
    print(f"  选课表: {len(sc)} 条 (原始 {len(raw_sc)} 条)")

    return {
        'students': students, 'courses': courses, 'sc': sc,
        'raw_students': raw_students, 'raw_courses': raw_courses, 'raw_sc': raw_sc,
    }


def get_all_groups(data):
    """获取所有组号集合"""
    s_g = set(data['students']['group_no'].unique())
    c_g = set(data['courses']['group_no'].unique())
    sc_g = set(data['sc']['group_no'].unique())
    all_g = sorted(s_g | c_g | sc_g)
    return all_g, s_g, c_g, sc_g


# ============================================================
# 1. 缺失值分析
# ============================================================
def analyze_missing_values(data, all_groups):
    """
    缺失值分析：
    - 各组在三张表中的覆盖情况
    - 各字段的缺失值按组分布
    """
    print("\n" + "=" * 70)
    print("1. 缺失值分析")
    print("=" * 70)

    students = data['students']
    courses = data['courses']
    sc = data['sc']

    findings = []

    # --- 1a. 组级别数据覆盖 ---
    s_g = set(students['group_no'].unique())
    c_g = set(courses['group_no'].unique())
    sc_g = set(sc['group_no'].unique())

    # 构建覆盖矩阵
    coverage = pd.DataFrame(index=sorted(all_groups))
    coverage['Has Students'] = coverage.index.isin(s_g)
    coverage['Has Courses'] = coverage.index.isin(c_g)
    coverage['Has SC'] = coverage.index.isin(sc_g)
    coverage['Completeness'] = coverage.sum(axis=1)

    full_groups = coverage[coverage['Completeness'] == 3].index.tolist()
    partial_groups = coverage[coverage['Completeness'] < 3].index.tolist()

    print(f"\n  完整组 (三表齐全): {len(full_groups)} 个 — {full_groups}")
    print(f"  不完整组: {len(partial_groups)} 个")
    for g in partial_groups:
        missing_tables = []
        if g not in s_g:
            missing_tables.append('学生表')
        if g not in c_g:
            missing_tables.append('课程表')
        if g not in sc_g:
            missing_tables.append('选课表')
        print(f"    组{g}: 缺少 {', '.join(missing_tables)}")

    if partial_groups:
        findings.append({
            '类别': '缺失值-组级',
            '严重程度': '高',
            '描述': f'共 {len(partial_groups)} 个组数据不完整（缺少至少一张表）：{partial_groups}',
            '详情': '; '.join([f"组{g}缺少{['Students','Courses','SC'][i]}" for g in partial_groups for i in range(3) if not coverage.iloc[all_groups.index(g), i]]),
        })

    # --- 1b. 字段级缺失值 ---
    print("\n  [字段级缺失值统计]")

    # 学生表字段缺失
    student_null_cols = ['account', 'password']
    for col in student_null_cols:
        null_count = students[col].isnull().sum()
        if null_count > 0:
            null_groups = students[students[col].isnull()]['group_no'].unique()
            print(f"  students.{col}: {null_count} 个缺失, 涉及组 {sorted(null_groups)}")
            findings.append({
                '类别': '缺失值-字段',
                '严重程度': '低',
                '描述': f'学生表 {col} 字段共 {null_count} 条缺失',
                '详情': f'涉及组: {sorted(null_groups)}，占总记录 {null_count/len(students)*100:.1f}%',
            })

    # 选课表成绩缺失 — 按组分析
    sc_null_by_group = sc.groupby('group_no')['score'].apply(
        lambda x: x.isnull().sum()
    ).reset_index(name='null_count')
    sc_null_by_group['total'] = sc.groupby('group_no').size().values
    sc_null_by_group['null_rate'] = (
        sc_null_by_group['null_count'] / sc_null_by_group['total'] * 100
    )
    sc_null_by_group = sc_null_by_group.sort_values('null_rate', ascending=False)

    print("\n  [成绩缺失率按组分布]")
    for _, row in sc_null_by_group.iterrows():
        if row['null_rate'] > 0:
            print(f"    组{int(row['group_no']):2d}: {int(row['null_count'])}/{int(row['total'])} "
                  f"({row['null_rate']:.1f}%)")

    full_null_groups = sc_null_by_group[sc_null_by_group['null_rate'] == 100]['group_no'].tolist()
    partial_null_groups = sc_null_by_group[
        (sc_null_by_group['null_rate'] > 0) & (sc_null_by_group['null_rate'] < 100)
    ]['group_no'].tolist()

    if full_null_groups:
        findings.append({
            '类别': '缺失值-成绩',
            '严重程度': '中',
            '描述': f'共 {len(full_null_groups)} 个组所有选课记录的成绩均为 NULL',
            '详情': f'组: {full_null_groups}，这些组完全未录入成绩数据',
        })
    if partial_null_groups:
        findings.append({
            '类别': '缺失值-成绩',
            '严重程度': '中',
            '描述': f'共 {len(partial_null_groups)} 个组部分选课记录成绩为 NULL',
            '详情': f'组: {partial_null_groups}',
        })

    # 本组成绩情况
    g16_score_null = sc_null_by_group[sc_null_by_group['group_no'] == OWN_GROUP]
    if len(g16_score_null) > 0:
        print(f"\n  本组({OWN_GROUP})成绩缺失: {int(g16_score_null['null_count'].values[0])}/{int(g16_score_null['total'].values[0])}")

    return findings, coverage, sc_null_by_group


# ============================================================
# 2. 重复值检查
# ============================================================
def analyze_duplicates(data, all_groups):
    """
    重复值检查：
    - 重复学号（跨组/组内）
    - 重复课程编号（跨组/组内）
    - 重复选课记录
    """
    print("\n" + "=" * 70)
    print("2. 重复值检查")
    print("=" * 70)

    students = data['students']
    courses = data['courses']
    sc = data['sc']
    raw_students = data['raw_students']
    raw_courses = data['raw_courses']
    raw_sc = data['raw_sc']

    findings = []

    # --- 2a. 学号重复 ---
    # 组内重复
    sid_dup_within = students[students.duplicated(subset=['group_no', 'student_id'], keep=False)]
    sid_dup_within_count = sid_dup_within.groupby('group_no')['student_id'].nunique()
    print(f"\n  [学号组内重复]: {len(sid_dup_within)} 条涉及重复学号")
    for g, cnt in sid_dup_within_count.items():
        dup_ids = sid_dup_within[sid_dup_within['group_no'] == g]['student_id'].unique()
        print(f"    组{g}: {cnt} 个重复学号 → {dup_ids[:5].tolist()}")

    if len(sid_dup_within) > 0:
        findings.append({
            '类别': '重复值-学号组内',
            '严重程度': '高',
            '描述': f'共 {len(sid_dup_within)} 条记录存在组内学号重复',
            '详情': f'涉及组: {sorted(sid_dup_within_count.index.tolist())}',
        })

    # 跨组重复学号
    sid_cross = students[students.duplicated(subset=['student_id'], keep=False)]
    sid_cross_groups = sid_cross.groupby('student_id')['group_no'].apply(
        lambda x: sorted(set(x))
    )
    sid_cross_multi = sid_cross_groups[sid_cross_groups.apply(len) > 1]
    print(f"\n  [学号跨组重复]: {len(sid_cross_multi)} 个学号在多个组中出现")
    for sid, groups in sid_cross_multi.head(10).items():
        print(f"    {sid}: 组 {groups}")

    if len(sid_cross_multi) > 0:
        findings.append({
            '类别': '重复值-学号跨组',
            '严重程度': '中',
            '描述': f'共 {len(sid_cross_multi)} 个学号在多个组中出现（跨组重复）',
            '详情': '不同组可能使用了相同的学号编码规则',
        })

    # --- 2b. 课程编号重复 ---
    cid_dup_within = courses[courses.duplicated(subset=['group_no', 'course_id'], keep=False)]
    cid_dup_count = cid_dup_within.groupby('group_no')['course_id'].nunique()
    print(f"\n  [课程编号组内重复]: {len(cid_dup_within)} 条涉及重复")
    for g, cnt in cid_dup_count.items():
        dup_cids = cid_dup_within[cid_dup_within['group_no'] == g]['course_id'].unique()
        print(f"    组{g}: {cnt} 个重复 → {dup_cids.tolist()}")

    if len(cid_dup_within) > 0:
        findings.append({
            '类别': '重复值-课程编号组内',
            '严重程度': '高',
            '描述': f'共 {len(cid_dup_within)} 条记录存在组内课程编号重复',
            '详情': f'涉及组: {sorted(cid_dup_count.index.tolist())}',
        })

    # 跨组重复课程编号
    cid_cross = courses[courses.duplicated(subset=['course_id'], keep=False)]
    cid_cross_groups = cid_cross.groupby('course_id')['group_no'].apply(
        lambda x: sorted(set(x))
    )
    cid_cross_multi = cid_cross_groups[cid_cross_groups.apply(len) > 1]
    print(f"\n  [课程编号跨组重复]: {len(cid_cross_multi)} 个课程编号在多个组中出现")
    for cid, groups in cid_cross_multi.head(10).items():
        print(f"    {cid}: 组 {groups}")

    # --- 2c. 选课记录重复 ---
    sc_dup = sc.duplicated(subset=['student_id', 'course_id'], keep=False)
    sc_dup_count = sc[sc_dup].groupby('group_no').size()
    print(f"\n  [选课记录重复]: {sc_dup.sum()} 条")
    if sc_dup.sum() > 0:
        for g, cnt in sc_dup_count.items():
            print(f"    组{g}: {cnt} 条重复")
        findings.append({
            '类别': '重复值-选课记录',
            '严重程度': '中',
            '描述': f'清洗后仍存在 {sc_dup.sum()} 条重复选课记录',
            '详情': f'涉及组: {sorted(sc_dup_count.index.tolist())}',
        })

    # --- 2d. 清洗前后对比 ---
    raw_sc_dup = raw_sc.duplicated(subset=['student_id', 'course_id']).sum()
    print(f"\n  [清洗效果]: 原始选课重复 {raw_sc_dup} 条 → 清洗后 {sc_dup.sum()} 条")

    return findings, sid_cross_multi, cid_cross_multi


# ============================================================
# 3. 格式异常检查
# ============================================================
def analyze_format_anomalies(data, all_groups):
    """
    格式异常检查：
    - 学号格式：长度、前缀模式、字符构成
    - 课程编号格式：长度、前缀模式
    - 性别字段异常值
    - 共享标志异常值
    """
    print("\n" + "=" * 70)
    print("3. 格式异常检查")
    print("=" * 70)

    students = data['students']
    courses = data['courses']
    sc = data['sc']

    findings = []
    format_profile = {}  # 存储各组格式画像，供可视化使用

    # --- 3a. 学号格式分析 ---
    print("\n  [学号格式按组分析]")
    sid_format = []
    for g in sorted(students['group_no'].unique()):
        g_df = students[students['group_no'] == g]
        ids = g_df['student_id'].astype(str)
        lengths = ids.str.len()
        # 提取前缀模式（前2-3个字符）
        has_alpha = ids.str.contains(r'[A-Za-z]').mean()
        has_digit = ids.str.contains(r'\d').mean()
        has_special = ids.str.contains(r'[^A-Za-z0-9]').mean()

        sid_format.append({
            'group_no': g,
            'count': len(g_df),
            'min_len': lengths.min(),
            'max_len': lengths.max(),
            'mean_len': round(lengths.mean(), 1),
            'unique_lengths': sorted(lengths.unique()),
            'has_alpha_pct': round(has_alpha * 100, 1),
            'has_special_pct': round(has_special * 100, 1),
            'samples': ids.head(3).tolist(),
        })

    sid_format_df = pd.DataFrame(sid_format)
    # 找出格式偏离大多数（长度中位数）的组
    median_len = sid_format_df['mean_len'].median()
    len_outliers = sid_format_df[
        abs(sid_format_df['mean_len'] - median_len) > 3
    ]['group_no'].tolist()

    print(f"  学号平均长度中位数: {median_len}")
    print(f"  长度偏离组: {len_outliers}")
    for _, row in sid_format_df.iterrows():
        flag = " [!]" if row['group_no'] in len_outliers else ""
        print(f"    组{int(row['group_no']):2d}: len=[{row['min_len']}-{row['max_len']}], "
              f"mean={row['mean_len']:.1f}, alpha={row['has_alpha_pct']:.0f}%, "
              f"special={row['has_special_pct']:.0f}%{flag}")

    # 含特殊字符的学号
    special_sid_groups = sid_format_df[sid_format_df['has_special_pct'] > 0]
    if len(special_sid_groups) > 0:
        findings.append({
            '类别': '格式异常-学号特殊字符',
            '严重程度': '低',
            '描述': f'共 {len(special_sid_groups)} 个组的学号包含特殊字符（如连字符）',
            '详情': f'涉及组: {special_sid_groups["group_no"].tolist()}，示例: 组14使用 "A14-S001" 格式',
        })

    findings.append({
        '类别': '格式异常-学号长度',
        '严重程度': '低',
        '描述': f'学号长度跨组差异大：范围 {sid_format_df["min_len"].min()}-{sid_format_df["max_len"].max()} 字符',
        '详情': f'最短组: {sid_format_df.loc[sid_format_df["mean_len"].idxmin(), "group_no"]} '
                f'({sid_format_df["mean_len"].min():.0f}字符), '
                f'最长组: {sid_format_df.loc[sid_format_df["mean_len"].idxmax(), "group_no"]} '
                f'({sid_format_df["mean_len"].max():.0f}字符)',
    })

    # --- 3b. 课程编号格式分析 ---
    print("\n  [课程编号格式按组分析]")
    cid_format = []
    for g in sorted(courses['group_no'].unique()):
        g_df = courses[courses['group_no'] == g]
        ids = g_df['course_id'].astype(str)
        lengths = ids.str.len()
        has_special = ids.str.contains(r'[^A-Za-z0-9]').mean()

        cid_format.append({
            'group_no': g,
            'count': len(g_df),
            'min_len': lengths.min(),
            'max_len': lengths.max(),
            'mean_len': round(lengths.mean(), 1),
            'has_special_pct': round(has_special * 100, 1),
            'samples': ids.head(3).tolist(),
        })

    cid_format_df = pd.DataFrame(cid_format)
    for _, row in cid_format_df.iterrows():
        print(f"    组{int(row['group_no']):2d}: len=[{row['min_len']}-{row['max_len']}], "
              f"mean={row['mean_len']:.1f}, special={row['has_special_pct']:.0f}%")

    # --- 3c. 其他字段格式检查 ---
    # 性别字段
    invalid_gender = students[~students['gender'].isin(['M', 'F'])]
    if len(invalid_gender) > 0:
        print(f"\n  [性别字段异常]: {len(invalid_gender)} 条非 M/F 值")
        findings.append({
            '类别': '格式异常-性别',
            '严重程度': '低',
            '描述': f'存在 {len(invalid_gender)} 条性别字段取值异常',
            '详情': f'异常值: {invalid_gender["gender"].unique().tolist()}',
        })

    # 共享标志
    invalid_share = courses[~courses['share_flag'].isin(['Y', 'N'])]
    if len(invalid_share) > 0:
        print(f"\n  [共享标志异常]: {len(invalid_share)} 条非 Y/N 值")
        findings.append({
            '类别': '格式异常-共享标志',
            '严重程度': '低',
            '描述': f'存在 {len(invalid_share)} 条 share_flag 取值异常',
            '详情': f'异常值: {invalid_share["share_flag"].unique().tolist()}',
        })

    # 学分异常
    if 'credit' in courses.columns:
        credit_outliers = courses[(courses['credit'] <= 0) | (courses['credit'] > 10)]
        if len(credit_outliers) > 0:
            findings.append({
                '类别': '格式异常-学分',
                '严重程度': '中',
                '描述': f'存在 {len(credit_outliers)} 条学分取值异常（≤0 或 >10）',
                '详情': f'涉及组: {sorted(credit_outliers["group_no"].unique().tolist())}',
            })

    format_profile = {
        'sid_format': sid_format_df,
        'cid_format': cid_format_df,
    }

    return findings, format_profile


# ============================================================
# 4. 数量异常检查
# ============================================================
def analyze_quantity_anomalies(data, all_groups):
    """
    数量异常检查：
    - 各组学生数、课程数、选课数
    - 偏离预期规模的组
    - 院系分布不均衡的组
    """
    print("\n" + "=" * 70)
    print("4. 数量异常检查")
    print("=" * 70)

    students = data['students']
    courses = data['courses']
    sc = data['sc']

    findings = []
    quant_stats = []  # 存储各组数量统计

    s_g = set(students['group_no'].unique())
    c_g = set(courses['group_no'].unique())
    sc_g = set(sc['group_no'].unique())

    for g in sorted(all_groups):
        s_cnt = len(students[students['group_no'] == g]) if g in s_g else 0
        c_cnt = len(courses[courses['group_no'] == g]) if g in c_g else 0
        sc_cnt = len(sc[sc['group_no'] == g]) if g in sc_g else 0

        # 各院系分布
        s_dept = students[students['group_no'] == g]['dept_no'].value_counts().to_dict() if g in s_g else {}
        c_dept = courses[courses['group_no'] == g]['dept_no'].value_counts().to_dict() if g in c_g else {}

        quant_stats.append({
            'group_no': g,
            'student_count': s_cnt,
            'course_count': c_cnt,
            'sc_count': sc_cnt,
            'sc_per_student': round(sc_cnt / s_cnt, 2) if s_cnt > 0 else 0,
            'course_per_student': round(c_cnt / s_cnt, 3) if s_cnt > 0 else 0,
            's_dept_A': s_dept.get('A', 0),
            's_dept_B': s_dept.get('B', 0),
            's_dept_C': s_dept.get('C', 0),
            'c_dept_A': c_dept.get('A', 0),
            'c_dept_B': c_dept.get('B', 0),
            'c_dept_C': c_dept.get('C', 0),
        })

    quant_df = pd.DataFrame(quant_stats)

    # 只对有三表数据的组做偏离分析
    full_data = quant_df[(quant_df['student_count'] > 0) & (quant_df['course_count'] > 0)]

    # 学生数偏离
    if len(full_data) > 0:
        median_s = full_data['student_count'].median()
        s_outliers = full_data[
            abs(full_data['student_count'] - median_s) > median_s * 0.2
        ]
        print(f"\n  [学生数偏离]: 中位数 {median_s:.0f}")
        for _, row in s_outliers.iterrows():
            deviation = (row['student_count'] - median_s) / median_s * 100
            print(f"    组{int(row['group_no'])}: {int(row['student_count'])} 人 "
                  f"(偏离 {deviation:+.0f}%)")

        if len(s_outliers) > 0:
            findings.append({
                '类别': '数量异常-学生数',
                '严重程度': '高',
                '描述': f'共 {len(s_outliers)} 个组学生数明显偏离中位数 {median_s:.0f}',
                '详情': ', '.join([
                    f"组{int(r['group_no'])}:{int(r['student_count'])}人"
                    for _, r in s_outliers.iterrows()
                ]),
            })

    # 课程数偏离
    if len(full_data) > 0:
        median_c = full_data['course_count'].median()
        c_outliers = full_data[
            abs(full_data['course_count'] - median_c) > median_c * 0.2
        ]
        print(f"\n  [课程数偏离]: 中位数 {median_c:.0f}")
        for _, row in c_outliers.iterrows():
            deviation = (row['course_count'] - median_c) / median_c * 100
            print(f"    组{int(row['group_no'])}: {int(row['course_count'])} 门 "
                  f"(偏离 {deviation:+.0f}%)")

        if len(c_outliers) > 0:
            findings.append({
                '类别': '数量异常-课程数',
                '严重程度': '高',
                '描述': f'共 {len(c_outliers)} 个组课程数明显偏离中位数 {median_c:.0f}',
                '详情': ', '.join([
                    f"组{int(r['group_no'])}:{int(r['course_count'])}门"
                    for _, r in c_outliers.iterrows()
                ]),
            })

    # 选课数偏离
    if len(full_data) > 0:
        median_sc = full_data['sc_count'].median()
        sc_outliers = full_data[
            abs(full_data['sc_count'] - median_sc) > median_sc * 0.2
        ]
        print(f"\n  [选课数偏离]: 中位数 {median_sc:.0f}")
        for _, row in sc_outliers.iterrows():
            deviation = (row['sc_count'] - median_sc) / median_sc * 100
            print(f"    组{int(row['group_no'])}: {int(row['sc_count'])} 条 "
                  f"(偏离 {deviation:+.0f}%)")

        if len(sc_outliers) > 0:
            findings.append({
                '类别': '数量异常-选课数',
                '严重程度': '高',
                '描述': f'共 {len(sc_outliers)} 个组选课数明显偏离中位数 {median_sc:.0f}',
                '详情': ', '.join([
                    f"组{int(r['group_no'])}:{int(r['sc_count'])}条"
                    for _, r in sc_outliers.iterrows()
                ]),
            })

    # 院系分布不均衡检查
    print("\n  [院系分布检查]")
    dept_imbalance = []
    for _, row in full_data.iterrows():
        s_vals = [row['s_dept_A'], row['s_dept_B'], row['s_dept_C']]
        if max(s_vals) > 0 and min(s_vals) / max(s_vals) < 0.8:
            dept_imbalance.append({
                'group_no': int(row['group_no']),
                'A': int(row['s_dept_A']),
                'B': int(row['s_dept_B']),
                'C': int(row['s_dept_C']),
            })
            print(f"    组{int(row['group_no'])}: A={int(row['s_dept_A'])}, "
                  f"B={int(row['s_dept_B'])}, C={int(row['s_dept_C'])} [!] 不均衡")

    if len(dept_imbalance) > 0:
        findings.append({
            '类别': '数量异常-院系分布',
            '严重程度': '中',
            '描述': f'共 {len(dept_imbalance)} 个组院系学生分布不均衡',
            '详情': str(dept_imbalance),
        })

    # 检查每组是否有3个院系
    print("\n  [院系覆盖检查]")
    for _, row in full_data.iterrows():
        s_depts = sum(1 for d in ['s_dept_A', 's_dept_B', 's_dept_C'] if row[d] > 0)
        c_depts = sum(1 for d in ['c_dept_A', 'c_dept_B', 'c_dept_C'] if row[d] > 0)
        if s_depts < 3 or c_depts < 3:
            print(f"    组{int(row['group_no'])}: 学生覆盖{s_depts}个院系, 课程覆盖{c_depts}个院系")

    print(f"\n  本组({OWN_GROUP}): {quant_df[quant_df['group_no']==OWN_GROUP].to_dict('records')}")

    return findings, quant_df


# ============================================================
# 5. 逻辑异常检查
# ============================================================
def analyze_logic_anomalies(data, all_groups):
    """
    逻辑异常检查：
    - 选课记录引用不存在的学生或课程
    - 跨组引用（某组的SC引用其他组的课程/学生）
    - 学生无选课记录
    - 课程无被选记录
    """
    print("\n" + "=" * 70)
    print("5. 逻辑异常检查")
    print("=" * 70)

    students = data['students']
    courses = data['courses']
    sc = data['sc']

    findings = []

    # --- 5a. 参照完整性（全库级别）---
    valid_sids = set(students['student_id'])
    valid_cids = set(courses['course_id'])
    sc_sids = set(sc['student_id'])
    sc_cids = set(sc['course_id'])

    orphan_sids = sc_sids - valid_sids
    orphan_cids = sc_cids - valid_cids

    print(f"  选课表中学号在学生表中不存在: {len(orphan_sids)}")
    print(f"  选课表中课程号在课程表中不存在: {len(orphan_cids)}")

    if len(orphan_sids) > 0:
        findings.append({
            '类别': '逻辑异常-孤立学号',
            '严重程度': '高',
            '描述': f'选课表中有 {len(orphan_sids)} 个学号在学生表中不存在',
            '详情': f'示例: {list(orphan_sids)[:10]}',
        })
    if len(orphan_cids) > 0:
        findings.append({
            '类别': '逻辑异常-孤立课程号',
            '严重程度': '高',
            '描述': f'选课表中有 {len(orphan_cids)} 个课程号在课程表中不存在',
            '详情': f'示例: {list(orphan_cids)[:10]}',
        })

    # --- 5b. 跨组引用分析 ---
    # 每组SC引用的课程号是否在本组课程表中
    print("\n  [跨组引用分析]")
    cross_refs = []
    for g in sorted(sc['group_no'].unique()):
        g_sc = sc[sc['group_no'] == g]
        g_courses = courses[courses['group_no'] == g]
        g_cids = set(g_courses['course_id'])
        sc_cids_g = set(g_sc['course_id'])

        internal = sc_cids_g & g_cids
        external = sc_cids_g - g_cids
        cross_rate = len(external) / len(sc_cids_g) * 100 if len(sc_cids_g) > 0 else 0

        if len(external) > 0:
            cross_refs.append({
                'group_no': g,
                'total_cids': len(sc_cids_g),
                'internal': len(internal),
                'external': len(external),
                'cross_rate': round(cross_rate, 1),
                'external_sample': list(external)[:5],
            })
            print(f"    组{g}: {len(external)}/{len(sc_cids_g)} 课程引用自其他组 "
                  f"({cross_rate:.1f}%), 示例: {list(external)[:3]}")

    if len(cross_refs) > 0:
        findings.append({
            '类别': '逻辑异常-跨组课程引用',
            '严重程度': '中',
            '描述': f'共 {len(cross_refs)} 个组的选课记录引用了其他组的课程',
            '详情': f'跨组引用率最高的组: {max(cross_refs, key=lambda x: x["cross_rate"])}',
        })

    # --- 5c. 学生无选课 ---
    sc_student_ids = set(sc['student_id'])
    no_sc_students = students[~students['student_id'].isin(sc_student_ids)]
    no_sc_by_group = no_sc_students.groupby('group_no').size()
    print(f"\n  [无选课记录的学生]: 共 {len(no_sc_students)} 人")
    for g, cnt in no_sc_by_group.items():
        total_g = len(students[students['group_no'] == g])
        print(f"    组{g}: {cnt}/{total_g} ({cnt/total_g*100:.1f}%)")

    if len(no_sc_students) > 0:
        findings.append({
            '类别': '逻辑异常-学生无选课',
            '严重程度': '中',
            '描述': f'共 {len(no_sc_students)} 名学生没有任何选课记录',
            '详情': f'涉及组: {sorted(no_sc_by_group.index.tolist())}',
        })

    # --- 5d. 课程无被选 ---
    sc_course_ids = set(sc['course_id'])
    no_sc_courses = courses[~courses['course_id'].isin(sc_course_ids)]
    no_sc_c_by_group = no_sc_courses.groupby('group_no').size()
    print(f"\n  [无被选记录的课程]: 共 {len(no_sc_courses)} 门")
    for g, cnt in no_sc_c_by_group.items():
        total_g = len(courses[courses['group_no'] == g])
        print(f"    组{g}: {cnt}/{total_g} ({cnt/total_g*100:.1f}%)")

    # --- 5e. 组19特殊分析：有SC无Course ---
    g19_sc = sc[sc['group_no'] == 19]
    if len(g19_sc) > 0:
        g19_courses_used = g19_sc['course_id'].unique()
        g19_course_sources = courses[courses['course_id'].isin(g19_courses_used)]
        g19_source_groups = g19_course_sources['group_no'].unique()
        print(f"\n  [组19特殊分析]: 有{len(g19_sc)}条选课但无本组课程")
        print(f"    使用的课程来自组: {sorted(g19_source_groups)}")
        findings.append({
            '类别': '逻辑异常-组19',
            '严重程度': '高',
            '描述': '组19有500条选课记录但无本组课程表，所有选课引用其他组的课程',
            '详情': f'课程来源组: {sorted(g19_source_groups)}',
        })

    # --- 5f. 本组逻辑检查 ---
    print(f"\n  [本组({OWN_GROUP})逻辑检查]")
    g16_sc = sc[sc['group_no'] == OWN_GROUP]
    g16_courses = courses[courses['group_no'] == OWN_GROUP]
    g16_students = students[students['group_no'] == OWN_GROUP]
    g16_cids = set(g16_courses['course_id'])
    g16_sc_cids = set(g16_sc['course_id'])
    g16_external = g16_sc_cids - g16_cids
    print(f"    跨组课程引用: {len(g16_external)} 个")
    g16_no_sc = g16_students[~g16_students['student_id'].isin(set(g16_sc['student_id']))]
    print(f"    无选课学生: {len(g16_no_sc)} 人")
    g16_no_enrolled = g16_courses[~g16_courses['course_id'].isin(g16_sc_cids)]
    print(f"    无被选课程: {len(g16_no_enrolled)} 门")

    # --- 5g. 成绩全为0（非NULL）检查 ---
    print("\n  [成绩全0检查（非NULL）]")
    zero_score_groups = []
    for g in sorted(sc['group_no'].unique()):
        g_sc = sc[sc['group_no'] == g]
        non_null = g_sc['score'].notnull()
        if non_null.sum() > 0 and (g_sc.loc[non_null, 'score'] == 0).all():
            zero_score_groups.append(g)
            print(f"    组{g}: {non_null.sum()}条非空成绩全部为0")
    if zero_score_groups:
        findings.append({
            '类别': '逻辑异常-成绩全0',
            '严重程度': '中',
            '描述': f'共 {len(zero_score_groups)} 个组成绩非空但全部为0（疑似占位数据）',
            '详情': f'组: {zero_score_groups}，这些组的成绩字段不为NULL但值全为0，建议按缺失值处理',
        })

    # --- 5h. 成绩分布异常集中检查 ---
    print("\n  [成绩分布异常集中检查]")
    concentrated_groups = []
    for g in sorted(sc['group_no'].unique()):
        g_sc = sc[sc['group_no'] == g]
        non_null_scores = g_sc['score'].dropna()
        if len(non_null_scores) >= 50:  # 至少50条有成绩才检查
            score_range = non_null_scores.max() - non_null_scores.min()
            score_std = non_null_scores.std()
            if score_std < 5 and score_range < 20:  # 标准差过小且范围窄
                concentrated_groups.append({
                    'group_no': g,
                    'count': len(non_null_scores),
                    'mean': round(non_null_scores.mean(), 1),
                    'std': round(score_std, 1),
                    'range': f"{int(non_null_scores.min())}-{int(non_null_scores.max())}",
                })
                print(f"    组{g}: 均值={non_null_scores.mean():.1f}, 标准差={score_std:.1f}, "
                      f"范围={int(non_null_scores.min())}-{int(non_null_scores.max())}")
    if concentrated_groups:
        findings.append({
            '类别': '逻辑异常-成绩分布集中',
            '严重程度': '中',
            '描述': f'共 {len(concentrated_groups)} 个组成绩分布异常集中（标准差<5）',
            '详情': str(concentrated_groups),
        })

    return findings, cross_refs, orphan_sids, orphan_cids


# ============================================================
# 6. 可视化
# ============================================================
def create_visualizations(data, coverage, sc_null_by_group, quant_df,
                          sid_format_df, cid_format_df, all_groups):
    """
    创建所有异常检测可视化图表
    """
    print("\n" + "=" * 70)
    print("生成可视化图表...")
    print("=" * 70)

    ensure_dir(FIGURES_DIR)

    students = data['students']
    courses = data['courses']
    sc = data['sc']

    # 计算成绩缺失组分类
    _full_null_groups = sc_null_by_group[sc_null_by_group['null_rate'] == 100]['group_no'].tolist()
    _partial_null_groups = sc_null_by_group[
        (sc_null_by_group['null_rate'] > 0) & (sc_null_by_group['null_rate'] < 100)
    ]['group_no'].tolist()

    # 配色方案
    PALETTE = sns.color_palette("Set2", 8)
    RED_PALETTE = sns.color_palette("Reds", 6)
    BLUE_PALETTE = sns.color_palette("Blues", 6)

    # ---- 图1: 各组数据完整度热力图 ----
    fig, ax = plt.subplots(figsize=(14, 6))
    coverage_plot = coverage.copy()
    coverage_plot.index.name = 'Group No.'

    # 用颜色表示完整度
    mask = ~coverage_plot[['Has Students', 'Has Courses', 'Has SC']]
    hm_data = coverage_plot[['Has Students', 'Has Courses', 'Has SC']].astype(int)
    sns.heatmap(hm_data.T, annot=True, fmt='d', cmap='RdYlGn',
                cbar=False, linewidths=0.5, linecolor='white',
                xticklabels=1, yticklabels=1, ax=ax)
    ax.set_title('Data Table Coverage by Group', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig1_data_coverage_heatmap.png'))
    plt.close(fig)
    print("  [OK] 图1: 各组数据表覆盖热力图")

    # ---- 图2: 各组学生/课程/选课数量分布（带异常高亮）----
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    quant_full = quant_df.copy()
    # 标记本组
    quant_full['is_own'] = quant_full['group_no'] == OWN_GROUP

    # 学生数
    colors_s = ['#e74c3c' if row['student_count'] == 0 or
                abs(row['student_count'] - EXPECTED_STUDENTS) > EXPECTED_STUDENTS * 0.3
                else '#2ecc71' if row['group_no'] == OWN_GROUP else '#3498db'
                for _, row in quant_full.iterrows()]
    axes[0].bar(quant_full['group_no'].astype(str), quant_full['student_count'], color=colors_s, alpha=0.85)
    axes[0].axhline(y=EXPECTED_STUDENTS, color='gray', linestyle='--', alpha=0.7, label=f'Expected({EXPECTED_STUDENTS})')
    axes[0].set_title('Student Count by Group', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Group No.')
    axes[0].set_ylabel('Student Count')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].legend(fontsize=8)

    # 课程数
    colors_c = ['#e74c3c' if row['course_count'] == 0 or
                abs(row['course_count'] - EXPECTED_COURSES) > EXPECTED_COURSES * 0.3
                else '#2ecc71' if row['group_no'] == OWN_GROUP else '#3498db'
                for _, row in quant_full.iterrows()]
    axes[1].bar(quant_full['group_no'].astype(str), quant_full['course_count'], color=colors_c, alpha=0.85)
    axes[1].axhline(y=EXPECTED_COURSES, color='gray', linestyle='--', alpha=0.7, label=f'Expected({EXPECTED_COURSES})')
    axes[1].set_title('Course Count by Group', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Group No.')
    axes[1].set_ylabel('Course Count')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].legend(fontsize=8)

    # 选课数
    colors_sc = ['#e74c3c' if row['sc_count'] == 0 or
                 abs(row['sc_count'] - EXPECTED_SC) > EXPECTED_SC * 0.3
                 else '#2ecc71' if row['group_no'] == OWN_GROUP else '#3498db'
                 for _, row in quant_full.iterrows()]
    axes[2].bar(quant_full['group_no'].astype(str), quant_full['sc_count'], color=colors_sc, alpha=0.85)
    axes[2].axhline(y=EXPECTED_SC, color='gray', linestyle='--', alpha=0.7, label=f'Expected({EXPECTED_SC})')
    axes[2].set_title('SC Count by Group', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Group No.')
    axes[2].set_ylabel('SC Record Count')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].legend(fontsize=8)

    fig.suptitle('Data Scale by Group (Red=Anomaly, Green=Own G16)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig2_quantity_distribution.png'))
    plt.close(fig)
    print("  [OK] 图2: 各组数量分布对比")

    # ---- 图3: 成绩缺失率按组分布 ----
    fig, ax = plt.subplots(figsize=(14, 5))
    merged = quant_df.merge(sc_null_by_group, on='group_no', how='left')
    merged['null_rate'] = merged['null_rate'].fillna(0 if merged['sc_count'].sum() > 0 else 100)

    bar_colors = ['#e74c3c' if r == 100 else '#f39c12' if r > 0 else '#2ecc71'
                  for r in merged['null_rate']]
    bars = ax.bar(merged['group_no'].astype(str), merged['null_rate'], color=bar_colors, alpha=0.85)
    ax.set_title('Score Null Rate by Group', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Score Null Rate (%)')
    ax.set_ylim(0, 110)
    ax.tick_params(axis='x', rotation=45)

    # 标注数值
    for bar, rate in zip(bars, merged['null_rate']):
        if rate > 0:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                    f'{rate:.0f}%', ha='center', va='bottom', fontsize=7)

    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#e74c3c', label='100% Null'),
        Patch(facecolor='#f39c12', label='Partial Null'),
        Patch(facecolor='#2ecc71', label='No Null'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig3_score_null_rate.png'))
    plt.close(fig)
    print("  [OK] 图3: 成绩缺失率分布")

    # ---- 图4: 学号/课程编号长度分布箱线图 ----
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # 为箱线图准备数据
    sid_len_data = {}
    for g in sorted(students['group_no'].unique()):
        g_df = students[students['group_no'] == g]
        sid_len_data[f'G{g}'] = g_df['student_id'].astype(str).str.len().values

    sid_box_data = [sid_len_data[k] for k in sorted(sid_len_data.keys(), key=lambda x: int(x.replace('G', '')))]
    sid_labels = sorted(sid_len_data.keys(), key=lambda x: int(x.replace('G', '')))

    bp1 = axes[0].boxplot(sid_box_data, labels=sid_labels, patch_artist=True,
                          showfliers=True, widths=0.6)
    for patch in bp1['boxes']:
        patch.set_facecolor('#3498db')
        patch.set_alpha(0.6)
    axes[0].set_title('Student ID Length Distribution by Group', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Group No.')
    axes[0].set_ylabel('Student ID Length (chars)')
    axes[0].tick_params(axis='x', rotation=45)

    # 课程编号长度
    cid_len_data = {}
    for g in sorted(courses['group_no'].unique()):
        g_df = courses[courses['group_no'] == g]
        cid_len_data[f'G{g}'] = g_df['course_id'].astype(str).str.len().values

    cid_box_data = [cid_len_data[k] for k in sorted(cid_len_data.keys(), key=lambda x: int(x.replace('G', '')))]
    cid_labels = sorted(cid_len_data.keys(), key=lambda x: int(x.replace('G', '')))

    bp2 = axes[1].boxplot(cid_box_data, labels=cid_labels, patch_artist=True,
                          showfliers=True, widths=0.6)
    for patch in bp2['boxes']:
        patch.set_facecolor('#e67e22')
        patch.set_alpha(0.6)
    axes[1].set_title('Course ID Length Distribution by Group', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Group No.')
    axes[1].set_ylabel('Course ID Length (chars)')
    axes[1].tick_params(axis='x', rotation=45)

    fig.suptitle('ID Format Difference Analysis by Group', fontsize=14, fontweight='bold')
    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig4_id_format_boxplot.png'))
    plt.close(fig)
    print("  [OK] 图4: 学号/课程编号格式箱线图")

    # ---- 图5: 缺失值热力图（字段×组） ----
    fig, ax = plt.subplots(figsize=(14, 8))

    # 构建缺失矩阵：各行=组，各列=关键字段
    missing_fields = {
        '学生-account': students.groupby('group_no')['account'].apply(lambda x: x.isnull().mean() * 100),
        '学生-password': students.groupby('group_no')['password'].apply(lambda x: x.isnull().mean() * 100),
        '选课-score': None,  # 稍后处理
    }

    # 成绩缺失率
    sc_null_rate_series = sc.groupby('group_no')['score'].apply(lambda x: x.isnull().mean() * 100)

    missing_matrix = pd.DataFrame(index=sorted(all_groups))
    missing_matrix['account Null%'] = students.groupby('group_no')['account'].apply(
        lambda x: x.isnull().mean() * 100
    ).reindex(sorted(all_groups)).fillna(100)  # 无数据的组视为100%缺失
    missing_matrix['password Null%'] = students.groupby('group_no')['password'].apply(
        lambda x: x.isnull().mean() * 100
    ).reindex(sorted(all_groups)).fillna(100)
    missing_matrix['score Null%'] = sc_null_rate_series.reindex(sorted(all_groups)).fillna(100)

    sns.heatmap(missing_matrix, annot=True, fmt='.0f', cmap='YlOrRd',
                linewidths=0.5, linecolor='white', ax=ax,
                vmin=0, vmax=100, cbar_kws={'label': 'Null Rate (%)'})
    ax.set_title('Key Field Null Rate Heatmap by Group', fontsize=14, fontweight='bold')
    ax.set_ylabel('Group No.')
    ax.set_xlabel('Field')

    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig5_missing_value_heatmap.png'))
    plt.close(fig)
    print("  [OK] 图5: 缺失值热力图")

    # ---- 图6: 各组异常评分总览 ----
    fig, ax = plt.subplots(figsize=(14, 6))

    # 计算各组异常评分
    anomaly_scores = pd.DataFrame(index=sorted(all_groups))
    anomaly_scores['Incomplete'] = anomaly_scores.index.map(
        lambda g: 0 if g in set(students['group_no'].unique()) & set(courses['group_no'].unique()) & set(sc['group_no'].unique()) else 1
    )
    anomaly_scores['Qty Anomaly'] = anomaly_scores.index.map(
        lambda g: 1 if (g in set(students['group_no'].unique()) and
                        abs(len(students[students['group_no'] == g]) - EXPECTED_STUDENTS) > EXPECTED_STUDENTS * 0.2)
                       or (g in set(courses['group_no'].unique()) and
                           abs(len(courses[courses['group_no'] == g]) - EXPECTED_COURSES) > EXPECTED_COURSES * 0.2)
                  else 0
    )
    anomaly_scores['Score All Null'] = anomaly_scores.index.map(
        lambda g: 1 if g in _full_null_groups else 0
    )
    anomaly_scores['Score Partial Null'] = anomaly_scores.index.map(
        lambda g: 1 if (g in _partial_null_groups) else 0
    )

    anomaly_scores['Total Score'] = anomaly_scores.sum(axis=1)
    # 本组高亮
    colors_total = ['#2ecc71' if g == OWN_GROUP else '#e74c3c' if s >= 3 else '#f39c12' if s >= 1 else '#3498db'
                    for g, s in zip(anomaly_scores.index, anomaly_scores['Total Score'])]
    ax.bar(anomaly_scores.index.astype(str), anomaly_scores['Total Score'], color=colors_total, alpha=0.85)
    ax.set_title('Anomaly Score Overview by Group', fontsize=14, fontweight='bold')
    ax.set_xlabel('Group No.')
    ax.set_ylabel('Anomaly Score')
    ax.tick_params(axis='x', rotation=45)

    # 标注
    for i, (g, score) in enumerate(zip(anomaly_scores.index, anomaly_scores['Total Score'])):
        if score > 0:
            ax.text(i, score + 0.1, str(int(score)), ha='center', fontsize=8)

    plt.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, 'fig6_anomaly_score_overview.png'))
    plt.close(fig)
    print("  [OK] 图6: 各组异常评分总览")

    print(f"\n  所有图表已保存至 {FIGURES_DIR}/")
    return 6  # 返回图表数量


# ============================================================
# 7. 生成异常检测报告
# ============================================================
def generate_report(data, findings, quant_df, coverage, all_groups, s_g, c_g, sc_g,
                    figure_count, sid_format_df, cid_format_df, sc_null_by_group):
    """
    生成异常检测Markdown报告
    """
    print("\n" + "=" * 70)
    print("生成异常检测报告...")
    print("=" * 70)

    students_groups = s_g
    courses_groups = c_g
    sc_groups = sc_g

    full_groups = sorted(students_groups & courses_groups & sc_groups)

    report = []
    report.append("# 异常数据检测报告")
    report.append(f"\n> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"> 分析组数: {len(all_groups)} 个组")
    report.append(f"> 本组组号: {OWN_GROUP}")
    report.append("")

    # ---- 总览 ----
    report.append("## 一、数据总览")
    report.append("")
    report.append(f"| 指标 | 数值 |")
    report.append(f"|------|------|")
    report.append(f"| 涉及总组数 | {len(all_groups)} |")
    report.append(f"| 三表齐全组数 | {len(full_groups)} |")
    report.append(f"| 缺少课程表组数 | {len(students_groups - courses_groups)} |")
    report.append(f"| 缺少选课表组数 | {len(students_groups - sc_groups)} |")
    report.append(f"| 学生表记录总数 | {len(data['students'])} |")
    report.append(f"| 课程表记录总数 | {len(data['courses'])} |")
    report.append(f"| 选课表记录总数 | {len(data['sc'])} |")
    report.append(f"| 成绩字段非空率 | {data['sc']['score'].notnull().sum()/len(data['sc'])*100:.1f}% |")
    report.append("")

    # ---- 异常清单 ----
    report.append("## 二、异常发现清单")
    report.append("")
    report.append("| 序号 | 类别 | 严重程度 | 描述 |")
    report.append("|------|------|----------|------|")
    for i, f in enumerate(findings, 1):
        severity_emoji = {'高': '[HIGH]', '中': '[MED]', '低': '[LOW]'}.get(f['严重程度'], '[NONE]')
        report.append(f"| {i} | {f['类别']} | {severity_emoji} {f['严重程度']} | {f['描述']} |")
    report.append("")

    # ---- 详细分析 ----
    report.append("## 三、详细分析")
    report.append("")

    # 3.1 数据完整性
    report.append("### 3.1 数据表覆盖情况")
    report.append("")
    report.append(f"共有 **{len(all_groups)}** 个组在数据库中留有数据，但并非所有组都上传了完整的三张表：")
    report.append("")
    report.append(f"- **三表齐全**: {len(full_groups)} 个组 — {full_groups}")
    only_student = sorted(students_groups - courses_groups - sc_groups)
    if only_student:
        report.append(f"- **仅有学生表**: {len(only_student)} 个组 — {only_student}（可能仅上传了部分数据）")
    student_sc_no_course = sorted((students_groups & sc_groups) - courses_groups)
    if student_sc_no_course:
        report.append(f"- **有学生表和选课表但无课程表**: {len(student_sc_no_course)} 个组 — {student_sc_no_course}")
    report.append("")

    # 3.2 缺失值
    report.append("### 3.2 缺失值分析")
    report.append("")
    report.append("#### 3.2.1 学生表字段缺失")
    report.append("")
    report.append("- **account / password**: 共 150 条缺失，涉及部分组。这些字段为登录凭证信息，不影响教务数据分析。")
    report.append("")
    report.append("#### 3.2.2 成绩缺失")
    report.append("")
    total_sc_null = data['sc']['score'].isnull().sum()
    report.append(f"选课表成绩字段共 **{total_sc_null}** 条缺失（占 {total_sc_null/len(data['sc'])*100:.1f}%）。")
    report.append("")
    report.append("**成绩完全缺失的组（100% NULL）**:")
    full_null_groups = sc_null_by_group[sc_null_by_group['null_rate'] == 100]['group_no'].tolist()
    for g in full_null_groups:
        report.append(f"- 组 {int(g)}")
    report.append("")
    report.append("**成绩部分缺失的组**:")
    partial_groups = sc_null_by_group[(sc_null_by_group['null_rate'] > 0) & (sc_null_by_group['null_rate'] < 100)]
    for _, row in partial_groups.iterrows():
        report.append(f"- 组 {int(row['group_no'])}: {int(row['null_count'])}/{int(row['total'])} ({row['null_rate']:.1f}%)")
    report.append("")

    # 3.3 数量异常
    report.append("### 3.3 数量异常")
    report.append("")
    report.append(f"最常见的标准规模为：{EXPECTED_STUDENTS} 学生 + {EXPECTED_COURSES} 课程 + {EXPECTED_SC} 选课。以下组偏离该模式：")
    report.append("")
    report.append("| 组号 | 学生数 | 课程数 | 选课数 | 异常说明 |")
    report.append("|------|--------|--------|--------|----------|")
    for _, row in quant_df.iterrows():
        anomalies = []
        if row['student_count'] > 0 and abs(row['student_count'] - EXPECTED_STUDENTS) > EXPECTED_STUDENTS * 0.2:
            anomalies.append(f"学生数异常({int(row['student_count'])})")
        if row['course_count'] > 0 and abs(row['course_count'] - EXPECTED_COURSES) > EXPECTED_COURSES * 0.2:
            anomalies.append(f"课程数异常({int(row['course_count'])})")
        if row['sc_count'] > 0 and abs(row['sc_count'] - EXPECTED_SC) > EXPECTED_SC * 0.2:
            anomalies.append(f"选课数异常({int(row['sc_count'])})")
        if row['student_count'] == 0 or row['course_count'] == 0:
            anomalies.append("数据不完整")

        if anomalies:
            report.append(f"| {int(row['group_no'])} | {int(row['student_count'])} | "
                          f"{int(row['course_count'])} | {int(row['sc_count'])} | "
                          f"{'; '.join(anomalies)} |")
    report.append("")

    # 3.4 格式异常
    report.append("### 3.4 格式差异分析")
    report.append("")
    report.append("各组学号和课程编号的编码格式存在显著差异，体现在长度和命名规则上：")
    report.append("")
    report.append("#### 学号格式")
    report.append("")
    report.append("| 组号 | 长度范围 | 平均长度 | 含字母 | 含特殊字符 | 示例 |")
    report.append("|------|----------|----------|--------|------------|------|")
    for _, row in sid_format_df.iterrows():
        report.append(f"| {int(row['group_no'])} | {row['min_len']}-{row['max_len']} | "
                      f"{row['mean_len']:.1f} | {row['has_alpha_pct']:.0f}% | "
                      f"{row['has_special_pct']:.0f}% | {row['samples'][0]} |")
    report.append("")

    report.append("#### 课程编号格式")
    report.append("")
    report.append("| 组号 | 长度范围 | 平均长度 | 含特殊字符 | 示例 |")
    report.append("|------|----------|----------|------------|------|")
    for _, row in cid_format_df.iterrows():
        report.append(f"| {int(row['group_no'])} | {row['min_len']}-{row['max_len']} | "
                      f"{row['mean_len']:.1f} | {row['has_special_pct']:.0f}% | "
                      f"{row['samples'][0]} |")
    report.append("")

    # 3.5 逻辑异常
    report.append("### 3.5 逻辑异常")
    report.append("")
    report.append("清洗后的数据已满足基本参照完整性（所有选课记录的学号和课程编号均能在主表中找到）。")
    report.append("但存在以下值得注意的跨组引用现象：部分组的选课记录引用了其他组的课程。")
    report.append("")

    report.append("")

    # ---- 建议 ----
    report.append("## 四、数据处理建议")
    report.append("")
    report.append("1. **数据不完整的组（9, 19, 25）**: 这些组缺少关键表，在进行组间统计分析和相似度计算时应予以排除或单独标记。")
    report.append("2. **成绩缺失处理**: 相似度计算中，成绩特征维度需考虑缺失情况。对成绩100%缺失的组（4, 19, 20），应跳过成绩相关特征。")
    report.append('3. **格式差异**: 学号和课程编号格式的差异反映了各组编码风格的不同，可作为相似度分析中的「编码风格」特征。')
    report.append("4. **组2特殊处理**: 组2数据规模远超其他组（374学生/312课程/4755选课），可能是按其他规格生成的数据，分析时需注意其特殊性。")
    report.append("5. **跨组引用**: 部分组选课记录引用其他组课程的现象，可能影响以组为单位的独立分析，建议在相似度计算中考虑课程独立性指标。")
    report.append("")

    # ---- 图表清单 ----
    report.append("## 五、可视化图表清单")
    report.append("")
    report.append("| 编号 | 图表名称 | 文件 | 说明 |")
    report.append("|------|----------|------|------|")
    report.append("| 图1 | 各组数据表覆盖热力图 | fig1_data_coverage_heatmap.png | 展示各表在各组中的存在情况 |")
    report.append("| 图2 | 各组数据规模对比 | fig2_quantity_distribution.png | 学生数/课程数/选课数分布，异常高亮 |")
    report.append("| 图3 | 成绩缺失率分布 | fig3_score_null_rate.png | 各组选课成绩缺失率柱状图 |")
    report.append("| 图4 | ID格式箱线图 | fig4_id_format_boxplot.png | 学号/课程编号长度分布箱线图 |")
    report.append("| 图5 | 缺失值热力图 | fig5_missing_value_heatmap.png | 各组关键字段缺失率热力图 |")
    report.append("| 图6 | 异常评分总览 | fig6_anomaly_score_overview.png | 各组综合异常评分 |")
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
    print("  异常数据检测脚本 - 作业四 成员3")
    print(f"  执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    ensure_dir(FIGURES_DIR)

    # 加载数据
    data = load_data()
    all_groups, s_g, c_g, sc_g = get_all_groups(data)

    # 1. 缺失值分析
    miss_findings, coverage, sc_null_by_group = analyze_missing_values(data, all_groups)

    # 2. 重复值检查
    dup_findings, sid_cross, cid_cross = analyze_duplicates(data, all_groups)

    # 3. 格式异常检查
    fmt_findings, format_profile = analyze_format_anomalies(data, all_groups)
    sid_format_df = format_profile['sid_format']
    cid_format_df = format_profile['cid_format']

    # 4. 数量异常检查
    quant_findings, quant_df = analyze_quantity_anomalies(data, all_groups)

    # 5. 逻辑异常检查
    logic_findings, cross_refs, orphan_sids, orphan_cids = analyze_logic_anomalies(data, all_groups)

    # 汇总所有发现
    all_findings = miss_findings + dup_findings + fmt_findings + quant_findings + logic_findings

    # 6. 生成可视化
    figure_count = create_visualizations(
        data, coverage, sc_null_by_group, quant_df,
        sid_format_df, cid_format_df, all_groups,
    )

    # 7. 生成报告
    report = generate_report(
        data, all_findings, quant_df, coverage, all_groups, s_g, c_g, sc_g,
        figure_count, sid_format_df, cid_format_df, sc_null_by_group,
    )

    # 汇总输出
    print("\n" + "=" * 70)
    print("  异常检测完成！")
    print(f"  - 共发现 {len(all_findings)} 个异常/问题")
    print(f"  - 生成 {figure_count} 张可视化图表")
    print(f"  - 报告: {REPORT_PATH}")
    print(f"  - 图表: {FIGURES_DIR}/")
    print("=" * 70)

    # 打印发现摘要
    print("\n  异常摘要:")
    for i, f in enumerate(all_findings, 1):
        sev = f['严重程度']
        print(f"    {i}. [{sev}] {f['类别']}: {f['描述'][:80]}...")


if __name__ == "__main__":
    main()
