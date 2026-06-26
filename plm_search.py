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
    """Arama sonuçları popup'ında DRW satırına tıklar."""
    main_window = driver.current_window_handle
    all_windows = driver.window_handles
    print(f"Toplam pencere sayısı: {len(all_windows)}")

    for w in all_windows:
        driver.switch_to.window(w)
        print(f"  Pencere: {driver.title} - URL: {driver.current_url}")

    if len(all_windows) > 1:
        driver.switch_to.window(all_windows[-1])
        print(f"Popup pencereye geçildi: {driver.title}")

    frames = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Frame sayısı: {len(frames)}")
    for i, frame in enumerate(frames):
        print(f"  Frame {i}: id='{frame.get_attribute('id')}', "
              f"name='{frame.get_attribute('name')}', "
              f"src='{frame.get_attribute('src')}'")

    drw_prefix = f"DRW_{part_number}"

    def find_drw_link():
        links = driver.find_elements(By.PARTIAL_LINK_TEXT, "DRW_")
        for link in links:
            if link.text.strip().startswith(drw_prefix):
                return link
        return None

    link = find_drw_link()
    if link:
        print(f"Tıklanıyor: {link.text}")
        link.click()
        return

    for i, frame in enumerate(frames):
        try:
            driver.switch_to.frame(frame)
            link = find_drw_link()
            if link:
                print(f"Frame {i} içinde bulundu. Tıklanıyor: {link.text}")
                link.click()
                return
            inner_frames = driver.find_elements(By.TAG_NAME, "iframe")
            for j, inner in enumerate(inner_frames):
                try:
                    driver.switch_to.frame(inner)
                    link = find_drw_link()
                    if link:
                        print(f"Frame {i}/{j} içinde bulundu. Tıklanıyor: {link.text}")
                        link.click()
                        return
                    driver.switch_to.parent_frame()
                except Exception:
                    driver.switch_to.parent_frame()
            driver.switch_to.default_content()
        except Exception:
            driver.switch_to.default_content()

    raise Exception(f"'{drw_prefix}' ile başlayan link bulunamadı!")


def click_tab_in_frames(driver, tab_text):
    """Tüm frame'lerde belirtilen metni içeren sekmeyi bulup tıklar."""
    def find_tab():
        short_text = tab_text[:14] if len(tab_text) > 14 else tab_text
        links = driver.find_elements(By.PARTIAL_LINK_TEXT, short_text)
        if links:
            return links[0]
        spans = driver.find_elements(By.XPATH, f"//*[contains(text(), '{short_text}')]")
        for span in spans:
            if span.is_displayed():
                return span
        xpath = "/html/body/div/div[3]/div[1]/ul/li[5]/div"
        elements = driver.find_elements(By.XPATH, xpath)
        if elements:
            return elements[0]
        return None

    tab = find_tab()
    if tab:
        print(f"Sekme bulundu: {tab.text}")
        tab.click()
        return

    frames = driver.find_elements(By.TAG_NAME, "iframe")
    for i, frame in enumerate(frames):
        try:
            driver.switch_to.frame(frame)
            tab = find_tab()
            if tab:
                print(f"Frame {i} içinde sekme bulundu: {tab.text}")
                tab.click()
                return
            inner_frames = driver.find_elements(By.TAG_NAME, "iframe")
            for j, inner in enumerate(inner_frames):
                try:
                    driver.switch_to.frame(inner)
                    tab = find_tab()
                    if tab:
                        print(f"Frame {i}/{j} içinde sekme bulundu: {tab.text}")
                        tab.click()
                        return
                    driver.switch_to.parent_frame()
                except Exception:
                    driver.switch_to.parent_frame()
            driver.switch_to.default_content()
        except Exception:
            driver.switch_to.default_content()

    raise Exception(f"'{tab_text}' sekmesi bulunamadı!")


def click_derived_output(driver):
    """Derived Output sekmesine tıklar."""
    driver.switch_to.default_content()
    click_tab_in_frames(driver, "Derived Output")


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
    time.sleep(15)

    driver.switch_to.default_content()
    click_derived_output(driver)

    print("Derived Output yükleniyor...")
    time.sleep(5)
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
