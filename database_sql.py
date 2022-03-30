
import os
import time
import sqlite3



IS_DEBUG = True


def debug(*args, **kwargs):
    if IS_DEBUG:
        print(*args, **kwargs)


def get_timestamp():
    return round(time.time()*1000)


def get_sqlite_column_type_by_short_tag(tag: str = "Str") -> str:
    """
    @tag in ["Str","Int","Float"]
    """
    return {"str": "TEXT", "int": "INTEGER", "float": "DOUBLE"}.get(tag, "TEXT")



def create_table(db_path: str = "", db_columns: dict = {}):
    #  db_columns {"from":{"type": str,"name": str,"link_to": str}}
    debug(db_path, db_columns)
    # 获取数据库标头，构造 SQL
    colunms_string = ", ".join(
        ["{} {}".format(
            c["link_to"], get_sqlite_column_type_by_short_tag(c["type"])
        ) for c in db_columns.values()]
    )
    # 创建数据表之时，追加一个 update_at 和 update_by 字段，查询时提供，但更新或保存时不需要提供，由系统自动更新。
    create_string = "CREATE TABLE sheet ({}, update_at INTEGER, update_by TEXT);".format(
        colunms_string)
    debug(create_string)
    conn = sqlite3.connect(db_path)
    cs = conn.cursor()
    try:
        cs.execute(create_string)
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()


def insert_row(db_path: str = "form_id", subuser_id: str = "", row: dict = {"A2": "AA"}):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"
    # 更新或保存时不需要提供，由系统自动更新 update_at 字段，并预留 update_by 字段
    update_by = subuser_id
    update_at = get_timestamp()


    placeholder = ",".join((len(row.keys())+2)*"?")
    db_string = "INSERT INTO sheet ({}) VALUES ({})".format(
        ",".join(list(row.keys())+["update_at", "update_by"]), placeholder
    )
    db_values = list(row.values())+[update_at, update_by]
    debug(db_string, db_values)

    conn = sqlite3.connect(db_path)
    cs = conn.cursor()
    try:
        cs.execute(db_string, db_values)
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()



def update_row(db_path: str = "form_id", subuser_id: str = "",row_id:int=0 ,row: dict = {"A2": "AA"}):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"
    # 更新或保存时不需要提供，由系统自动更新 update_at 字段，并预留 update_by 字段
    update_by = subuser_id
    update_at = get_timestamp()

    db_keys = list(row.keys())+["update_at", "update_by"]
    db_values = list(row.values())+[update_at, update_by]

    db_string = "UPDATE sheet SET {} WHERE rowid = {}".format(
        " = ? , ".join(db_keys)+" = ? ", row_id)

    debug(db_string, db_values)

    conn = sqlite3.connect(db_path)
    cs = conn.cursor()
    try:
        cs.execute(db_string, db_values)
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()




def delete_row(db_path: str = "form_id", subuser_id: str = "", row_id:int=0):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    db_string = "DELETE FROM sheet WHERE rowid = ? AND update_by = ?"
    conn = sqlite3.connect(db_path)
    cs = conn.cursor()

    try:
        debug(db_string)
        cs.execute(db_string,[row_id,subuser_id,])
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()


def delete_rows(db_path: str = "form_id", subuser_id: str = "", row_ids:list=[0,]):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"
    rows_string = ",".join(row_ids)
    db_string = "DELETE FROM sheet WHERE rowid in ({}) AND update_by = ?".format(rows_string)
    conn = sqlite3.connect(db_path)
    cs = conn.cursor()

    try:
        debug(db_string,subuser_id)
        cs.execute(db_string,[subuser_id,])
        return 200, ""
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()


def get_subuser_rows(db_path: str = "form_id", subuser_id: str = "" ,offset=0, limit=10000):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    # 显式的指定。例如，select rowid, * from tablename 获取 rowid 列
    db_string = "SELECT rowid,* FROM sheet WHERE update_by = ? LIMIT {} OFFSET {};".format(limit, offset)
    debug(db_string,subuser_id)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cs = conn.cursor()
    try:
        c = cs.execute(db_string,[subuser_id,])
        return 200, c.fetchall()
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()


def get_row_by_rowid(db_path: str = "form_id", row_id=0):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    db_string = "SELECT * FROM sheet WHERE rowid = {};".format(row_id)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cs = conn.cursor()

    try:
        debug(db_string)
        c = cs.execute(db_string)
        return 200, c.fetchall()
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()


def get_rows_by_rowids(db_path: str = "form_id", subuser_id: str = "", row_ids:list=[0]):
    if not os.path.isfile(db_path):
        return 404, "数据库不存在"

    rows_string = ",".join(row_ids)
    db_string = "SELECT rowid,* FROM sheet WHERE rowid in ({}) AND update_by = ?".format(rows_string)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cs = conn.cursor()

    try:
        debug(db_string)
        c = cs.execute(db_string,[subuser_id,])
        return 200, c.fetchall()
    except Exception as e:
        return 500, str(e)
    finally:
        cs.close()
        conn.commit()
        conn.close()

