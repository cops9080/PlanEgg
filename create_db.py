import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("데이터베이스 연결 성공!")
try:
    # 퀘스트 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_name TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            time_duration INTEGER NOT NULL,
            coin INTEGER NOT NULL,
            exp INTEGER NOT NULL,
            status INTEGER DEFAULT 0
        )
     """)

    # 유저 스탯 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lvl INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            coin INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    print("테이블 생성 완료 및 저장 완료!")

except sqlite3.OperationalError as e:
    print(f"테이블 생성 오류: {e}")

finally:
    conn.close()