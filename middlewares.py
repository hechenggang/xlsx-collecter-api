

from fastapi import Header,HTTPException,Path
from tools_of_account import code_check
from tools import check_sheet_subuser

# account.imhcg.cn
async def get_user_by_api_token(x_api_code: str = Header(...)):
    status,result = code_check(x_api_code)
    if status == 200:
        return result
    else:
        raise HTTPException(status_code=400,detail="认证失败")



# 本地表单用户的认证
def subuser_code_check(code,sheet_id):
    split_string = "-"
    if len(code) != 129: 
        return 400,"@code 长度不正确"
    if split_string not in code:
        return 400,"@code 格式不正确"
    subuser_id, password_hash = code.split(split_string)
    if check_sheet_subuser(subuser_id,password_hash,sheet_id):
        return 200,[sheet_id,subuser_id,password_hash]
    else: 
        return 401,"认证失败"


async def get_user_by_subuser_code(sheet_id: str = Path(...),x_api_subuser_code: str = Header(...)):
    status,result = subuser_code_check(x_api_subuser_code,sheet_id)
    if status == 200:
        return result
    else:
        raise HTTPException(status_code=status,detail=result)