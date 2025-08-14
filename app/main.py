from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers.auth import auth
from app.routers.desgreen import farea
from app.routers.tools import shape_to_geojson


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Semua origin boleh
    allow_credentials=True,     # Cookie / Authorization header boleh
    allow_methods=["*"],        # Semua method (GET, POST, DELETE, dll)
    allow_headers=["*"],        # Semua header custom diizinkan
)
app.include_router(auth.router)
app.include_router(farea.router)
app.include_router(shape_to_geojson.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

