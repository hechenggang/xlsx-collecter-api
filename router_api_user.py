# 用户相关 API
# /user/*


import os
import json
from io import BytesIO

from fastapi import (
    Depends, 
    APIRouter, 
    File, 
    Form, 
    Path, 
    Request, 
    Query, 
    Header,
    HTTPException
)
from openpyxl import load_workbook


from tools import (
    get_user_path,
    get_sheets_from_user_status,
    get_hashed_text,
    add_subusers_to_sheet,
    check_sheet_subuser,
)
from middlewares import get_user_by_api_token

router = APIRouter(prefix="/user")

# /api/user/sheets
@router.get("/sheets")
async def get_user_sheets(
    user: list = Depends(get_user_by_api_token)
):
    user_id,_ = user
    code,result = get_sheets_from_user_status(user_id)
    if code != 200:
        raise HTTPException(status_code=code,detail=result)
    else:
        return result



@router.post("/{sheet_id}/subusers/import")
def import_subusers_form_xlsx(
    file: bytes = File(...),
    sheet_id: str = Path(...),
    user: list = Depends(get_user_by_api_token)
):
    if not file:
        raise HTTPException(status_code=400,detail="file missing")
    user_id, _ = user
    users = {}
    workbook = load_workbook(BytesIO(file))
    worksheet = workbook.worksheets[0]
    for index, row in enumerate(worksheet.rows):
        if index == 0:
            continue
        users[get_hashed_text(row[0].value)] = {
            "a": row[0].value, 
            "p": get_hashed_text(row[1].value)
            }
    code,result = add_subusers_to_sheet(user_id, sheet_id, users)
    if code != 200:
        raise HTTPException(status_code=code,detail=result)
    else:
        return {"msg":result}


@router.post("/{sheet_id}/subuser/login")
async def sheet_subuser_login(
    request:Request,
    sheet_id: str = Path(...),
):
    data: dict = await request.json()
    print(data)
    account = data.get("account")
    password = data.get("password")
    subuser_id = get_hashed_text(account)
    password_hash = get_hashed_text(password)
    if check_sheet_subuser(subuser_id, password_hash, sheet_id):
        return {"x-api-subuser-code": "{}-{}".format(subuser_id, password_hash),"name":account}
    else:
        raise HTTPException(status_code=401,detail="校验失败")
