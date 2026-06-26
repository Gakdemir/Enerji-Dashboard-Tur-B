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


PLM_URL = "https://plm.vnet.valeo.com:7001/enovia/common/emxNavigator.jsp"
PART_NUMBER = "C597104"


def open_edge_and_connect():
    """Edge'i Selenium ile başlatır (debug modu olmadan)."""
    options = webdriver.EdgeOptions()
    options.add_argument(r"--user-data-dir=C:\EdgeSeleniumProfile")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-features=msEdgeIEModeTest")

    driver = webdriver.Edge(options=options)
    print("Edge açıldı, PLM'e gidiliyor...")
    driver.get(PLM_URL)

    print("Sayfa yüklenmesi bekleniyor...")
    time.sleep(10)
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
    """Arama sonuçları popup'ında DRW satırına XPath ile tıklar."""
    # Arama sonuçları popup pencerede açılıyor - ona geç
    main_window = driver.current_window_handle
    all_windows = driver.window_handles
    print(f"Toplam pencere sayısı: {len(all_windows)}")

    for w in all_windows:
        driver.switch_to.window(w)
        print(f"  Pencere: {driver.title} - URL: {driver.current_url}")

    # Son pencereye (popup) geç
    if len(all_windows) > 1:
        driver.switch_to.window(all_windows[-1])
        print(f"Popup pencereye geçildi: {driver.title}")

    # Frame'leri listele
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

    def click_or_navigate(link, label):
        """Linkin href'ini alıp ana pencerede navigate et."""
        href = link.get_attribute("href")
        onclick = link.get_attribute("onclick")
        print(f"{label}: text='{link.text}', href='{href}', onclick='{onclick}'")
        if href and href != "#" and "javascript:" not in href:
            driver.switch_to.default_content()
            driver.get(href)
        elif onclick:
            driver.switch_to.default_content()
            driver.execute_script(onclick)
        else:
            link.click()

    # Önce mevcut sayfada dene
    link = find_drw_link()
    if link:
        click_or_navigate(link, "Sayfada bulundu")
        return

    # Tüm frame'lerin içinde ara
    for i, frame in enumerate(frames):
        try:
            driver.switch_to.frame(frame)
            link = find_drw_link()
            if link:
                click_or_navigate(link, f"Frame {i} içinde bulundu")
                return
            inner_frames = driver.find_elements(By.TAG_NAME, "iframe")
            for j, inner in enumerate(inner_frames):
                try:
                    driver.switch_to.frame(inner)
                    link = find_drw_link()
                    if link:
                        click_or_navigate(link, f"Frame {i}/{j} içinde bulundu")
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
        # İlk 14 karakter ("Derived Output") ile ara
        short_text = tab_text[:14] if len(tab_text) > 14 else tab_text
        links = driver.find_elements(By.PARTIAL_LINK_TEXT, short_text)
        if links:
            return links[0]
        spans = driver.find_elements(By.XPATH, f"//*[contains(text(), '{short_text}')]")
        for span in spans:
            if span.is_displayed():
                return span
        # XPath ile de dene
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
    # Loading animasyonunun bitmesini bekle (max 60 sn)
    for i in range(12):
        time.sleep(5)
        driver.switch_to.default_content()
        # "Derived Output" sekmesi görünür olduysa sayfa yüklenmiştir
        try:
            frames = driver.find_elements(By.TAG_NAME, "iframe")
            for frame in frames:
                try:
                    driver.switch_to.frame(frame)
                    tabs = driver.find_elements(By.PARTIAL_LINK_TEXT, "Derived")
                    if tabs:
                        print(f"Sayfa yüklendi ({(i+1)*5} sn sonra)")
                        driver.switch_to.default_content()
                        break
                    driver.switch_to.default_content()
                except Exception:
                    driver.switch_to.default_content()
            else:
                continue
            break
        except Exception:
            pass
    else:
        print("Sayfa yüklenmesi 60 saniyeyi aştı, devam ediliyor...")

    driver.switch_to.default_content()
    click_derived_output(driver)

    print("Derived Output yükleniyor...")
    time.sleep(5)
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
