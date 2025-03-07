# pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import zipfile
import xml.etree.ElementTree as ET
import json

# Buat folder untuk menyimpan file ZIP & JSON
download_folder = os.path.abspath("downloads")
os.makedirs(download_folder, exist_ok=True)

# Konfigurasi Chrome WebDriver
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)

# Buka halaman IDX
driver.get("https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan")
time.sleep(5)

# Pilih Tahun 2024 & Triwulan Audit
try:
    driver.find_element(By.XPATH, "//input[@value='2024']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//input[@value='audit']").click()
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Terapkan')]").click()
    time.sleep(5)
except Exception as e:
    print(f"ERROR: Gagal menerapkan filter. ({e})")

# Looping download
while True:
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'instance.zip')]"))
        )
    except:
        print("Tidak ada file untuk diunduh.")
        break

    download_buttons = driver.find_elements(By.XPATH, "//a[contains(@href, 'instance.zip')]")
    print(f"Menemukan {len(download_buttons)} file ZIP untuk diunduh.")

    if not download_buttons:
        break

    for index, button in enumerate(download_buttons):
        print(f"Mengunduh file {index+1}...")
        
        try:
            close_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Tutup')]")
            close_button.click()
            time.sleep(2)
        except:
            pass

        driver.execute_script("document.querySelector('.site-header').style.display='none';")

        existing_files = set(os.listdir(download_folder))
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        driver.execute_script("arguments[0].scrollIntoView();", button)
        time.sleep(1)

        try:
            actions = ActionChains(driver)
            actions.move_to_element(button).click().perform()
        except:
            driver.execute_script("arguments[0].click();", button)

        time.sleep(5)

        while True:
            new_files = set(os.listdir(download_folder)) - existing_files
            if any(f.endswith(".crdownload") for f in os.listdir(download_folder)):
                time.sleep(3)
            else:
                break

        new_files = set(os.listdir(download_folder)) - existing_files
        if not new_files:
            print("Download gagal!")
            continue

        downloaded_zip = list(new_files)[0]
        new_zip_path = os.path.join(download_folder, f"instance_{timestamp}.zip")
        os.rename(os.path.join(download_folder, downloaded_zip), new_zip_path)
        print(f"ZIP file tersimpan: {new_zip_path}")

        try:
            with zipfile.ZipFile(new_zip_path, "r") as zip_file:
                if "instance.xbrl" not in zip_file.namelist():
                    print("ERROR: Tidak ada 'instance.xbrl' dalam ZIP!")
                    continue

                with zip_file.open("instance.xbrl") as xbrl_file:
                    tree = ET.parse(xbrl_file)
                    root = tree.getroot()

                    data = {elem.tag.split("}")[-1]: elem.text.strip() if elem.text else None for elem in root.iter()}
                    emiten_name = data.get("EntityName", f"Emiten_{timestamp}")

                    json_filename = f"instance_{timestamp}.json"
                    json_path = os.path.join(download_folder, json_filename)
                    with open(json_path, "w", encoding="utf-8") as json_file:
                        json.dump({"emiten": emiten_name, "laporan_keuangan": data}, json_file, indent=4, ensure_ascii=False)

                    print(f"Data disimpan: {json_path}")

        except zipfile.BadZipFile:
            print("ERROR: File ZIP tidak valid!")

        # Hapus file ZIP setelah diproses
        os.remove(new_zip_path)
        print(f"ZIP file dihapus: {new_zip_path}")

    try:
        next_button = driver.find_element(By.XPATH, "//button[contains(@class, '--next')]")
        if next_button.is_enabled():
            next_button.click()
            time.sleep(7)
        else:
            break
    except:
        break

driver.quit()
print("Scraping selesai.")
