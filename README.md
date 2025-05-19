# KIK Gas Usage Monitoring App

Aplikasi berbasis **Streamlit** untuk memantau dan menganalisis data pemakaian gas bulanan dari 12 tenant. Aplikasi ini menampilkan grafik pemakaian, nilai rekonsiliasi, serta ringkasan data penting secara interaktif dan mudah digunakan.

## Fitur Utama
- Upload file Excel berisi data pemakaian gas dan kurs.
- Visualisasi grafik pemakaian per tenant untuk tiap bulan.
- Informasi tenant dengan pemakaian tertinggi dan terendah.
- Perhitungan nilai rekonsiliasi dalam Rupiah berdasarkan kurs.
- Tampilan responsif dengan layout *wide* untuk pengalaman pengguna optimal.
- Proteksi login sederhana menggunakan `streamlit-authenticator` untuk menjaga keamanan data sensitif.

## Instalasi

1. Clone repository ini  
   ```bash
   git clone https://github.com/username/repo-name.git
   cd repo-name
