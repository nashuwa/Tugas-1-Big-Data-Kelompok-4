import pandas as pd
import yfinance as yf
import time
import logging
import json

# Setup logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

# Baca file Excel
file_path = "tickers.xlsx"
df = pd.read_excel(file_path)

# Ambil daftar ticker dan tambahkan ".JK" jika belum ada
tickers = df["Ticker"].astype(str).tolist()
tickers = [ticker + ".JK" if not ticker.endswith(".JK") else ticker for ticker in tickers]

print(f"Total ticker yang akan diproses: {len(tickers)}")

# Fungsi untuk mengambil data dari yfinance
def fetch_ticker_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist_data = stock.history(start="2024-01-01", end="2024-12-31")
        
        if hist_data.empty:
            print(f"{ticker} mungkin delisted atau tidak memiliki data untuk tahun 2024.")
            return None

        return {
            "Ticker": ticker,
            "info": info,
            "hist_data": hist_data.to_dict("records")
        }
    except Exception as e:
        print(f"Gagal mengambil data untuk {ticker}: {e}")
        logging.error(f"Gagal mengambil data untuk {ticker}: {e}")
        return None

# List untuk menyimpan semua data
all_data = []

# Loop untuk mengambil data
for ticker in tickers:
    retries = 3
    success = False
    
    while retries > 0 and not success:
        try:
            data = fetch_ticker_data(ticker)
            if data:
                all_data.append(data)
                print(f"Data untuk {ticker} berhasil diambil.")
                success = True
            else:
                print(f"Data untuk {ticker} tidak tersedia.")
                break
        except Exception as e:
            print(f"Error pada {ticker}: {e}. Mencoba lagi dalam 5 detik...")
            logging.error(f"Error pada {ticker}: {e}. Mencoba lagi dalam 5 detik...")
            retries -= 1
            time.sleep(5)
        
        time.sleep(2)

# Simpan data ke JSON
json_file_path = "tickers_data.json"
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)

print(f"Semua data telah disimpan ke {json_file_path}")
