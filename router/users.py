

import os
import json

from fastapi import Depends, APIRouter, File, Form, Path, Request, Query, Header


from tools import init_form_path, cache_path, get_form_path, get_user_path
from middlewares import get_user_by_api_token

router = APIRouter(prefix="/user")


@router.get("/forms")
async def get_forms(
    request: Request,
    user_info: list = Depends(get_user_by_api_token)
):
    print(user_info)
    user_path = get_user_path(user_info[0])
    forms_path = os.path.join(user_path, "forms.json")
    if not os.path.isfile(forms_path):
        return {"code": 404, "errmsg": "用户表单不存在"}
    with open(forms_path,"rt",encoding="utf-8")as t:
        return {"code": 200, "forms": json.loads(t.read())}


@router.post("/forms")
async def get_forms(
    request: Request,
    user_info: list = Depends(get_user_by_api_token)
):
    print(user_info)
    user_path = get_user_path(user_info[0])
    forms_path = os.path.join(user_path, "forms.json")
    if not os.path.isfile(forms_path):
        return {"code": 404, "errmsg": "用户表单不存在"}
    with open(forms_path,"rt",encoding="utf-8")as t:
        return {"code": 200, "forms": json.loads(t.read())}
