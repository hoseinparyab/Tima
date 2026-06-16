from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.reports import router as reports_router
from app.api.v1.time_entry import router as time_entry_router
from app.api.v1.workspace import router as workspace_router
from app.core.config import settings
from app.core.database import close_db, connect_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(workspace_router, prefix=API_PREFIX)
app.include_router(projects_router, prefix=API_PREFIX)
app.include_router(time_entry_router, prefix=API_PREFIX)
app.include_router(reports_router, prefix=API_PREFIX)


@app.get(
    "/health",
    summary="بررسی سلامت سرویس",
    description="وضعیت API را برمی‌گرداند. برای مانیتورینگ و اطمینان از بالا بودن سرور استفاده می‌شود.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
