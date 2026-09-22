# Harvest2Day
Foobar is a Python library for dealing with word pluralization.

## Installation

pip install these:

```bash
fastapi
uvicorn
pandas
numpy
scikit-learn
python-multipart
```

## Usage
Isi Folder (Yang Penting):
1. regres.ipynb -> model dalam bentuk python lewat google colab: https://colab.research.google.com/drive/1w4M-2xZRk26pKO6zcCH9K_lVD3TyHfQ4 <- Akses kodenya lewat sini aja (jauh lebih mudah)

2. Folder "kaggle dataset" -> idrice.csv <- upload file ini di webapp atau di google colab (ini adalah dataset yang dipakai)

3. AOLWebAPP -> berisi folder API, dan file-file websitenya.

(PENTING!)
Untuk menjalankan webapp Harvest2Day:
Buka folder AOLWebAPP -> folder API -> buka file "requirements.txt" di notepad, pip install semuanya yang ada di sana.
Setelah udah selesai pip install semua library/dependencies di file "requirements.txt" (saran: pakai versi python 3.12.x) buka command prompt atau terminal pilihan kalian, pastikan kalian berada di file directory folder "AI AOL\AOLWebAPP\API"

jalankan command "uvicorn aolapp:app --reload"
outputnya seharusnya mirip seperti ini:

INFO:     Will watch for changes in these directories: ['(DRIVE):\\AI AOL\\AOLWebAPP\\API']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [29580] using StatReload
INFO:     Started server process [19520]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

(PENTING!: Terminal API tidak boleh ditutup (di minimize boleh))

Untuk menjalankan websitenya:
Buka folder AOLWebAPP -> buka index.html -> selesai.


Extra: Kegunaan Dependencies/Library/Plugins/Package di API (Application Programming Interface) :

1. FastAPI
Framework backend Python modern yang digunakan untuk membuat API.

Fungsinya:
Membuat endpoint seperti /upload-dataset, /train, /predict-province, /predict-farmer
Menangani request/response secara cepat

2. Uvicorn
ASGI(Asynchronous Server Gateway Interface) server yang digunakan untuk menjalankan FastAPI.

Fungsinya:
Menjalankan aplikasi FastAPI
Hot-reload (--reload) saat ada perubahan kode
Menerima HTTP request dari frontend

3. Pandas
Library data processing.

Fungsinya di API kamu:
Membaca CSV yang di-upload user
Rename kolom dataset
Filter data berdasarkan provinsi
Hitung rata-rata produktivitas
Membersihkan & memvalidasi data

4. NumPy
Library operasi matematika & array.

Fungsinya:
Membentuk matriks X dan y untuk model regresi
Mengubah tahun menjadi array 2D: np.array([[year]])
Menghitung nilai tambahan untuk plotting

5. Scikit-Learn
Library pemodelan machine learning.

Fungsinya:
Membuat model regresi linear:
LinearRegression()

Menghitung metrik model:
R²
RMSE
Prediksi produksi berdasarkan tahun

6. Matplotlib
Library plotting grafik.

Fungsinya:
Membuat grafik regresi(scatter + line)
Mengubah grafik menjadi Base64 PNG untuk dikirim ke frontend(website)

Backend menghasilkan:
plot_png_base64
yang frontend(website) tampilkan sebagai <img>.

7. python-multipart
Library untuk menangani upload file multipart/form-data.

Fungsinya:
Memungkinkan endpoint FastAPI menerima file CSV:
UploadFile = File(...)
Tanpa package/library ini, upload CSV tidak bisa diproses.
