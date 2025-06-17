# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ─── Route modules ────────────────────────────────────────────────────
from app.routes.extract_all import router as extract_all_router
from app.routes.extract_sections import router as extract_sections_router
from app.routes.extract_methods import router as extract_methods_router
from app.routes.extract_tables import router as extract_tables_router  # NEW

# ─── FastAPI instance ────────────────────────────────────────────────
app = FastAPI(
    title="PDF Section & Table Extractor",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS (allow browser UI to call API) ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static assets (HTML UI lives in app/static) ─────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
async def homepage():
    """Serve the HTML UI."""
    return FileResponse("app/static/index.html")

# ─── Register API routes ─────────────────────────────────────────────
app.include_router(extract_all_router)
app.include_router(extract_sections_router)
app.include_router(extract_methods_router)
app.include_router(extract_tables_router)       # NEW
