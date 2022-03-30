# 负责处理用户上传的 xlsx 表格文件
# /sheet

import os
from io import BytesIO
import zipfile

from fastapi import (
    Depends,
    APIRouter,
    File,
    Form,
    Path,
    Request,
    Query,
    HTTPException
)
from fastapi.responses import StreamingResponse
from openpyxl import load_workbook

from tools import (
    get_db_path,
    get_sheet_path,
    init_sheet_path_and_id,
    add_sheet_to_user_status,
    parse_sheet_columns_from_xlsx_file,
    get_sheet_columns_from_cache,
    get_matched_data,
    get_sheet_data_template,
    fill_to_xlsx,
    delete_sheet_path_and_files,
    delete_sheet_from_user_status,
    get_user_path,
    get_sheets_from_user_status,

)
from database_sql import (
    create_table,
    insert_row,
    get_subuser_rows,
    update_row,
    delete_row,
    get_row_by_rowid,
    get_rows_by_rowids,
    delete_rows,
)

from middlewares import (
    get_user_by_api_token,
    get_user_by_subuser_code,
)


router = APIRouter(prefix="/sheet")

# 用户级才能新建表单


@router.post("/create")
def create_sheet_by_xlsx(
    file: bytes = File(...),
    title: str = Form(...),
    user: list = Depends(get_user_by_api_token)
):
    if not file:
        raise HTTPException(status_code=400, detail="file missing")

    user_id, _ = user
    # 初始化一个表单 ID 和文件夹
    sheet_id, sheet_path = init_sheet_path_and_id()
    # 添加表单到用户目录
    add_sheet_to_user_status(
        user_id, sheet={"index": sheet_id, "title": title})
    # 保存 xlsx 文件
    with open(os.path.join(sheet_path, f"{sheet_id}.xlsx"), "wb")as b:
        b.write(file)
    code, result = parse_sheet_columns_from_xlsx_file(file, sheet_id)
    if code != 200:
        os.removedirs(sheet_path)
        raise HTTPException(status_code=code, detail=result)
    columns = result
    # 创建数据库
    code, result = create_table(
        db_path=os.path.join(sheet_path, f"{sheet_id}.db"),
        db_columns=get_sheet_columns_from_cache(sheet_id)
    )
    if code != 200:
        os.removedirs(sheet_path)
        raise HTTPException(status_code=code, detail=result)

    return {"code": 200, "sheet_id": sheet_id, "sheet_title": title, "columns": columns}



@router.post("/{sheet_id}/delete")
def delete_sheet(
    sheet_id: str = Path(...),
    user: list = Depends(get_user_by_api_token)
):
    if not sheet_id and len(sheet_id) == 32:
        raise HTTPException(status_code=400, detail="sheet_id missing")
    user_id, _ = user
    code,result = get_sheets_from_user_status(user_id)
    if code !=200:
        raise HTTPException(status_code=code,detail=result)
    if sheet_id not in result:
        raise HTTPException(status_code=401,detail="只能删除已拥有的表单")
    else:
        delete_sheet_path_and_files(sheet_id)
        delete_sheet_from_user_status(user_id, sheet_id)
        return {"code": 200}


@router.get("/{sheet_id}/columns")
async def get_sheet_columns(
    subuser: list = Depends(get_user_by_subuser_code)
):
    sheet_id, _, _ = subuser
    return get_sheet_data_template(sheet_id)


@router.post("/{sheet_id}/row/insert")
async def insert_row_to_db(
    request: Request,
    subuser: list = Depends(get_user_by_subuser_code)
):
    sheet_id, subuser_id, _ = subuser
    # 剔除与模板不匹配的数据
    data: dict = await request.json()
    template = get_sheet_data_template(sheet_id)
    row = get_matched_data(data=data, template=template)
    # 插入数据
    code, result = insert_row(
        db_path=get_db_path(sheet_id),
        subuser_id=subuser_id,
        row=row
    )
    if code != 200:
        raise HTTPException(status_code=code, detail=result)
    return result


@router.post("/{sheet_id}/row/{row_id}/update")
async def update_row_to_db(
    request: Request,
    subuser: list = Depends(get_user_by_subuser_code),
    row_id: int = Path(...)
):
    sheet_id, subuser_id, _ = subuser
    # 剔除与模板不匹配的数据
    data: dict = await request.json()
    template = get_sheet_data_template(sheet_id)
    row = get_matched_data(data=data, template=template)
    # 插入数据
    code, result = update_row(
        db_path=get_db_path(sheet_id),
        subuser_id=subuser_id,
        row=row,
        row_id=row_id,
    )
    if code != 200:
        raise HTTPException(status_code=code, detail=result)
    return result


@router.post("/{sheet_id}/row/{row_id}/delete")
async def delete_row_from_db(
    subuser: list = Depends(get_user_by_subuser_code),
    row_id: int = Path(...)
):
    sheet_id, subuser_id, _ = subuser
    code, result = delete_row(
        db_path=get_db_path(sheet_id),
        subuser_id=subuser_id,
        row_id=row_id,
    )
    if code != 200:
        raise HTTPException(status_code=code, detail=result)
    return result


@router.post("/{sheet_id}/rows/delete")
async def delete_rows_from_db(
    request: Request,
    subuser: list = Depends(get_user_by_subuser_code),
):
    sheet_id, subuser_id, _ = subuser

    data: list = await request.json()
    
    # 校验字段
    for rowid in data:
        print(rowid,type(rowid))
        if not isinstance(rowid,int):
            raise HTTPException(status_code=400, detail="每一个 rowid 都必须是 int 类型")
    
    # 传入数据库前，先转为 str
    data = map(lambda x:str(x),data)
    code, result = delete_rows(
        db_path=get_db_path(sheet_id),
        subuser_id=subuser_id,
        row_ids=data,
    )
    if code != 200:
        raise HTTPException(status_code=code, detail=result)
    return result

    


@router.get("/{sheet_id}/rows")
async def get_rows_from_db(
    subuser: list = Depends(get_user_by_subuser_code),
    limit: int = Query(default=10000),
    offset: int = Query(default=0),
):
    sheet_id, subuser_id, _ = subuser

    code, result = get_subuser_rows(
        db_path=get_db_path(sheet_id),
        subuser_id=subuser_id,
        offset=offset,
        limit=limit
    )
    if code != 200:
        raise HTTPException(status_code=code, detail=result)
    return result


@router.get("/{sheet_id}/rows/{row_id}/xlsx")
def get_form_row_to_xlsx(
    row_id: int = Path(...),
    user: list = Depends(get_user_by_subuser_code)
):
    sheet_id, user_id, _ = user
    code, result = get_row_by_rowid(
        db_path=get_db_path(sheet_id),
        row_id=row_id
    )
    if result:
        code, result = fill_to_xlsx(sheet_id, dict(result[0]))
        print(code, result)
        if code == 200:
            return StreamingResponse(result,
                                     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     )
    else:
        return {"code": 404, "errmsg": "没有找到记录"}



@router.post("/{sheet_id}/rows/xlsx")
async def get_form_rows_to_xlsx(
    request: Request,
    user: list = Depends(get_user_by_subuser_code)
):
    sheet_id, user_id, _ = user
    data: list = await request.json()
    # 校验字段
    for rowid in data:
        print(rowid,type(rowid))
        if not isinstance(rowid,int):
            raise HTTPException(status_code=400, detail="每一个 rowid 都必须是 int 类型")
    
    # 传入数据库前，先转为 str
    row_ids = map(lambda x:str(x),data)


    code, result = get_rows_by_rowids(
        db_path=get_db_path(sheet_id),
        subuser_id=user_id,
        row_ids=row_ids,
    )
    if result:

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for row in result:
                row = dict(row)
                print(row)
                file_name = str(row.get("rowid"))+".xlsx"
                code, bytes = fill_to_xlsx(sheet_id, row)
                print(code,file_name)
                file_value = bytes.getvalue()
                zip_file.writestr(file_name,file_value)
        zip_buffer.seek(0)
        return StreamingResponse(zip_buffer,
                                    media_type="application/zip",)
    else:
        return {"code": 404, "errmsg": "没有找到记录"}
