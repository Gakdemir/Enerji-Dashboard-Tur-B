"""
Enovia PLM'de parça arama otomasyonu.
Kullanım: Tarayıcı açık ve PLM'e giriş yapılmış durumda olmalı.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def connect_to_existing_browser():
    """
    Zaten açık olan Chrome tarayıcıya bağlanır.
    Chrome'u şu şekilde başlatmanız gerekir:
      chrome.exe --remote-debugging-port=9222
    """
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=options)
    return driver


def search_part(driver, part_number):
    """PLM arama kutusuna parça numarası yazıp aratır."""
    search_query = f"*{part_number}"

    # Üstteki arama input alanını bul (ekrandaki toolbar'daki input)
    # Enovia'da bu genelde id="AEFGlobalFullTextSearchInput" veya benzer bir id taşır
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
            break
        except Exception:
            continue

    if not search_input:
        # Fallback: toolbar'daki tüm input'ları dene
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
        print(f"Bulunan text input sayısı: {len(inputs)}")
        for i, inp in enumerate(inputs):
            print(f"  Input {i}: id='{inp.get_attribute('id')}', "
                  f"name='{inp.get_attribute('name')}', "
                  f"class='{inp.get_attribute('class')}', "
                  f"value='{inp.get_attribute('value')}'")
        if inputs:
            search_input = inputs[0]
            print(f"İlk input kullanılıyor: {search_input.get_attribute('id')}")
        else:
            # Frame'lerin içine bak
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


def main():
    part_number = "C597104"

    print("Açık tarayıcıya bağlanılıyor...")
    driver = connect_to_existing_browser()
    print(f"Bağlanıldı. Sayfa: {driver.title}")

    search_part(driver, part_number)

    print("Sonuçların yüklenmesi bekleniyor...")
    time.sleep(5)
    print("Arama tamamlandı.")


if __name__ == "__main__":
    main()
