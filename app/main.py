from fastapi import FastAPI
from core.settings import settings

app = FastAPI()

print(settings)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
