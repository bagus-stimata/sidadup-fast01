from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse, FileResponse
import geopandas as gpd
import os
import gzip
import tempfile
import traceback

from fastapi.params import Header
from shapely.ops import transform

router = APIRouter(prefix="/api/desgreen", tags=["farea"])

def check_auth(authorization: str | None):
    if not authorization or authorization.strip() != "Basic 123Welcome123":
        return False
    return True

@router.post("/tools/convert-shapefile-to-geojsongzip")
async def convert_shapefile_to_geojson_gzip(
    file_shp: UploadFile = File(...),
    file_shx: UploadFile = File(...),
    file_dbf: UploadFile = File(...),
    file_prj: UploadFile = File(...),
    authorization: str | None = Header(None)
):
    if not check_auth(authorization):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        required_files = {'shp': file_shp, 'shx': file_shx, 'dbf': file_dbf, 'prj': file_prj}

        with tempfile.TemporaryDirectory() as tmpdir:
            original_filename = file_shp.filename
            base_name = os.path.splitext(os.path.basename(original_filename))[0]

            input_paths = {}

            for ext, upload_file in required_files.items():
                path = os.path.join(tmpdir, f"{base_name}.{ext}")
                with open(path, "wb") as buffer:
                    buffer.write(await upload_file.read())
                input_paths[ext] = path

            shp_path = input_paths['shp']
            print(f"📥 Membaca: {shp_path}")

            gdf = gpd.read_file(shp_path, engine='fiona', ignore_geometry_errors=True)

            gdf = gdf[gdf.geometry.notnull()]

            if gdf.empty:
                return JSONResponse(status_code=400, content={"error": "Tidak ada geometri valid setelah pemrosesan"})

            if gdf.crs is None:
                return JSONResponse(status_code=400, content={"error": "CRS tidak terdeteksi. File .prj kemungkinan rusak"})

            if gdf.crs.to_epsg() != 4326:
                print("🔄 Mengubah CRS ke EPSG:4326")
                gdf = gdf.to_crs(epsg=4326)

            print("🔧 Memperbaiki geometri dengan buffer(0)")
            gdf["geometry"] = gdf["geometry"].buffer(0)

            gdf['geometry'] = gdf['geometry'].apply(lambda geom: round_geometry_coords(geom, precision=7))

            geojson_str = gdf.to_json()
            output_gz_path = os.path.join(tmpdir, f"{base_name}.geojson.gz")

            with gzip.open(output_gz_path, "wt", encoding="utf-8") as f:
                f.write(geojson_str)

            return FileResponse(
                output_gz_path,
                media_type="application/gzip",
                filename=f"{base_name}.geojson.gz"
            )

    except Exception as e:
        print("ERROR:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Gagal memproses shapefile: {str(e)}"})

def round_geometry_coords(geom, precision=7):
    def _round_coords(x, y, z=None):
        if z is None:
            return (round(x, precision), round(y, precision))
        else:
            return (round(x, precision), round(y, precision), round(z, precision))
    return transform(_round_coords, geom)

@router.post("/tools/convert-kml-to-geojsongzip")
async def convert_kml_to_geojson_gzip():
    return {"status": "success", "message": "Welcome to FastAPI KML Converter!"}