"""
Enovia PLM'de parça arama otomasyonu (Microsoft Edge).
Kullanım:
  1) Tüm Edge pencerelerini kapatın
  2) Bu scripti çalıştırın - Edge'i otomatik açar, PLM'e gider ve arama yapar
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
import time
import subprocess


PLM_URL = "https://plm.vnet.valeo.com:7001/enovia/common/emxNavigator.jsp"
PART_NUMBER = "C597104"


def open_edge_and_connect():
    """Edge'i debug modunda başlatıp Selenium ile bağlanır."""
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    subprocess.Popen([
        edge_path,
        "--remote-debugging-port=9222",
        "--user-data-dir=C:\\EdgeDebugProfile",
        PLM_URL
    ])

    print("Edge açılıyor, sayfa yüklenmesi bekleniyor...")
    time.sleep(10)

    options = webdriver.EdgeOptions()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Edge(options=options)
    return driver


def search_part(driver, part_number):
    """PLM arama kutusuna *parça_numarası yazıp aratır."""
    search_query = f"*{part_number}*"

    possible_selectors = [
        "input#AEFGlobalFullTextSearchInput",
        "input[name='AEFGlobalFullTextSearchInput']",
        "input.search-input",
        "input[type='text'][id*='Search']",
        "input[type='text'][id*='search']",
    ]

    search_input = None
    for selector in possible_selectors:
        try:
            search_input = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            print(f"Arama kutusu bulundu: {selector}")
            break
        except Exception:
            continue

    if not search_input:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        print(f"Bulunan text input sayısı: {len(inputs)}")
        for i, inp in enumerate(inputs):
            print(f"  Input {i}: id='{inp.get_attribute('id')}', "
                  f"name='{inp.get_attribute('name')}', "
                  f"class='{inp.get_attribute('class')}'")
        if inputs:
            search_input = inputs[0]
        else:
            frames = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Frame sayısı: {len(frames)}")
            for idx, frame in enumerate(frames):
                try:
                    driver.switch_to.frame(frame)
                    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    if inputs:
                        print(f"Frame {idx} içinde {len(inputs)} input bulundu")
                        search_input = inputs[0]
                        break
                    driver.switch_to.default_content()
                except Exception:
                    driver.switch_to.default_content()

    if not search_input:
        raise Exception("Arama kutusu bulunamadı! Sayfanın yüklendiğinden emin olun.")

    search_input.clear()
    search_input.send_keys(search_query)
    time.sleep(0.5)
    search_input.send_keys(Keys.RETURN)
    print(f"'{search_query}' araması yapıldı.")


def click_latest_drawing(driver, part_number):
    """Arama sonuçlarından DRW_ ile başlayan en yüksek revizyonlu linke tıklar."""
    drw_prefix = f"DRW_{part_number}"

    def matches_drawing(text):
        return text.startswith("DRW_") and part_number in text

    # Sonuç tablosundaki tüm linkleri bul
    links = driver.find_elements(By.CSS_SELECTOR, "a")
    drawing_links = []
    for link in links:
        text = link.text.strip()
        if matches_drawing(text):
            drawing_links.append(link)

    if not drawing_links:
        # Frame'lerin içine bak
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in frames:
            try:
                driver.switch_to.frame(frame)
                links = driver.find_elements(By.CSS_SELECTOR, "a")
                for link in links:
                    text = link.text.strip()
                    if matches_drawing(text):
                        drawing_links.append(link)
                if drawing_links:
                    break
                driver.switch_to.default_content()
            except Exception:
                driver.switch_to.default_content()

    if not drawing_links:
        raise Exception(f"'{drw_prefix}' ile başlayan link bulunamadı!")

    # En yüksek revizyonu bul - revision sütunu Name'in yanındaki hücrede
    best_link = drawing_links[0]
    best_rev = ""
    for link in drawing_links:
        try:
            row = link.find_element(By.XPATH, "./ancestor::tr")
            cells = row.find_elements(By.TAG_NAME, "td")
            for cell in cells:
                cell_text = cell.text.strip()
                if len(cell_text) == 1 and cell_text.isalpha():
                    if cell_text > best_rev:
                        best_rev = cell_text
                        best_link = link
                    break
        except Exception:
            pass

    print(f"Tıklanıyor: {best_link.text} (Revizyon: {best_rev or 'N/A'})")
    best_link.click()


def main():
    print("Edge başlatılıyor...")
    driver = open_edge_and_connect()
    print(f"Bağlanıldı. Sayfa: {driver.title}")

    print("PLM sayfasının tam yüklenmesi bekleniyor...")
    time.sleep(5)

    search_part(driver, PART_NUMBER)

    print("Sonuçların yüklenmesi bekleniyor...")
    time.sleep(5)

    click_latest_drawing(driver, PART_NUMBER)

    print("Drawing sayfası yükleniyor...")
    time.sleep(5)
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
