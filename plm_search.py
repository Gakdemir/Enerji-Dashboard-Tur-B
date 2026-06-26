"""
Enovia PLM'de parça arama otomasyonu - Edge'i IE MODUNDA sürer.

ÖNEMLİ: PLM sitesi Internet Explorer modu gerektiriyor. Bu yüzden
remote-debugging yerine IEDriverServer ile Edge IE modunda sürülür.

KURULUM (tek seferlik):
  1) IEDriverServer.exe (64-bit) indir:
     https://www.selenium.dev/downloads/  (Internet Explorer Driver, x64)
     ve aşağıdaki IEDRIVER_PATH yoluna koy (ör. C:\\WebDriver\\IEDriverServer.exe)
  2) Tüm Edge pencerelerini kapat
  3) Bu scripti çalıştır (registry ayarını otomatik yapar)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.ie.service import Service as IEService
from selenium.webdriver.ie.options import Options as IEOptions
import time
import os
import winreg


PLM_URL = "https://plm.vnet.valeo.com:7001/enovia/common/emxNavigator.jsp"
PART_NUMBER = "C597104"

# IEDriverServer.exe'nin tam yolu (indirip buraya koy)
IEDRIVER_PATH = r"C:\WebDriver\IEDriverServer.exe"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def ensure_ie_registry():
    """IE driver'ın çalışması için gereken registry anahtarını ayarlar.
    HKCU altında olduğu için admin gerektirmez."""
    try:
        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Internet Explorer\Main",
        )
        winreg.SetValueEx(key, "TabProcGrowth", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print("Registry ayarı tamam (TabProcGrowth=0).")
    except Exception as e:
        print(f"UYARI: Registry ayarı yapılamadı: {e}")


def open_edge_and_connect():
    """Edge'i IE modunda başlatıp IEDriverServer ile bağlanır."""
    ensure_ie_registry()

    options = IEOptions()
    options.attach_to_edge_chrome = True
    options.edge_executable_path = EDGE_PATH
    options.ignore_zoom_level = True
    options.ignore_protected_mode_settings = True
    options.require_window_focus = False

    if os.path.isfile(IEDRIVER_PATH):
        print(f"IEDriverServer kullanılıyor: {IEDRIVER_PATH}")
        service = IEService(executable_path=IEDRIVER_PATH)
        driver = webdriver.Ie(service=service, options=options)
    else:
        print("IEDRIVER_PATH bulunamadı; Selenium Manager otomatik indirmeyi deniyor...")
        driver = webdriver.Ie(options=options)

    print("Edge IE modunda açıldı, PLM'e gidiliyor...")
    driver.get(PLM_URL)
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


def _click_tab_recursive(driver, matches, depth=0, max_depth=4):
    """Mevcut frame ve iç frame'lerde eşleşen sekmeyi bulup JS ile tıklar."""
    # Sekme genelde <a>, <div>, <span>, <td> veya <li> elemanı (anchor olmayabilir)
    candidates = driver.find_elements(
        By.XPATH, "//*[self::a or self::div or self::span or self::td or self::li]"
    )
    for el in candidates:
        try:
            txt = el.text.strip()
        except Exception:
            continue
        # "Derived Output (3)" gibi kısa bir etiket olmalı (uzun container'ları ele)
        if txt and matches(txt) and len(txt) <= 22 and el.is_displayed():
            driver.execute_script("arguments[0].click();", el)
            print(f"Sekmeye tıklandı: '{txt}'")
            return True

    if depth >= max_depth:
        return False

    frames = driver.find_elements(By.CSS_SELECTOR, "frame, iframe")
    for fr in frames:
        try:
            driver.switch_to.frame(fr)
        except Exception:
            continue
        if _click_tab_recursive(driver, matches, depth + 1, max_depth):
            return True
        driver.switch_to.parent_frame()
    return False


def click_derived_output(driver, timeout=45):
    """Derived Output sekmesi görünene kadar bekleyip tıklar.

    Not: Properties sekmesi IE modu gerektirdiği için 'Loading'de kalabilir,
    ama Derived Output sekmesine tıklamak için onu beklemeye gerek yok.
    """
    def matches(t):
        return t.startswith("Derived Output")

    end = time.time() + timeout
    while time.time() < end:
        driver.switch_to.default_content()
        if _click_tab_recursive(driver, matches):
            return
        time.sleep(2)

    raise Exception("Derived Output sekmesi bulunamadı!")


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

    # Properties sekmesi 'Loading'de kalabilir (IE modu) - beklemeden
    # doğrudan Derived Output sekmesine geçiyoruz. Tab çubuğu zaten DOM'da.
    print("Drawing sayfası açılıyor, Derived Output sekmesi aranıyor...")
    time.sleep(3)
    click_derived_output(driver)

    print("Derived Output içeriği yükleniyor...")
    time.sleep(5)
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
