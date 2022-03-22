
import os,sys
from time import time as timestamp
import uuid
import hashlib
import openpyxl

import json
import time
from io import StringIO, BytesIO
from tempfile import NamedTemporaryFile
from typing import Optional
from fastapi import Depends, APIRouter, File, Form, Path, Request, Query
from fastapi.responses import FileResponse, StreamingResponse
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


def create_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
        return 200,""
    else:
        return 400,"创建失败，因为目标文件夹已存在"


def get_hashed_text(text: str = None, mix_text: str = None):
    text = str(text)
    if not bool(text):
        text = "{}{}".format(str(timestamp()), uuid.uuid1().hex)
    if bool(mix_text):
        text = "{}{}".format(str(text), str(mix_text))
    return hashlib.sha256(text.encode()).hexdigest()


def get_hashed_file(file: bytes = None):
    return hashlib.sha256(file).hexdigest()

def get_uuid_text():
    return uuid.uuid1().hex


# 准备相关目录
work_path = os.path.dirname(__file__)
print("boot dir is: ",work_path)
cache_path = os.path.join(work_path,"cache")
users_path = os.path.join(cache_path,"users")
froms_path = os.path.join(cache_path,"forms")
required_paths = [cache_path,users_path,froms_path]
for path in required_paths:
    create_dir(path)


def get_user_path(user_id):
    user_path = os.path.join(users_path,user_id)
    if not os.path.isdir(user_path):
        os.makedirs(user_path)
    return user_path

def get_form_path(form_id):
    return os.path.join(froms_path,form_id)

def get_db_path(form_id):
    return os.path.join(get_form_path(form_id), f"{form_id}.db")
    
def init_form_path():
    form_id = get_uuid_text()
    form_path = get_form_path(form_id)
    code, _ = create_dir(form_path)
    if code != 200:
        init_form_path()
    return form_id,form_path
    


def get_marks_from_xlsx_sheet(worksheet: Worksheet):
    data = {}
    for row in worksheet.rows:
        for cell in row:
            data[cell.coordinate] = {"value": cell.value}

    marked_data = {}
    for cell in data:
        value = data[cell].get("value")
        if not value:
            continue
        # 当遇到形如 input:str->A2 的格子时，标记为需要采集的格子
        mark_a = "->"
        mark_b = "input:"
        if mark_a in value and mark_b in value:
            type, link_to = value[len(mark_b):].split(mark_a)
            marked_data[cell] = {
                "type": type,
                "link_to": link_to,
                "defalt_value": data[link_to].get("value")
            }

    return marked_data


def get_marked_data(form_id) -> dict:
    with open(os.path.join(get_form_path(form_id), f"{form_id}.json"), "rt", encoding="utf-8")as t:
        marked_data = json.loads(t.read())
        return marked_data


def get_db_columns(form_id):
    marked_data = get_marked_data(form_id)
    db_columns = [
        {
            "type": marked_data[i]["type"],
            "column_name":marked_data[i]["link_to"],
            "defalt_value":marked_data[i]["defalt_value"]
        } for i in marked_data
    ]
    return db_columns



def get_db_columns_name(form_id):
    return [i["column_name"] for i in get_db_columns(form_id)]

def get_map_of_link_to(form_id):
    r = {}
    columns = get_marked_data(form_id)
    for i in columns.keys():
        r[columns[i]["link_to"]] = i
    return r


def fill_to_xlsx(form_id, row: dict):
    print("output:", form_id, row)
    try:
        workbook = load_workbook(os.path.join(
            get_form_path(form_id), "{}.xlsx".format(form_id)))
        sheet = workbook.worksheets[0]
        link_to_map = get_map_of_link_to(form_id)
        for key in row.keys():
            value = row[key]
            raw_position = link_to_map.get(key)
            if not raw_position:
                continue
            sheet[raw_position] = value

        out = BytesIO()
        workbook.save(out)
        out.seek(0)
        return 200, out
    except Exception as e:
        return 500, str(e)


def append_form_to_user(user_id, form_id, form_title):
    user_path = get_user_path(user_id)
    forms_path = os.path.join(user_path, "forms.json")
    temp_forms = []
    if os.path.isfile(forms_path):
        with open(forms_path, "rt", encoding="utf-8")as t:
            temp_forms += json.loads(t.read())
    temp_forms.append(
        {"form_id": form_id, "form_title": form_title, "create_at": time.time()})
    with open(forms_path, "wt", encoding="utf-8")as t:
        t.write(json.dumps(temp_forms))


def append_users_to_form(user_id, form_id, users):
    # 检查 表单所属
    user_path = get_user_path(user_id)
    forms_path = os.path.join(user_path, "forms.json")
    if not os.path.isfile(forms_path):
        return {"code": 400, "errmsg": "用户没有表单"}
    with open(forms_path, "rt", encoding="utf-8")as t:
        forms = json.loads(t.read())
        form_ids = []
        for form in forms:
            form_ids.append(form["form_id"])
        if not form_id in form_ids:
            return {"code": 400, "errmsg": "用户未拥有该表单"}

    # 写入信息
    form_path = get_form_path(form_id)
    form_users_path = os.path.join(form_path, "users.json")
    with open(form_users_path, "wt", encoding="utf-8")as t:
        t.write(json.dumps(users))


def check_form_user(user_id, password_hash, form_id):

    form_path = get_form_path(form_id)
    form_users_path = os.path.join(form_path, "users.json")
    if not os.path.isfile(form_users_path):
        return False
    with open(form_users_path, "rt", encoding="utf-8")as t:
        users: dict = json.loads(t.read())
        user: dict = users.get(user_id)
        if not user:
            return False
        if user.get("p") == password_hash:
            return True
        else:
            return False

def write_sheet(header:list=[],rows:list=[], sheet_name="导出数据",fp=""):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(header)
    for row in rows:
        ws.append(row)
    wb.save(fp)

def read_sheet(file_path, sheet_name=""):
    wb = openpyxl.load_workbook(file_path)
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.worksheets[0]
    return [row for row in ws.values]

