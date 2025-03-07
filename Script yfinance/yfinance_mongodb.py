import pandas as pd
import yfinance as yf
from pymongo import MongoClient
import time
import logging
from datetime import datetime

# Setup logging untuk menyimpan error ke file
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

# Baca file Excel
file_path = "tickers.xlsx"
df = pd.read_excel(file_path)

# Ambil daftar ticker dari kolom 'Ticker' dan pastikan semua nilai berupa string
tickers = df["Ticker"].astype(str).tolist()

# Tambahkan '.JK' untuk format Yahoo Finance (jika belum ada)
tickers = [ticker + ".JK" if isinstance(ticker, str) and not ticker.endswith(".JK") else ticker for ticker in tickers]

print(f"Total ticker yang akan diproses: {len(tickers)}")

# Fungsi untuk mengambil data dari yfinance
def fetch_ticker_data(ticker):
    try:
        # Ambil objek Ticker dari yfinance
        stock = yf.Ticker(ticker)
        
        # Ambil info perusahaan
        info = stock.info
        
        # Ambil data historis untuk tahun 2024
        hist_data = stock.history(start="2024-01-01", end="2024-12-31")
        
        # Jika data historis kosong, kemungkinan ticker delisted
        if hist_data.empty:
            print(f"{ticker} mungkin delisted atau tidak memiliki data untuk tahun 2024.")
            return None
        
        # Kembalikan data dalam bentuk dictionary
        return {
            "info": info,
            "hist_data": hist_data.to_dict("records")
        }
    except Exception as e:
        print(f"Gagal mengambil data untuk {ticker}: {e}")
        logging.error(f"Gagal mengambil data untuk {ticker}: {e}")
        return None

# Koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Ganti dengan connection string MongoDB Anda
db = client["data_emiten"]  # Nama database
collection = db["tickers_yfinance"]  # Nama koleksi

# Loop melalui setiap ticker
for ticker in tickers:
    retries = 3  # Jumlah percobaan ulang jika gagal
    success = False
    
    while retries > 0 and not success:
        try:
            # Ambil data dari Yahoo Finance
            data = fetch_ticker_data(ticker)
            
            if data:
                # Tambahkan kolom ticker ke data
                data["Ticker"] = ticker
                
                # Simpan data ke MongoDB (1 ticker = 1 dokumen)
                collection.insert_one(data)
                
                print(f"Data untuk {ticker} berhasil diambil dan disimpan.")
                success = True
            else:
                print(f"Data untuk {ticker} tidak tersedia.")
                break
        except Exception as e:
            print(f"Gagal menyimpan data untuk {ticker}: {e}. Mencoba lagi dalam 5 detik...")
            logging.error(f"Gagal menyimpan data untuk {ticker}: {e}. Mencoba lagi dalam 5 detik...")
            retries -= 1
            time.sleep(5)  # Tunggu 5 detik sebelum mencoba lagi
        
        # Tambahkan delay 2 detik antara setiap permintaan
        time.sleep(2)

print("Proses selesai.")