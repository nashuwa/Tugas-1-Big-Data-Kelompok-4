from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import zipfile
import xml.etree.ElementTree as ET
import pymongo
import json

# Koneksi ke MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["bigdata_idx"]
collection = db["laporan_keuangan"]

# Buat folder untuk menyimpan file ZIP & JSON
download_folder = os.path.abspath("downloads")
os.makedirs(download_folder, exist_ok=True)

# Konfigurasi Chrome WebDriver untuk otomatis download ZIP
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

# Buka WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Buka halaman IDX
print("Membuka halaman IDX...")
driver.get("https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan")
time.sleep(5)

# Pilih Tahun 2024
try:
    tahun_2024 = driver.find_element(By.XPATH, "//input[@value='2024']")
    driver.execute_script("arguments[0].click();", tahun_2024)
    time.sleep(2)
    print("Tahun 2024 dipilih.")
except Exception as e:
    print(f"ERROR: Tidak dapat memilih tahun 2024. ({e})")

# Pilih Triwulan 1
try:
    triwulan_1 = driver.find_element(By.XPATH, "//input[@value='tw1']")
    driver.execute_script("arguments[0].click();", triwulan_1)
    time.sleep(2)
    print("Triwulan 1 dipilih.")
except Exception as e:
    print(f"ERROR: Tidak dapat memilih Triwulan 1. ({e})")

# Klik tombol Terapkan
try:
    tombol_terapkan = driver.find_element(By.XPATH, "//button[contains(text(), 'Terapkan')]")
    driver.execute_script("arguments[0].click();", tombol_terapkan)
    time.sleep(5)
    print("Tombol Terapkan diklik.")
except Exception as e:
    print(f"ERROR: Tidak dapat menemukan tombol Terapkan. ({e})")

# Looping untuk berpindah halaman sampai halaman terakhir
while True:
    # Tunggu sampai halaman selesai loading
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'instance.zip')]"))
        )
        print("Halaman sudah siap, mulai download...")
    except:
        print("WARNING: Halaman belum siap, cek lagi nanti.")

    # Ambil semua tombol download instance.zip
    download_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'instance.zip')]")
    print(f"Jumlah tombol download ditemukan: {len(download_buttons)}")

    if len(download_buttons) == 0:
        print("GAGAL: Tidak ada tombol download ditemukan!")
    else:
        for index, button in enumerate(download_buttons):
            print(f"Mengunduh file ke-{index+1}...")

            # Simpan nama file sebelum download
            existing_files = set(os.listdir(download_folder))

            # Klik tombol download
            driver.execute_script("arguments[0].click();", button)
            time.sleep(5)  # Beri jeda waktu awal

            # Tunggu sampai file selesai diunduh
            while True:
                new_files = set(os.listdir(download_folder)) - existing_files
                crdownload_files = [f for f in os.listdir(download_folder) if f.endswith(".crdownload")]

                if crdownload_files:
                    print(f"Menunggu file selesai diunduh: {crdownload_files}")
                    time.sleep(3)  # Cek setiap 3 detik
                else:
                    break  # Semua file sudah selesai diunduh

            # Cek file baru yang diunduh
            new_files = set(os.listdir(download_folder)) - existing_files
            if not new_files:
                print("ERROR: Download gagal atau tidak ditemukan!")
                continue

            zip_path = os.path.join(download_folder, list(new_files)[0])
            print(f"ZIP file tersimpan: {zip_path}")

            # Periksa apakah file benar-benar ZIP
            with open(zip_path, "rb") as f:
                file_header = f.read(4)
                if file_header != b"PK\x03\x04":
                    print(f"ERROR: {zip_path} bukan file ZIP yang valid!")
                    continue

            try:
                with zipfile.ZipFile(zip_path, "r") as zip_file:
                    print("ZIP file berhasil dibuka.")

                    # Pastikan ada file instance.xbrl
                    if "instance.xbrl" not in zip_file.namelist():
                        print("ERROR: Tidak menemukan 'instance.xbrl' dalam ZIP!")
                        continue

                    # Parsing instance.xbrl
                    with zip_file.open("instance.xbrl") as xbrl_file:
                        tree = ET.parse(xbrl_file)
                        root = tree.getroot()

                        # Fungsi konversi XML ke dictionary
                        def xml_to_dict(element):
                            tag_name = element.tag.split("}")[-1]  # Hilangkan namespace
                            return {tag_name: element.text.strip() if element.text else None}

                        # Parsing semua elemen XML menjadi satu dictionary
                        data = {}
                        for elem in root.iter():
                            data.update(xml_to_dict(elem))  # Masukkan ke dalam satu objek

                        # Ambil nama emiten dari XML (misalnya ada tag "EntityName")
                        emiten_name = data.get("EntityName", f"Emiten_{index+1}")

                        # Struktur data untuk MongoDB
                        emiten_data = {
                            "emiten": emiten_name,
                            "laporan_keuangan": data
                        }

                        # Simpan ke file JSON
                        json_path = zip_path.replace(".zip", ".json")
                        with open(json_path, "w", encoding="utf-8") as json_file:
                            json.dump(emiten_data, json_file, indent=4, ensure_ascii=False)

                        print(f"Data berhasil dikonversi ke JSON: {json_path}")

                        # Simpan ke MongoDB dalam satu dokumen per emiten
                        collection.insert_one(emiten_data)
                        print(f"Data emiten {emiten_name} berhasil disimpan ke MongoDB!")

            except zipfile.BadZipFile:
                print("ERROR: File ZIP tidak valid!")
                continue

    # Cek apakah ada file yang masih diunduh sebelum lanjut ke halaman berikutnya
    while True:
        crdownload_files = [f for f in os.listdir(download_folder) if f.endswith(".crdownload")]
        if crdownload_files:
            print(f"Masih ada file yang diunduh: {crdownload_files}")
            time.sleep(3)
        else:
            print("Semua file sudah diunduh, lanjut ke halaman berikutnya.")
            break

    # Hapus ZIP setelah selesai diproses
    for file_name in os.listdir(download_folder):
        if file_name.endswith(".zip"):
            zip_file_path = os.path.join(download_folder, file_name)
            try:
                os.remove(zip_file_path)
                print(f"ZIP file dihapus: {zip_file_path}")
            except Exception as e:
                print(f"WARNING: Gagal menghapus ZIP {zip_file_path}. ({e})")

    # Coba cari tombol Next untuk pindah halaman
    try:
        tombol_next = driver.find_element(By.XPATH, "//button[contains(@class, '--next')]")

        # Periksa apakah tombol dalam kondisi aktif (bukan disabled)
        if not tombol_next.is_enabled() or "disabled" in tombol_next.get_attribute("class"):
            print("Tombol Next tidak aktif atau tidak ditemukan, proses selesai.")
            break

        print("Tombol Next ditemukan, berpindah halaman...")
        driver.execute_script("arguments[0].click();", tombol_next)

        # Tunggu halaman baru selesai loading sebelum mencari tombol download lagi
        time.sleep(7)

    except Exception as e:
        print(f"Tidak ada halaman berikutnya, proses selesai. ({e})")
        break

# Cek jumlah dokumen di MongoDB
print(f"Total dokumen di MongoDB setelah proses: {collection.count_documents({})}")
print("Semua data selesai diproses!")

# Tutup browser setelah selesai
driver.quit()