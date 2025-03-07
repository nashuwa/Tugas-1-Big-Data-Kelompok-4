# Tugas-1-Big-Data-Kelompok-4
Repository ini berisi skrip otomatisasi untuk mengambil, memproses, dan menyimpan data keuangan dari berbagai sumber, yaitu Yahoo Finance (yfinance), Bursa Efek Indonesia (IDX), dan IQPlus, ke dalam MongoDB. Proyek ini dibuat sebagai bagian dari implementasi konsep Big Data, khususnya dalam pengelolaan dan analisis data dalam jumlah besar.

## Struktur Folder
Berikut adalah penjelasan mengenai struktur folder dalam repository ini:

###  Script IDX
Berisi skrip untuk mengambil data dari Bursa Efek Indonesia (IDX).
- scrape_idx.py : Mengambil data saham dari IDX menggunakan web scraping.
- insert_to_mongodb.py : Memproses dan menyimpan data yang telah diambil ke dalam MongoDB.
webdriver/ : Folder berisi msedgedriver.exe, yang digunakan untuk web scraping.

### Script IQNews
Berisi skrip untuk mengambil berita pasar modal dari IQPlus.
- scrape_IQNews_market.py : Mengambil berita pasar dari IQPlus.
- scrape_IQNews_stock.py : Mengambil berita terkait saham dari IQPlus.
- insert_IQNews_market_to_mongodb.py : Menyimpan data berita pasar ke MongoDB.
- insert_IQNews_stock_to_mongodb.py : Menyimpan data berita saham ke MongoDB.

### Script yfinance
Berisi skrip untuk mengambil data saham dari Yahoo Finance.
- fetch_tickers.py : Mengambil daftar ticker saham yang tersedia di Yahoo Finance.
- insert_to_mongodb.py : Memasukkan data saham ke dalam MongoDB.
- tickers.xlsx : File yang berisi daftar ticker saham yang telah diambil.

## Fitur Utama
- Pengambilan Data: Menggunakan API dan web scraping untuk mengumpulkan data keuangan dari berbagai sumber.
- Pemrosesan Data: Melakukan pembersihan, transformasi, dan normalisasi data agar siap digunakan.
- Penyimpanan Data: Menyimpan data ke dalam MongoDB untuk analisis lebih lanjut.
- Analisis Data: Menyediakan akses cepat ke data untuk keperluan analisis keuangan.

## Teknologi yang Digunakan
- Python untuk scripting dan otomasi.
- MongoDB sebagai basis data NoSQL.
- API Yahoo Finance (yfinance) untuk mengambil data pasar saham global.
- Data dari Bursa Efek Indonesia (IDX) untuk informasi saham di Indonesia.
- IQPlus untuk berita dan sentimen pasar.
