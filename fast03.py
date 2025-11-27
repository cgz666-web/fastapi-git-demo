from fastapi import FastAPI

import uvicorn

app = FastAPI()

from book import book1

app.include_router(book1, prefix="/book")

from fastapi import Request

import fastapi_cdn_host
fastapi_cdn_host.patch_docs(app)

@app.get("/")
async def root(request: Request):
    name = request.query_params.get("name", "")  # 第二个参数是默认值，没获取到就返回空字符串
    param_111 = request.query_params.get("111", "")  # 规范命名：不建议用数字开头的变量名

    # 打印结果（友好显示，避免None）
    print(f"name参数值：{name}")
    print(f"111参数值：{param_111}")

    return {"message":"hello world"}

@app.post("/")
async def post_test(request: Request):
    result = await request.json()
    print(result.get("222"))
    return {"message":"hello world"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)