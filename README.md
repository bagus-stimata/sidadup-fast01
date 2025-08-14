Author: Mas-Win  
Lisensi: DES GREEN NUSANTARA License

## ⚠️ Persyaratan Python

> ✅ **Project ini WAJIB dijalankan pada Python versi 3.10 atau 3.11**
>
> ❌ **Python 3.12 atau 3.13 belum direkomendasikan**  
> 
> karena beberapa dependency utama (misal: passlib, geopandas, dll) belum 100% kompatibel dan bisa menyebabkan error saat runtime atau development.

> Cara cek versi Python yang aktif:
> bash
>> python --version

> 1.Buat virtual environment bau (WAJIB)
   > pada bash / command line
   > pastikan berada di dalam folder project ini
   > jika menggunakan Python 3.8 atau lebih baru:
>>   python3 -m venv venv
>   atau
>>   python -m venv .venv

> 2. Aktifkan virtual environment yang sudah dibuat:
> pada Windows:
>   .venv\Scripts\activate
> pada Linux/MacOS:
>>   source .venv/bin/activate
   
> 3. INSTALL DEPENDENCIES
pip install -r requirements.txt

> 4. Tambahkan enterpreter  IDE PyCharm ke dalam project ini
>     - PyCharm -> Settings -> Project: <nama_project> -> Python Interpreter -> Add Local Interpreter-> Pilih .venv yang sudah dibuat

> 5. Buat Setting .env Baru berisi konfigurasi untuk aplikasi FastAPI
>> DATABASE_URL = "mysql+pymysql://<user>:<password>> @localhost:3306/<nama_database>"

>>ALGORITHM=<HS256 atau HS512 yang paling umum tapi sudah cukup>
>>SECRET_KEY=<Untuk Hash dan Enkripsi>
>>ACCESS_TOKEN_EXPIRE_MINUTES=<Waktu dalam menit untuk token akses Standart JWT>


> Contoh:
>>DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/mydatabase"
>>SECRET_KEY=mysecretkey123
>>ALGORITHM=HS256 
>>ACCESS_TOKEN_EXPIRE_MINUTES = 360


> 6. Jalankan aplikasi FastAPI
>    - Buka terminal di PyCharm atau command line
>    - Pastikan virtual environment sudah aktif
>    - Jalankan perintah berikut:
    uvicorn app.main:app --reload
>atau
    uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

>7. Jalan test menggunakan pytest
>    - Pastikan virtual environment sudah aktif
>    - Jalankan perintah berikut:
    pytest -v --disable-warnings
> atau
    pytest

> Struktur Folder Project FastAPI: ByFeature
>>desgreen-fast01/
>>├── alembic/                > Folder migration database (alembic)
>>├── alembic.ini             > Config file untuk alembic
>>├── app/                    > Source code utama aplikasi FastAPI
>>├── requirements.txt        > Daftar dependency utama
>>├── requirements-lock.txt   > (Opsional, biasanya dari pip freeze atau poetry)
>>├── pytest.ini              > Config pytest (testing)
>>├── test/                   > Folder untuk unit/integration test
>>├── test_main.http          > (Opsional, biasanya contoh request untuk testing API, kadang dari JetBrains)
>>└── README.md               > Dokumentasi project

