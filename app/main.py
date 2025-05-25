# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import database
from app.api.routes import api_router  # <--- This is the crucial import


app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    await database.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()
