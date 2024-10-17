from fastapi import FastAPI
from router import router


app = FastAPI(title="SN generator")
app.include_router(router)
