---
title: Kotoba Kita Backend
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

<div align="center">
# 言葉・きた
# Kotoba Kita — Backend

**REST API untuk aplikasi web flashcard adaptif kosakata bahasa Jepang,
ditenagai algoritma FSRS dan dibangun dengan Django.**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Hugging Face](https://img.shields.io/badge/Deploy-Hugging%20Face-FFD21E?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/mademara/Kotoba-kita-Backend)

[📖 API Docs (Swagger)](https://mademara-kotoba-kita-backend.hf.space/api/docs/) · [🌐 Frontend Repo](https://github.com/mademara/Kotoba-kita-Frontend)

## </div>

## Tentang Proyek

Backend **Kotoba Kita** adalah REST API yang menjadi otak dari sistem pembelajaran adaptif. Di sinilah algoritma **FSRS (Free Spaced Repetition Scheduler)** bekerja — menghitung kapan setiap kartu harus muncul kembali berdasarkan riwayat jawaban pengguna, seberapa cepat mereka menjawab, dan apakah jawabannya benar.

Semua kalkulasi FSRS diproses di backend sehingga tidak bisa dimanipulasi dari sisi pengguna. Setiap jawaban yang dikirim frontend diproses, dinilai (Again / Hard / Good / Easy), lalu disimpan ke database — dan jadwal kemunculan kartu berikutnya dihitung secara otomatis.

> Capstone Project — Dicoding Bootcamp Batch 11 | ID Tim: DB11-G002
> Tema: _Accessible & Adaptive Learning_

---

## Arsitektur

```
GitHub (push ke main)
        │
        ▼ GitHub Actions (CI/CD)
        │
        ▼ Hugging Face Spaces (Docker)
        │   Django + Gunicorn, port 7860
        │
        ▼ Neon.tech
            PostgreSQL (cloud)
```

---

## Endpoint API

Dokumentasi interaktif tersedia di `/api/docs/` (Swagger UI). Ringkasan endpoint:

| Method           | Endpoint                   | Keterangan                                |
| ---------------- | -------------------------- | ----------------------------------------- |
| `POST`           | `/api/auth/register/`      | Daftar akun baru                          |
| `POST`           | `/api/auth/login/`         | Login, mendapatkan access & refresh token |
| `POST`           | `/api/auth/token/refresh/` | Perbarui access token                     |
| `POST`           | `/api/auth/logout/`        | Logout, blacklist refresh token           |
| `GET`            | `/api/words/`              | Daftar semua kosakata N5                  |
| `GET`            | `/api/words/{id}/`         | Detail satu kata                          |
| `GET`            | `/api/decks/`              | Daftar deck milik user                    |
| `POST`           | `/api/decks/`              | Buat deck baru                            |
| `GET/PUT/DELETE` | `/api/decks/{id}/`         | Detail, edit, hapus deck                  |
| `GET`            | `/api/study/{deck_id}/`    | Generate soal untuk sesi belajar          |
| `POST`           | `/api/study/submit/`       | Submit jawaban & proses FSRS              |
| `GET`            | `/api/study/stats/`        | Statistik global pengguna                 |

---

## Cara Kerja Algoritma FSRS

Setiap kali pengguna menjawab soal, backend menghitung **rating** berdasarkan dua faktor:

| Kondisi           | Rating                                   |
| ----------------- | ---------------------------------------- |
| Jawaban salah     | `Again` — kartu muncul lagi sangat cepat |
| Benar, ≤ 5 detik  | `Easy` — interval panjang                |
| Benar, 6–10 detik | `Good` — interval sedang                 |
| Benar, > 10 detik | `Hard` — interval pendek                 |

Rating ini dimasukkan ke library `py-fsrs` yang menghitung ulang nilai `stability`, `difficulty`, `state`, dan `due` (tanggal jatuh tempo kartu) untuk disimpan ke database.

---

## Prasyarat

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (wajib untuk menjalankan lokal)
- [Git](https://git-scm.com/)
- Python + pipenv (opsional, untuk autocomplete editor)

---

## Menjalankan Secara Lokal

### 1. Clone & Setup Environment

```bash
git clone https://github.com/mademara/Kotoba-kita-Backend.git
cd Kotoba-kita-Backend

# Buat file .env dari template
cp .env.example .env
```

Edit `.env` — nilai default di `.env.example` sudah cocok untuk development lokal, tidak perlu diubah kecuali kamu ingin mengganti `SECRET_KEY` dan `JWT_SECRET_KEY`:

```env
DEBUG=true
SECRET_KEY=ganti-dengan-string-acak-panjang
DATABASE_URL=postgres://user_dev:pass_dev@db:5432/proyek_db

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

JWT_SECRET_KEY=ganti-dengan-string-acak-lain
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

### 2. Jalankan dengan Docker

Pastikan Docker Desktop sudah aktif, lalu:

```bash
docker compose up
```

Backend siap saat log menampilkan:

```
backend-1  | Watching for file changes with StatReloader
db-1       | database system is ready to accept connections
```

- API berjalan di: **http://localhost:8000**
- Swagger UI di: **http://localhost:8000/api/docs/**
  Perubahan kode Python langsung ter-reload tanpa perlu restart.

```bash
# Stop server (data DB tetap aman)
Ctrl+C
docker compose down
```

### 3. Setup Database & Superuser

```bash
# Jalankan migrasi (wajib setelah clone pertama kali)
docker exec -it kotoba-backend python manage.py migrate

# Buat superuser untuk akses Django Admin
docker exec -it kotoba-backend python manage.py createsuperuser
```

Django Admin tersedia di **http://localhost:8000/admin/** — digunakan untuk mengelola data kosakata N5 dan pengguna.

---

## Seeding Data Kosakata N5

Data kosakata tidak ter-include di repository karena ukurannya. Cara memasukkan data ke database:

### Opsi A — Dari Lokal ke Database Production

Cara ini berguna untuk mengisi Neon.tech dari komputer lokal:

```bash
# 1. Ganti DATABASE_URL di .env dengan connection string Neon.tech-mu
# 2. Jalankan migrate ke database production
docker exec -it kotoba-backend python manage.py migrate

# 3. Import data melalui Django Admin atau management command
docker exec -it kotoba-backend python manage.py shell
```

### Opsi B — Melalui Django Admin

Setelah superuser dibuat, login ke `/admin/` dan tambahkan data kata melalui interface admin. Cocok untuk jumlah data kecil.

---

## Deploy ke Hugging Face Spaces

Proyek ini sudah dilengkapi CI/CD via GitHub Actions. Setiap push ke `main` otomatis men-deploy ke Hugging Face Spaces.

### Setup Pertama Kali

**1. Buat Hugging Face Space baru**

- Masuk ke [huggingface.co](https://huggingface.co) → New Space
- SDK: **Docker**, visibilitas: Public
- Catat nama space-mu (format: `username/nama-space`)
  **2. Tambahkan secrets di Hugging Face Space**

Di halaman Space → Settings → Repository Secrets, tambahkan:

```
DEBUG          = false
SECRET_KEY     = string-acak-panjang-untuk-production
DATABASE_URL   = postgresql://...  ← connection string dari Neon.tech
JWT_SECRET_KEY = string-acak-lain
CORS_ALLOWED_ORIGINS = https://url-frontend-vercel-kamu.vercel.app
CSRF_TRUSTED_ORIGINS = https://url-frontend-vercel-kamu.vercel.app
ACCESS_TOKEN_LIFETIME_MINUTES = 60
REFRESH_TOKEN_LIFETIME_DAYS   = 7
```

**3. Tambahkan HF_TOKEN di GitHub**

- Buat token di Hugging Face → Settings → Access Tokens (role: Write)
- Di GitHub repo → Settings → Secrets → Actions, tambahkan:
  ```
  HF_TOKEN = hf_xxxxxxxxxxxxxxxxxxxx
  ```

**4. Sesuaikan `deploy.yml`**

Edit `.github/workflows/deploy.yml`, ganti remote URL dengan nama Space-mu:

```yaml
git remote add hf https://USERNAME_HF:${HF_TOKEN}@huggingface.co/spaces/USERNAME_HF/NAMA_SPACE
```

**5. Push ke main**

```bash
git push origin main
```

GitHub Actions akan otomatis mendorong kode ke Hugging Face dan Space akan build ulang.

---

## Setup Database Neon.tech

1. Daftar di [neon.tech](https://neon.tech) (gratis)
2. Buat project baru → salin **Connection String** (format `postgresql://...`)
3. Gunakan connection string tersebut sebagai nilai `DATABASE_URL` di secrets Hugging Face Space
4. Jalankan migrasi dari lokal dengan mengganti `DATABASE_URL` di `.env` lokal ke connection string Neon.tech, lalu:
   ```bash
   docker exec -it kotoba-backend python manage.py migrate
   ```

---

## Menambah Dependency Python

```bash
# 1. Install via pipenv
pipenv install nama-package

# 2. Update requirements.txt untuk Docker
pipenv run pip freeze > requirements.txt

# 3. Rebuild Docker
docker compose up --build
```

---

## Struktur Proyek

```
Kotoba-kita-Backend/
├── apps/
│   ├── users/          — model User, autentikasi JWT (register, login, logout)
│   ├── words/          — model Word, endpoint read-only kosakata N5
│   ├── decks/          — model Deck, CRUD deck + relasi many-to-many ke words
│   └── flashcards/     — inti FSRS: generate soal, submit jawaban, statistik
│       ├── models.py   — model Flashcard (stability, difficulty, state, due, dll)
│       ├── services.py — logika FSRS (build_card, apply_review, get_rating)
│       └── views.py    — GenerateQuestionsView, SubmitAnswerView, HomeStatsView
├── core/               — settings, urls utama, wsgi
├── .github/workflows/  — CI/CD deploy ke Hugging Face
├── Dockerfile          — production (Gunicorn, port 7860)
├── Dockerfile.dev      — development (runserver + hot reload)
├── docker-compose.yml  — orkestrasi backend + PostgreSQL lokal
└── requirements.txt    — semua dependency Python
```

---

## Perintah Docker Berguna

```bash
# Masuk ke shell container backend
docker exec -it kotoba-backend bash

# Buat file migrasi baru setelah mengubah models.py
docker exec -it kotoba-backend python manage.py makemigrations

# Jalankan migrasi
docker exec -it kotoba-backend python manage.py migrate

# Buka psql untuk query langsung ke database
docker exec -it kotoba-db psql -U user_dev -d proyek_db
```

Perintah berguna di dalam psql:

| Perintah                    | Fungsi               |
| --------------------------- | -------------------- |
| `\dt`                       | Lihat semua tabel    |
| `\d nama_tabel`             | Lihat struktur tabel |
| `SELECT * FROM nama_tabel;` | Lihat isi tabel      |
| `\q`                        | Keluar               |

---

## Git Workflow

```bash
# Selalu pull sebelum mulai
git pull origin main

# Buat branch baru untuk setiap fitur
git checkout -b nama-fitur

# Setelah selesai
git add .
git commit -m "deskripsi perubahan"
git push origin nama-fitur

# Buat Pull Request — jangan push langsung ke main
```

---

## Troubleshooting

**`Port 5432 already in use`**

```bash
sudo service postgresql stop
docker compose up
```

**`Module not found` setelah pull**

```bash
pipenv install
docker compose up --build
```

**Perubahan model tidak ter-reflect di database**

```bash
docker exec -it kotoba-backend python manage.py makemigrations
docker exec -it kotoba-backend python manage.py migrate
```

**Container tidak bisa start**

```bash
docker compose down
docker compose up --build
```

---

## Atribusi Data Kosakata

Data kosakata Jepang pada proyek ini menggunakan **JMdict/EDICT**, yang dikembangkan oleh Electronic Dictionary Research and Development Group (EDRDG) dan dilisensikan di bawah [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

- JMdict project page: https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project
- JMdict-simplified (sumber JSON yang digunakan): https://github.com/scriptin/jmdict-simplified

---

<div align="center">
  Dibuat dengan ☕ dan kesabaran ekstra oleh <strong>Made Gusmara Sugiarta</strong><br>
  Dicoding Bootcamp Batch 11 · DB11-G002
</div>
