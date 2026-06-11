#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
import pandas as pd
import os
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': '10.60.254.44',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'hw4',
    'charset': 'utf8mb4'
}

# 输出目录
OUTPUT_DIR = './data'

def connect_database():
    """
    建立数据库连接
    返回：connection对象，如果连接失败则返回None
    """
    try:
        print(f"正在连接数据库 {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset']
        )
        print("✓ 数据库连接成功")
        return connection
    except pymysql.Error as e:
        print(f"✗ 数据库连接失败: {e}")
        return None

def fetch_table_data(connection, table_name):
    """
    从指定表提取全量数据

    参数：
        connection: 数据库连接对象
        table_name: 表名（student/course/sc）

    返回：
        DataFrame对象，包含表的全量数据
    """
    try:
        print(f"\n正在提取表 '{table_name}' 的数据...")
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, connection)
        print(f"✓ 成功提取 {len(df)} 条记录")

        # 显示基本信息
        print(f"  - 字段数：{len(df.columns)}")
        print(f"  - 字段列表：{', '.join(df.columns.tolist())}")

        # 统计各组数据量
        if 'group_no' in df.columns:
            group_counts = df['group_no'].value_counts().sort_index()
            print(f"  - 各组数据量：")
            for group, count in group_counts.items():
                print(f"    组{group}: {count}条")

        return df
    except pymysql.Error as e:
        print(f"✗ 提取表 '{table_name}' 数据失败: {e}")
        return None

def export_to_csv(df, filename):
    """
    将DataFrame导出为CSV文件

    参数：
        df: DataFrame对象
        filename: 输出文件名
    """
    try:
        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        filepath = os.path.join(OUTPUT_DIR, filename)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')  # 使用utf-8-sig便于Excel打开
        print(f"✓ 数据已导出至: {filepath}")

        # 显示文件大小
        file_size = os.path.getsize(filepath)
        print(f"  文件大小: {file_size/1024:.2f} KB")

    except Exception as e:
        print(f"✗ 导出CSV文件失败: {e}")

def get_table_structure(connection, table_name):
    """
    获取表结构信息

    参数：
        connection: 数据库连接对象
        table_name: 表名

    返回：
        DataFrame对象，包含表结构信息
    """
    try:
        query = f"DESCRIBE {table_name}"
        structure = pd.read_sql(query, connection)
        return structure
    except pymysql.Error as e:
        print(f"获取表 '{table_name}' 结构失败: {e}")
        return None

def display_data_preview(df, table_name, n=5):
    """
    显示数据预览

    参数：
        df: DataFrame对象
        table_name: 表名
        n: 显示前n条记录
    """
    print(f"\n表 '{table_name}' 数据预览（前{n}条）：")
    print("-" * 80)
    print(df.head(n).to_string())
    print("-" * 80)

def main():
    """
    主函数：执行完整的数据获取流程
    """
    print("=" * 80)
    print("数据获取脚本 - 作业四 16组")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 建立数据库连接
    connection = connect_database()
    if connection is None:
        print("\n程序终止：无法连接到数据库")
        print("提示：请确保您在校园网环境下，或已连接VPN")
        return

    try:
        # 定义需要提取的表
        tables = {
            'student': 'students.csv',
            'course': 'courses.csv',
            'sc': 'sc.csv'
        }

        # 存储所有数据
        all_data = {}

        # 逐个提取表数据
        for table_name, csv_filename in tables.items():
            # 获取表结构
            structure = get_table_structure(connection, table_name)
            if structure is not None:
                print(f"\n表 '{table_name}' 结构：")
                print(structure.to_string(index=False))

            # 提取数据
            df = fetch_table_data(connection, table_name)
            if df is not None:
                all_data[table_name] = df

                # 显示数据预览
                display_data_preview(df, table_name)

                # 导出为CSV
                export_to_csv(df, csv_filename)

        # 汇总统计
        print("\n" + "=" * 80)
        print("数据提取汇总")
        print("=" * 80)
        for table_name, df in all_data.items():
            print(f"\n表 '{table_name}':")
            print(f"  - 总记录数: {len(df)}")
            print(f"  - 字段数: {len(df.columns)}")
            if 'group_no' in df.columns:
                unique_groups = df['group_no'].nunique()
                print(f"  - 涉及组数: {unique_groups}")
            if 'dept_no' in df.columns:
                unique_depts = df['dept_no'].nunique()
                print(f"  - 涉及院系: {unique_depts}")

        print("\n✓ 数据获取任务完成！")
        print(f"所有数据已导出至: {OUTPUT_DIR}/")

    except Exception as e:
        print(f"\n✗ 执行过程中出现错误: {e}")

    finally:
        # 关闭数据库连接
        if connection:
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()
