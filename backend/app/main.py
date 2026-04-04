from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, products, orders, analytics
from app.database import engine, Base
import logging
import time

# ── Structured logging ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce DevOps Analytics API",
    description="Analytics platform for e-commerce data with DevOps integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / response logging middleware ─────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    logger.info(
        "%s %s → %s  (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(users.router,     prefix="/api/users",     tags=["Users"])
app.include_router(products.router,  prefix="/api/products",  tags=["Products"])
app.include_router(orders.router,    prefix="/api/orders",    tags=["Orders"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
def root():
    return {"message": "E-Commerce Analytics API", "status": "running", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
