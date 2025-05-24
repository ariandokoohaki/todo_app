# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import database, engine, Base
from app.api.routes import api_router # <--- This is the crucial import

# Create tables on startup (for SQLite)
# Base.metadata.create_all(bind=engine) # Consider if this is better handled by Alembic or a specific script/conftest for tests

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# This includes all routes defined in api_router at the root of your application
# So, if api_router has a "/token" route, it will be accessible as "/token"
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    await database.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()