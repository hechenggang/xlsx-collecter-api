# 程序入口

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from router.xlsx import router as xlsx_router
from router.users import router as users_router

app = FastAPI()

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
# 挂载路由
app.include_router(xlsx_router, prefix="/api")
app.include_router(users_router, prefix="/api")

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*","http://127.0.0.1:5500"],
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
