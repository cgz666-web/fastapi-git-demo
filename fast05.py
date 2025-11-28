from fastapi import FastAPI

import uvicorn

app = FastAPI()

from book import book1

app.include_router(book1, prefix="/book")

from fastapi import Request

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="1"), name="static_files")

from fastapi.templating import Jinja2Templates
template = Jinja2Templates(directory="templates")

from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM

register_tortoise(
app,
confiq=TORTOISE_ORM,
generate_schemas=True,
add_exception_handlers=True,
)

from models import User

import fastapi_cdn_host
fastapi_cdn_host.patch_docs(app)

@app.get("/")
async def root(request: Request):
    user_re = await User.get_or_none()
    user_all = await User.all()
    return {"message":"hello world"}

@app.post("/")
async def post_test(request: Request):
    result = await request.json(
    name =  result['name']
    await User.create(name=result['name'])
    return {"message":"hello world"}

@app.put(f"/{id}")
async def put_test(id:int,request: Request):
    result = await request.json(
    name=result['name']
    await User.filter(id=id).update(name=result['name'])
    return {"message":"hello world"}

@app.delete("/{id}")
async def delete_test(id:int,request: Request):
    await User.filter(id=id).delete()
    return {"message":"hello world"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)