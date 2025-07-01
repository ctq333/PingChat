#!/usr/bin/env python3
"""
数据库迁移脚本：为 users 表添加 is_muted 字段
"""

import os
import sys
from dotenv import load_dotenv
import pymysql

# 加载环境变量
load_dotenv()

def migrate_add_muted_field():
    """为 users 表添加 is_muted 字段"""
    
    # 数据库连接配置
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
    MYSQL_DB = os.environ.get('MYSQL_DB', 'test')
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'is_muted'
        """, (MYSQL_DB,))
        
        if cursor.fetchone():
            print("字段 is_muted 已存在，跳过迁移")
        else:
            # 添加 is_muted 字段
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN is_muted BOOLEAN DEFAULT FALSE
            """)
            connection.commit()
            print("成功添加 is_muted 字段到 users 表")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"迁移失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_add_muted_field()
    print("迁移完成！") 