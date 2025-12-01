# 🚀 iCafe Platform API (FastAPI + DDD)

Project ini merupakan implementasi arsitektur **Domain-Driven Design (DDD)** untuk platform **Layanan Reservasi, Billing, dan Pembayaran Warnet**.  
Dengan pendekatan aggregate dan value object, project ini memodelkan proses inti operasional warnet seperti reservasi, sesi pemakaian, perhitungan tagihan, dan pembayaran.

---


# iCafe Platform API - Panduan Autentikasi

Panduan ini menjelaskan cara menggunakan sistem autentikasi JWT yang telah ditambahkan ke iCafe API.

## Prasyarat

Install dependensi yang diperlukan:

```bash
pip install -r app/requirements.txt
```

## Menjalankan Server

```bash
cd app
uvicorn main:app --reload
```

API akan tersedia di `http://localhost:8000`

## Endpoint Autentikasi

### 1. Daftar Pengguna Baru

```bash
POST /auth/register
Content-Type: application/json

{
    "username": "testuser",
    "email": "testuser@example.com", 
    "password": "securepassword123",
    "role": "CUSTOMER"
}
```

Response:
```json
{
    "id": "user-uuid",
    "username": "testuser", 
    "email": "testuser@example.com",
    "role": "CUSTOMER",
    "status": "ACTIVE"
}
```

### 2. Login

```bash
POST /auth/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "securepassword123"
}
```

Response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

### 3. Dapatkan Informasi Pengguna Saat Ini

```bash
GET /users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:
```json
{
    "id": "user-uuid",
    "username": "testuser",
    "email": "testuser@example.com", 
    "role": "CUSTOMER",
    "status": "ACTIVE"
}
```

## Endpoint Terlindungi

Semua endpoint API yang sudah ada sekarang memerlukan autentikasi. Sertakan token JWT di header Authorization:

```bash
Authorization: Bearer <token-jwt-anda>
```

### Contoh:

#### Buat Reservasi
```bash
POST /reservations
Authorization: Bearer <token-jwt-anda>
Content-Type: application/json

{
    "customer_id": "customer123",
    "workstation_id": "ws001",
    "start": "2025-12-01T10:00:00",
    "end": "2025-12-01T12:00:00",
    "package_name": "Gaming Package",
    "package_duration_minutes": 120,
    "package_price_amount": 50000
}
```

#### Lihat Daftar Reservasi
```bash
GET /reservations
Authorization: Bearer <token-jwt-anda>
```

#### Mulai Sesi
```bash
POST /sessions
Authorization: Bearer <token-jwt-anda>
Content-Type: application/json

{
    "customer_id": "customer123",
    "workstation_id": "ws001",
    "reservation_id": "reservation-uuid"
}
```

## Peran Pengguna

- `CUSTOMER`: Pengguna biasa dengan akses untuk membuat reservasi, sesi, dll.
- `ADMIN`: Pengguna admin dengan hak istimewa (dapat diperluas untuk endpoint khusus admin)

## Konfigurasi Keamanan

- Token JWT berakhir setelah 30 menit secara default
- Password di-hash menggunakan bcrypt
- Secret key harus diubah di production (saat ini diatur di `auth_service.py`)

## Dokumentasi API

Kunjungi `http://localhost:8000/docs` untuk dokumentasi API interaktif dengan Swagger UI.

## Testing Autentikasi

1. Daftarkan pengguna baru dengan endpoint `/auth/register`
2. Login dengan endpoint `/auth/login` untuk mendapatkan token JWT  
3. Gunakan token di header Authorization untuk semua request selanjutnya
4. Coba akses endpoint terlindungi seperti `/reservations`, `/sessions`, `/invoices`

Semua endpoint akan mengembalikan `401 Unauthorized` jika tidak ada token valid yang diberikan.
