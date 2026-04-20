# flake8: noqa: E402
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from src.api.auth import router as auth_router
from src.api.users import router as users_router
from src.core.config import settings
from src.core.database import create_tables_if_not_exist

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API with JWT auth, Google OAuth2 and DynamoDB — deployable to AWS Lambda",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)


@app.on_event("startup")
def startup():
    create_tables_if_not_exist()


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "version": settings.app_version}


# AWS Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
