# 程序入口 

# 用户页面，需要创建、导出、删除表单
# 更新表单如何实现呢？或许可以为表单引入导入功能，建立一个新的，再申请导入数据。比对数据标头后，导入有效的部分。
# columns {}
# 表单页面，需要新建、修改、删除行数据。
# 需要新建、修改、删除数据维护员。
# 数据权限？增加 update_at,update_by 字段


# 所有的内部调用都返回 (status_code,result) 元组
# 所有的 api 视图调用都返回 {"code":status_code,"data":result}

import time,os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from router_api_sheet import router as sheet_router
from router_api_user import router as users_router

app = FastAPI()

# 挂载路由
app.include_router(sheet_router, prefix="/api")
app.include_router(users_router, prefix="/api")

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://127.0.0.1:5500","http://localhost:3000/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
