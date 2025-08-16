from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.routers.auth import auth
from app.routers.desgreen import farea
from app.routers.tools import shape_to_geojson
from app.routers.sidadup import (
    kecamatan,
    jenis_usaha as jenis_usaha_router,
    badan_usaha as badan_usaha_router,
    sub_sektor as subsektor_router,
    sektor_perizinan as sektor_router,
    data_perizinan as data_perizinan_router,
)
from app.routers.sidadup import provinsi as provinsi_router
from app.routers.sidadup import daerah as daerah_router

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
app.include_router(kecamatan.router)
app.include_router(provinsi_router.router)
app.include_router(daerah_router.router)
app.include_router(sektor_router.router)
app.include_router(subsektor_router.router)
app.include_router(badan_usaha_router.router)
app.include_router(jenis_usaha_router.router)
app.include_router(data_perizinan_router.router)
@app.get("/")
async def root():
    return {"message": "Hello World"}

