# app/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Route modules
from app.routes.extract_all import router as extract_all_router
from app.routes.extract_methods import router as extract_methods_router
from app.routes.extract_sections import router as extract_sections_router

app = FastAPI()

# Mount static assets (HTML/JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Homepage for browser use
@app.get("/")
async def homepage():
    return FileResponse("app/static/index.html")

# Register API routes
app.include_router(extract_all_router)
app.include_router(extract_methods_router)
app.include_router(extract_sections_router)
