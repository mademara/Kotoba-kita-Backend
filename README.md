---
title: Kotoba Kita Backend
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Kotoba Kita — Backend

Django REST Framework + PostgreSQL, dijalankan via Docker.

---

## Tentang Proyek

**Kotoba Kita** adalah aplikasi web flashcard adaptif untuk belajar kosakata bahasa Jepang, ditujukan bagi pemula berbahasa Indonesia. Aplikasi ini menggunakan algoritma **FSRS (Free Spaced Repetition Scheduler)** untuk menentukan kapan setiap kartu harus muncul kembali berdasarkan riwayat belajar masing-masing pengguna — kartu yang sering salah muncul lebih cepat, kartu yang sudah dikuasai muncul lebih jarang.

Proyek ini hadir sebagai solusi lokal atas rendahnya penyerapan tenaga kerja Indonesia ke Jepang akibat kegagalan sertifikasi bahasa — dengan antarmuka penuh Bahasa Indonesia agar tidak ada hambatan bahasa pengantar asing.

> **Capstone Project — Dicoding Bootcamp Batch 11** | Tim ID: DB11-G002 | Tema: _Accessible & Adaptive Learning_

### Tim

| Nama
| ----------------------
| Irgi Afandi Amienullah
| Adlian Nur Bhakti
| Made Gusmara Sugiarta

### Tech Stack

| Layer             | Teknologi                                  |
| ----------------- | ------------------------------------------ |
| Backend           | Python 3.13, Django, Django REST Framework |
| Autentikasi       | SimpleJWT                                  |
| Spaced Repetition | py-fsrs (algoritma FSRS)                   |
| Database          | PostgreSQL — hosted di Neon.tech           |
| Containerization  | Docker + Docker Compose                    |
| Frontend          | React + Vite, Axios                        |
| CI/CD             | GitHub Actions                             |
| Hosting Backend   | Hugging Face Spaces (Docker)               |
| Hosting Frontend  | Vercel                                     |

### Fitur MVP

- Autentikasi (register, login, logout)
- Sesi belajar: format multiple choice, Kanji/Kosakata → tebak arti Bahasa Indonesia, maks 20 kata baru/hari + kata yang due hari ini
- Algoritma FSRS: semua kalkulasi di backend, tidak bisa dimanipulasi user
- Dashboard: kartu due hari ini, streak belajar, tombol mulai review
- Ringkasan setelah sesi: akurasi, kata paling sering salah
- Browse kata N5: lihat kanji, furigana, arti, dan contoh kalimat
- Custom Deck: kurasi kata fokus dari database N5 yang sudah ada
- Profil & Statistik: retention rate, streak harian, total kata dipelajari

---

## Prasyarat

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Git](https://git-scm.com/)
- Python + pipenv

---

## Setup Awal

```bash
git clone https://github.com/mademara/Kotoba-kita-Backend
cd Kotoba-kita-Backend

# Install dependencies ke virtual env lokal (untuk editor/autocomplete)
pip install pipenv
pipenv install

# Buat file .env
cp .env.example .env
# Minta kredensial .env ke Mara — jangan buat sendiri
```

---

## Menjalankan Server

Pastikan Docker Desktop sudah aktif.

```bash
docker compose up
```

Backend siap saat log menampilkan:

```
backend-1  | Watching for file changes with StatReloader
db-1       | database system is ready to accept connections
```

Perubahan kode Python langsung ter-reload otomatis tanpa restart Docker.

**Menghentikan server:**

```bash
# Stop saja (bisa dilanjut lagi nanti)
Ctrl+C

# Stop + hapus container (data DB tetap aman)
docker compose down
```

---

## Perintah Django

Jalankan dari terminal biasa (tidak perlu masuk ke container):

```bash
# Migrate database (wajib setelah pull jika ada file migrasi baru)
docker exec -it kotoba-backend python manage.py migrate

# Buat file migrasi setelah mengubah models.py
docker exec -it kotoba-backend python manage.py makemigrations

# Buat superuser untuk Django admin
docker exec -it kotoba-backend python manage.py createsuperuser
```

Untuk sesi interaktif di dalam container:

```bash
docker exec -it kotoba-backend bash
# Ketik `exit` untuk keluar
```

---

## Database (PostgreSQL)

```bash
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

## Menambah Dependency Python

```bash
# 1. Install via pipenv (untuk editor)
pipenv install nama-package

# 2. Update requirements.txt (untuk Docker)
pipenv run pip freeze > requirements.txt

# 3. Rebuild Docker
docker compose up --build

# Opsional: bersihkan image lama
docker image prune
```

---

## Struktur Proyek

```
Kotoba-kita-Backend/
  apps/
    users/          ← autentikasi dan user
    words/          ← data kosakata Jepang
    flashcards/     ← FSRS spaced repetition
  core/             ← settings, urls, wsgi
  docker-compose.yml
  Dockerfile.dev
  requirements.txt
  Pipfile
```

---

## Git Workflow

```bash
# Sebelum mulai — selalu pull dulu
git pull origin main

# Buat branch baru untuk setiap fitur
git checkout -b nama-fitur

# Setelah selesai
git add .
git commit -m "deskripsi perubahan"
git push origin nama-fitur
```

> Jangan push langsung ke `main`. Selalu buat pull request.

---

## Troubleshooting

**Port 5432 already in use**

```bash
sudo service postgresql stop
docker compose up
```

**Module not found setelah pull**

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

- JMdict project page: [https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project](https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project)
- JMdict-simplified (sumber JSON yang digunakan): [https://github.com/scriptin/jmdict-simplified](https://github.com/scriptin/jmdict-simplified)
