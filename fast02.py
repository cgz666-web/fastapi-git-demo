from fastapi import FastAPI

import uvicorn

app = FastAPI()

from book import book1

app.include_router(book1, prefix="/book")

import fastapi_cdn_host
fastapi_cdn_host.patch_docs(app)

@app.get("/")
async def root():
    return {"message":"hello world"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)