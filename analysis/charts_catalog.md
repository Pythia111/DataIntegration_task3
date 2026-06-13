# 📊 数据可视化图表目录

> 生成时间: 2026-06-13 13:16:28
> 生成脚本: `visualization.py` (成员5)
> 图表数量: 14 张
> 输出目录: `analysis/figures/`
> 格式: PNG, 300dpi
> 中文字体: 未找到（使用英文）

---

## 图表分类索引

### 规模对比 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v1_scale_dashboard | Group Data Scale Overview Dashboard | 2×2子图仪表盘（柱状图） |

### 结构特征 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v2_dept_distribution | Department Distribution by Group | 堆叠柱状图 |

### 共享特征 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v3_share_ratio | Shared Course Ratio by Group | 水平条形图 |

### 性别特征 (2张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v4_gender_ratio | Gender Ratio by Group | 分组条形图 |
| fig_v5_gender_pie | Gender Ratio Pie Charts | 多饼图阵列 |

### 相似度分析 (3张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v6_similarity_heatmap | Inter-Group Similarity Heatmap | 热力图 |
| fig_v7_radar_comparison | Radar Chart: Own vs Most Similar Group | 雷达图/蜘蛛图 |
| fig_v8_similarity_ranking | Similarity Ranking to Own Group | 水平条形图 |

### 格式特征 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v9_id_format | Group ID Format Difference Analysis | 箱线图 |

### 内容特征 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v10_credit_distribution | Credit Distribution Analysis by Group | 柱状图 |

### 成绩特征 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v11_score_analysis | Score Data Quality & Distribution | 组合图（柱状图+误差线） |

### 异常检测 (1张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v12_anomaly_overview | Data Anomaly & Completeness Overview | 组合图（柱状图+饼图） |

### 综合分析 (2张)

| 编号 | 标题 | 类型 |
|------|------|------|
| fig_v13_feature_heatmap | Group Feature Profile Heatmap | 热力图 |
| fig_v14_scale_bubble | Group Scale Bubble Chart | 气泡散点图 |

---

## 图表详细说明

### 1. Group Data Scale Overview Dashboard

- **文件**: `fig_v1_scale_dashboard.png`
- **类型**: 2×2子图仪表盘（柱状图）
- **类别**: 规模对比
- **说明**: 2×2 dashboard comparing student count, course count, SC record count, and SC per student across all groups.

### 2. Department Distribution by Group

- **文件**: `fig_v2_dept_distribution.png`
- **类型**: 堆叠柱状图
- **类别**: 结构特征
- **说明**: Stacked bar charts showing student and course distribution across departments A/B/C for each group.

### 3. Shared Course Ratio by Group

- **文件**: `fig_v3_share_ratio.png`
- **类型**: 水平条形图
- **类别**: 共享特征
- **说明**: Horizontal bar chart showing the proportion of shared courses (Y flag) per group.

### 4. Gender Ratio by Group

- **文件**: `fig_v4_gender_ratio.png`
- **类型**: 分组条形图
- **类别**: 性别特征
- **说明**: Grouped bar chart showing male (blue) and female (red) ratio per group. Own group highlighted.

### 5. Gender Ratio Pie Charts

- **文件**: `fig_v5_gender_pie.png`
- **类型**: 多饼图阵列
- **类别**: 性别特征
- **说明**: Pie chart array for selected groups showing male/female split.

### 6. Inter-Group Similarity Heatmap

- **文件**: `fig_v6_similarity_heatmap.png`
- **类型**: 热力图
- **类别**: 相似度分析
- **说明**: Heatmap of combined similarity (cosine 50% + euclidean 50%). Greener = more similar.

### 7. Radar Chart: Own vs Most Similar Group

- **文件**: `fig_v7_radar_comparison.png`
- **类型**: 雷达图/蜘蛛图
- **类别**: 相似度分析
- **说明**: 8-dimension radar chart comparing own group (green) with most similar group (orange).

### 8. Similarity Ranking to Own Group

- **文件**: `fig_v8_similarity_ranking.png`
- **类型**: 水平条形图
- **类别**: 相似度分析
- **说明**: Horizontal bar chart ranking groups by combined similarity to own group.

### 9. Group ID Format Difference Analysis

- **文件**: `fig_v9_id_format.png`
- **类型**: 箱线图
- **类别**: 格式特征
- **说明**: Box plots of student ID length (top) and course ID length (bottom) by group.

### 10. Credit Distribution Analysis by Group

- **文件**: `fig_v10_credit_distribution.png`
- **类型**: 柱状图
- **类别**: 内容特征
- **说明**: Average credit (left) and credit std dev (right) by group.

### 11. Score Data Quality & Distribution

- **文件**: `fig_v11_score_analysis.png`
- **类型**: 组合图（柱状图+误差线）
- **类别**: 成绩特征
- **说明**: Score availability rate (left) and score distribution with mean/std/range for scored groups (right).

### 12. Data Anomaly & Completeness Overview

- **文件**: `fig_v12_anomaly_overview.png`
- **类型**: 组合图（柱状图+饼图）
- **类别**: 异常检测
- **说明**: Anomaly score bar chart + data completeness pie chart.

### 13. Group Feature Profile Heatmap

- **文件**: `fig_v13_feature_heatmap.png`
- **类型**: 热力图
- **类别**: 综合分析
- **说明**: Normalized feature heatmap with 10 dimensions across all analyzable groups.

### 14. Group Scale Bubble Chart

- **文件**: `fig_v14_scale_bubble.png`
- **类型**: 气泡散点图
- **类别**: 综合分析
- **说明**: Bubble scatter plot: students vs courses, bubble size = SC count.

---

## 统一配色方案

| 颜色 | 色值 | 用途 |
|------|------|------|
| 🟢 翠绿 | `#27ae60` | 本组(16)标识 |
| 🟠 橙色 | `#e67e22` | 最相似组标识 |
| 🔵 浅蓝 | `#5dade2` | 其他正常组 |
| 🔴 红色 | `#e74c3c` | 异常/严重问题 |
| 🟡 黄色 | `#f39c12` | 轻微异常/警告 |
| ⚪ 灰色 | `#bdc3c7` | 数据不完整组 |

| 院系 | 颜色 | 色值 |
|------|------|------|
| A院 | 🔵 蓝色 | `#3498db` |
| B院 | 🔴 红色 | `#e74c3c` |
| C院 | 🟢 绿色 | `#2ecc71` |

---

## 使用说明

### 运行方式

```bash
cd analysis/
python visualization.py
```

### 依赖

- pandas, numpy — 数据处理
- matplotlib, seaborn — 可视化
- scikit-learn — 相似度计算（可选，不影响基础图表）

### 输入数据

- `data/cleaned/students_cleaned.csv`
- `data/cleaned/courses_cleaned.csv`
- `data/cleaned/sc_cleaned.csv`

### 输出

- 14 张 PNG 图表 → `analysis/figures/`
- 本目录文件 → `analysis/charts_catalog.md`
