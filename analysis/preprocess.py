#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os
from datetime import datetime

# 数据目录
DATA_DIR = './data'

class DataPreprocessor:
    """数据预处理类"""

    def __init__(self, data_dir=DATA_DIR):
        """
        初始化预处理器

        参数：
            data_dir: 数据文件所在目录
        """
        self.data_dir = data_dir
        self.students_df = None
        self.courses_df = None
        self.sc_df = None

    def load_data(self):
        """
        加载CSV数据文件
        """
        try:
            print("正在加载数据文件...")

            # 加载学生数据
            student_path = os.path.join(self.data_dir, 'students.csv')
            if os.path.exists(student_path):
                self.students_df = pd.read_csv(student_path)
                print(f"✓ 已加载 students.csv ({len(self.students_df)} 条记录)")
            else:
                print(f"✗ 文件不存在: {student_path}")

            # 加载课程数据
            course_path = os.path.join(self.data_dir, 'courses.csv')
            if os.path.exists(course_path):
                self.courses_df = pd.read_csv(course_path)
                print(f"✓ 已加载 courses.csv ({len(self.courses_df)} 条记录)")
            else:
                print(f"✗ 文件不存在: {course_path}")

            # 加载选课数据
            sc_path = os.path.join(self.data_dir, 'sc.csv')
            if os.path.exists(sc_path):
                self.sc_df = pd.read_csv(sc_path)
                print(f"✓ 已加载 sc.csv ({len(self.sc_df)} 条记录)")
            else:
                print(f"✗ 文件不存在: {sc_path}")

            print()
            return True

        except Exception as e:
            print(f"✗ 加载数据失败: {e}")
            return False

    def check_data_quality(self):
        """
        数据质量初步检查
        """
        print("=" * 80)
        print("数据质量检查")
        print("=" * 80)

        # 检查学生表
        if self.students_df is not None:
            print("\n【学生表 (student)】")
            self._check_table_quality(self.students_df, 'student')

        # 检查课程表
        if self.courses_df is not None:
            print("\n【课程表 (course)】")
            self._check_table_quality(self.courses_df, 'course')

        # 检查选课表
        if self.sc_df is not None:
            print("\n【选课表 (sc)】")
            self._check_table_quality(self.sc_df, 'sc')

    def _check_table_quality(self, df, table_name):
        """
        检查单个表的数据质量

        参数：
            df: DataFrame对象
            table_name: 表名
        """
        # 基本信息
        print(f"记录数: {len(df)}")
        print(f"字段数: {len(df.columns)}")
        print(f"字段列表: {', '.join(df.columns.tolist())}")

        # 检查缺失值
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print("\n缺失值统计：")
            for col, count in null_counts[null_counts > 0].items():
                percentage = (count / len(df)) * 100
                print(f"  - {col}: {count} ({percentage:.2f}%)")
        else:
            print("✓ 无缺失值")

        # 检查重复值
        if table_name == 'student':
            if 'student_id' in df.columns:
                dup_count = df['student_id'].duplicated().sum()
                print(f"\n重复学号数: {dup_count}")

        elif table_name == 'course':
            if 'course_id' in df.columns:
                dup_count = df['course_id'].duplicated().sum()
                print(f"\n重复课程编号数: {dup_count}")

        elif table_name == 'sc':
            if 'student_id' in df.columns and 'course_id' in df.columns:
                dup_count = df.duplicated(subset=['student_id', 'course_id']).sum()
                print(f"\n重复选课记录数: {dup_count}")

        # 数据类型
        print("\n数据类型：")
        for col, dtype in df.dtypes.items():
            print(f"  - {col}: {dtype}")

    def clean_students(self):
        """
        清洗学生表数据
        """
        if self.students_df is None:
            return

        print("\n正在清洗学生表数据...")
        df = self.students_df.copy()

        # 1. 处理缺失值
        # 根据实际情况，学号、姓名、性别不应为空
        original_count = len(df)
        df = df.dropna(subset=['student_id', 'student_name'])
        dropped_count = original_count - len(df)
        if dropped_count > 0:
            print(f"  - 删除学号或姓名为空的记录: {dropped_count}条")

        # 2. 字符串字段去除首尾空格
        str_columns = ['student_id', 'student_name', 'gender', 'department', 'account', 'password']
        for col in str_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 3. 性别字段统一格式
        if 'gender' in df.columns:
            # 将常见的性别表示统一为 M/F
            gender_mapping = {
                '男': 'M', 'Male': 'M', 'male': 'M', 'M': 'M', 'm': 'M',
                '女': 'F', 'Female': 'F', 'female': 'F', 'F': 'F', 'f': 'F'
            }
            df['gender'] = df['gender'].map(gender_mapping).fillna(df['gender'])
            print(f"  - 性别字段已统一格式")

        # 4. 组号和院系编号处理
        for col in ['group_no', 'dept_no']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        self.students_df = df
        print(f"✓ 学生表清洗完成，当前记录数: {len(df)}")

    def clean_courses(self):
        """
        清洗课程表数据
        """
        if self.courses_df is None:
            return

        print("\n正在清洗课程表数据...")
        df = self.courses_df.copy()

        # 1. 处理缺失值
        original_count = len(df)
        df = df.dropna(subset=['course_id', 'course_name'])
        dropped_count = original_count - len(df)
        if dropped_count > 0:
            print(f"  - 删除课程编号或课程名为空的记录: {dropped_count}条")

        # 2. 字符串字段去除首尾空格
        str_columns = ['course_id', 'course_name', 'teacher_name', 'location', 'share_flag']
        for col in str_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 3. 学分字段转换为数值类型
        if 'credit' in df.columns:
            df['credit'] = pd.to_numeric(df['credit'], errors='coerce')
            print(f"  - 学分字段已转换为数值类型")

        # 4. 课时字段转换为数值类型
        for col in ['class_hours', 'practice_hours']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 5. 共享标志统一格式（Y/N）
        if 'share_flag' in df.columns:
            share_mapping = {
                'Y': 'Y', 'y': 'Y', '1': 'Y', 'Yes': 'Y', 'yes': 'Y', '是': 'Y',
                'N': 'N', 'n': 'N', '0': 'N', 'No': 'N', 'no': 'N', '否': 'N'
            }
            df['share_flag'] = df['share_flag'].map(share_mapping).fillna(df['share_flag'])
            print(f"  - 共享标志已统一格式")

        # 6. 组号和院系编号处理
        for col in ['group_no', 'dept_no']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        self.courses_df = df
        print(f"✓ 课程表清洗完成，当前记录数: {len(df)}")

    def clean_sc(self):
        """
        清洗选课表数据
        """
        if self.sc_df is None:
            return

        print("\n正在清洗选课表数据...")
        df = self.sc_df.copy()

        # 1. 处理缺失值
        original_count = len(df)
        df = df.dropna(subset=['student_id', 'course_id'])
        dropped_count = original_count - len(df)
        if dropped_count > 0:
            print(f"  - 删除学号或课程编号为空的记录: {dropped_count}条")

        # 2. 字符串字段去除首尾空格
        str_columns = ['student_id', 'course_id']
        for col in str_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 3. 成绩字段转换为数值类型（可能为NULL）
        if 'score' in df.columns:
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
            null_score_count = df['score'].isnull().sum()
            print(f"  - 成绩字段已转换为数值类型（NULL数: {null_score_count}）")

        # 4. 组号和院系编号处理
        for col in ['group_no', 'dept_no']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # 5. 删除重复选课记录
        before_dedup = len(df)
        df = df.drop_duplicates(subset=['student_id', 'course_id'], keep='first')
        after_dedup = len(df)
        if before_dedup > after_dedup:
            print(f"  - 删除重复选课记录: {before_dedup - after_dedup}条")

        self.sc_df = df
        print(f"✓ 选课表清洗完成，当前记录数: {len(df)}")

    def validate_referential_integrity(self):
        """
        验证参照完整性
        """
        print("\n" + "=" * 80)
        print("参照完整性验证")
        print("=" * 80)

        if self.students_df is None or self.courses_df is None or self.sc_df is None:
            print("✗ 数据未完全加载，无法验证参照完整性")
            return

        # 获取有效的学号和课程编号集合
        valid_student_ids = set(self.students_df['student_id'].unique())
        valid_course_ids = set(self.courses_df['course_id'].unique())

        # 检查选课表中的学号
        sc_student_ids = set(self.sc_df['student_id'].unique())
        invalid_students = sc_student_ids - valid_student_ids
        if len(invalid_students) > 0:
            print(f"✗ 选课表中有 {len(invalid_students)} 个学号在学生表中不存在")
            print(f"  示例: {list(invalid_students)[:5]}")
        else:
            print("✓ 所有选课记录的学号在学生表中都存在")

        # 检查选课表中的课程编号
        sc_course_ids = set(self.sc_df['course_id'].unique())
        invalid_courses = sc_course_ids - valid_course_ids
        if len(invalid_courses) > 0:
            print(f"✗ 选课表中有 {len(invalid_courses)} 个课程编号在课程表中不存在")
            print(f"  示例: {list(invalid_courses)[:5]}")
        else:
            print("✓ 所有选课记录的课程编号在课程表中都存在")

    def save_cleaned_data(self):
        """
        保存清洗后的数据
        """
        print("\n" + "=" * 80)
        print("保存清洗后的数据")
        print("=" * 80)

        # 创建cleaned子目录
        cleaned_dir = os.path.join(self.data_dir, 'cleaned')
        os.makedirs(cleaned_dir, exist_ok=True)

        # 保存学生数据
        if self.students_df is not None:
            output_path = os.path.join(cleaned_dir, 'students_cleaned.csv')
            self.students_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✓ 已保存: {output_path}")

        # 保存课程数据
        if self.courses_df is not None:
            output_path = os.path.join(cleaned_dir, 'courses_cleaned.csv')
            self.courses_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✓ 已保存: {output_path}")

        # 保存选课数据
        if self.sc_df is not None:
            output_path = os.path.join(cleaned_dir, 'sc_cleaned.csv')
            self.sc_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✓ 已保存: {output_path}")

        print(f"\n所有清洗后的数据已保存至: {cleaned_dir}/")

    def generate_summary_report(self):
        """
        生成数据预处理汇总报告
        """
        print("\n" + "=" * 80)
        print("数据预处理汇总报告")
        print("=" * 80)

        report_lines = []
        report_lines.append("# 数据预处理汇总报告")
        report_lines.append(f"\n生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"\n## 1. 数据概览\n")

        if self.students_df is not None:
            report_lines.append(f"### 学生表 (student)")
            report_lines.append(f"- 记录数：{len(self.students_df)}")
            report_lines.append(f"- 涉及组数：{self.students_df['group_no'].nunique() if 'group_no' in self.students_df.columns else 'N/A'}")
            report_lines.append(f"- 涉及院系：{self.students_df['dept_no'].nunique() if 'dept_no' in self.students_df.columns else 'N/A'}")

        if self.courses_df is not None:
            report_lines.append(f"\n### 课程表 (course)")
            report_lines.append(f"- 记录数：{len(self.courses_df)}")
            report_lines.append(f"- 涉及组数：{self.courses_df['group_no'].nunique() if 'group_no' in self.courses_df.columns else 'N/A'}")
            report_lines.append(f"- 涉及院系：{self.courses_df['dept_no'].nunique() if 'dept_no' in self.courses_df.columns else 'N/A'}")

        if self.sc_df is not None:
            report_lines.append(f"\n### 选课表 (sc)")
            report_lines.append(f"- 记录数：{len(self.sc_df)}")
            report_lines.append(f"- 涉及组数：{self.sc_df['group_no'].nunique() if 'group_no' in self.sc_df.columns else 'N/A'}")
            report_lines.append(f"- 涉及院系：{self.sc_df['dept_no'].nunique() if 'dept_no' in self.sc_df.columns else 'N/A'}")

        report_lines.append(f"\n## 2. 数据清洗说明\n")
        report_lines.append("### 学生表")
        report_lines.append("- 删除学号或姓名为空的记录")
        report_lines.append("- 字符串字段去除首尾空格")
        report_lines.append("- 性别字段统一为 M/F 格式")
        report_lines.append("- 组号和院系编号格式统一")

        report_lines.append("\n### 课程表")
        report_lines.append("- 删除课程编号或课程名为空的记录")
        report_lines.append("- 字符串字段去除首尾空格")
        report_lines.append("- 学分、课时字段转换为数值类型")
        report_lines.append("- 共享标志统一为 Y/N 格式")
        report_lines.append("- 组号和院系编号格式统一")

        report_lines.append("\n### 选课表")
        report_lines.append("- 删除学号或课程编号为空的记录")
        report_lines.append("- 字符串字段去除首尾空格")
        report_lines.append("- 成绩字段转换为数值类型（保留NULL）")
        report_lines.append("- 删除重复选课记录")
        report_lines.append("- 组号和院系编号格式统一")

        report_content = "\n".join(report_lines)
        print(report_content)

        # 保存报告文件
        report_path = os.path.join(self.data_dir, 'preprocessing_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n报告已保存至: {report_path}")


def main():
    """
    主函数：执行完整的数据预处理流程
    """
    print("=" * 80)
    print("数据预处理脚本 - 作业四 16组")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 创建预处理器实例
    preprocessor = DataPreprocessor()

    # 加载数据
    if not preprocessor.load_data():
        print("程序终止：数据加载失败")
        return

    # 数据质量检查
    preprocessor.check_data_quality()

    # 数据清洗
    print("\n" + "=" * 80)
    print("开始数据清洗")
    print("=" * 80)

    preprocessor.clean_students()
    preprocessor.clean_courses()
    preprocessor.clean_sc()

    # 参照完整性验证
    preprocessor.validate_referential_integrity()

    # 保存清洗后的数据
    preprocessor.save_cleaned_data()

    # 生成汇总报告
    preprocessor.generate_summary_report()

    print("\n✓ 数据预处理任务完成！")


if __name__ == "__main__":
    main()
