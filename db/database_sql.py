
import sqlite3
import json
import os

def get_db_type_by_tag(tag: str = "str"):
    return {"str": "TEXT", "int": "INTEGER", "float": "DOUBLE"}.get(tag, "TEXT")


def create(db_path: str = "form_id", db_columns: list = [{"type": "str", "column_name": "A1"}]):

    colunms_string = ",".join(["{} {}".format(
        c["column_name"], get_db_type_by_tag(c["type"])) for c in db_columns])
    create_string = "CREATE TABLE sheet (id INTEGER PRIMARY KEY AUTOINCREMENT,{});".format(
        colunms_string)
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 创建游标
    cs = conn.cursor()
    try:
        # 创建表
        print(create_string)
        cs.execute(create_string)
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        # 关闭 Cursor
        cs.close()
        # 提交当前事务
        conn.commit()
        # 关闭连接
        conn.close()


def insert(db_path: str = "form_id", row: dict = {"A2": "AA"}):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    placeholder = ",".join(len(row.keys())*"?")
    db_string = "INSERT INTO sheet ({}) VALUES ({})".format(
        ",".join(row.keys()), placeholder)
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 创建游标
    cs = conn.cursor()

    try:
        # 创建表
        print(db_string, list(row.values()))
        cs.execute(db_string, list(row.values()))
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        # 关闭 Cursor
        cs.close()
        # 提交当前事务
        conn.commit()
        # 关闭连接
        conn.close()


def rows(db_path: str = "form_id", offset=0, limit=10):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    db_string = "SELECT * FROM sheet LIMIT {} OFFSET {};".format(limit, offset)
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 返回 dict 结果，而不是 list
    conn.row_factory = sqlite3.Row
    # 创建游标
    cs = conn.cursor()

    try:
        print(db_string)
        c = cs.execute(db_string)
        return 200, c.fetchall()
    except Exception as e:
        return 500, str(e)
    finally:
        # 关闭 Cursor
        cs.close()
        # 提交当前事务
        conn.commit()
        # 关闭连接
        conn.close()


def row_by_id(db_path: str = "form_id", row_id = 0):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    db_string = "SELECT * FROM sheet WHERE id = {};".format(row_id)
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 返回 dict 结果，而不是 list
    conn.row_factory = sqlite3.Row
    # 创建游标
    cs = conn.cursor()

    try:
        # 创建表
        print(db_string)
        c = cs.execute(db_string)
        return 200, c.fetchall()
    except Exception as e:
        return 500, str(e)
    finally:
        # 关闭 Cursor
        cs.close()
        # 提交当前事务
        conn.commit()
        # 关闭连接
        conn.close()

def update(db_path: str = "form_id", row_id=0, row: dict = {"A2": "AA"}):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    db_string = "UPDATE sheet SET {} WHERE id = {}".format(
        " = ? , ".join(row.keys())+" = ? ", row_id)
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 创建游标
    cs = conn.cursor()

    try:
        # 创建表
        print(db_string, list(row.values()))
        cs.execute(db_string, list(row.values()))
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        # 关闭 Cursor
        cs.close()
        # 提交当前事务
        conn.commit()
        # 关闭连接
        conn.close()


def delete(db_path: str = "form_id", row_id=0):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    db_string = "DELETE FROM sheet WHERE id = {}".format(row_id)
    # 连接数据库
    conn = sqlite3.connect(db_path)
    # 创建游标
    cs = conn.cursor()

    try:
        # 创建表
        print(db_string)
        cs.execute(db_string)
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        # 关闭 Cursor
        cs.close()
        # 提交当前事务
        conn.commit()
        # 关闭连接
        conn.close()
