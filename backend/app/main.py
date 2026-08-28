from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, inventory, orders, dashboard, agent, ws
from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # In production, use Alembic migrations instead of create_all.
    # create_all is fine for local dev / demo bootstrapping.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.APP_NAME, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production to your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(dashboard.router)
app.include_router(agent.router)
app.include_router(ws.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}
