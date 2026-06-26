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
import getpass
import winreg
import subprocess


def dismiss_alerts(driver, label=""):
    """Açık olan PLM uyarı pencerelerini (alert) kapatır."""
    closed = 0
    for _ in range(5):
        try:
            alert = driver.switch_to.alert
            text = alert.text
            alert.accept()
            closed += 1
            print(f"Uyarı kapatıldı{(' (' + label + ')') if label else ''}: {text}")
            time.sleep(0.5)
        except Exception:
            break
    return closed


def paste_text(element, text):
    """Clipboard üzerinden yapıştırarak hızlı metin girer (IE driver send_keys çok yavaş)."""
    subprocess.run(["clip.exe"], input=text.encode("utf-16-le"), check=True)
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.CONTROL, "v")
    time.sleep(0.3)


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
    # PLM'in fırlattığı uyarı (alert) pencerelerini otomatik kapat (OK)
    options.unhandled_prompt_behavior = "accept"

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


SEARCH_SELECTORS = [
    "input#AEFGlobalFullTextSearchInput",
    "input[name='AEFGlobalFullTextSearchInput']",
    "input[type='text'][id*='Search']",
    "input[type='text'][id*='search']",
    "input.search-input",
]


def _type_search_recursive(driver, query, depth=0, max_depth=4):
    """Mevcut frame ve iç frame'lerde arama kutusunu bulup yazar.
    IE modu uyumlu: get_attribute kullanmaz."""
    for sel in SEARCH_SELECTORS:
        for el in driver.find_elements(By.CSS_SELECTOR, sel):
            try:
                if el.is_displayed() and el.is_enabled():
                    el.click()
                    paste_text(el, query)
                    el.send_keys(Keys.RETURN)
                    print(f"Arama yapıldı (selector: {sel})")
                    return True
            except Exception:
                continue

    if depth >= max_depth:
        return False

    for fr in driver.find_elements(By.CSS_SELECTOR, "frame, iframe"):
        try:
            driver.switch_to.frame(fr)
        except Exception:
            continue
        if _type_search_recursive(driver, query, depth + 1, max_depth):
            return True
        driver.switch_to.parent_frame()
    return False


def search_part(driver, part_number):
    """PLM arama kutusuna *parça_numarası* yazıp aratır (tüm frame'lerde arar)."""
    search_query = f"*{part_number}*"

    # Arama kutusu birkaç saniye sonra render olabilir - tekrar dene
    for attempt in range(6):
        dismiss_alerts(driver, "arama öncesi")
        driver.switch_to.default_content()
        try:
            if _type_search_recursive(driver, search_query):
                return
        except Exception as e:
            print(f"Arama denemesi {attempt+1} hata: {e}")
            dismiss_alerts(driver, "arama hatası")
        time.sleep(2)

    raise Exception("Arama kutusu bulunamadı! Sayfanın yüklendiğinden emin olun.")


def _click_drw_recursive(driver, drw_prefix, depth=0, max_depth=4):
    """Mevcut frame ve iç frame'lerde DRW_ linkini bulup tıklar (IE uyumlu)."""
    for link in driver.find_elements(By.PARTIAL_LINK_TEXT, "DRW_"):
        try:
            txt = link.text.strip()
        except Exception:
            continue
        if txt.startswith(drw_prefix):
            print(f"Tıklanıyor: {txt}")
            link.click()
            return True

    if depth >= max_depth:
        return False

    for fr in driver.find_elements(By.CSS_SELECTOR, "frame, iframe"):
        try:
            driver.switch_to.frame(fr)
        except Exception:
            continue
        if _click_drw_recursive(driver, drw_prefix, depth + 1, max_depth):
            return True
        driver.switch_to.parent_frame()
    return False


def click_latest_drawing(driver, part_number):
    """Arama sonuçlarında DRW_<part> linkini bulup tıklar.
    Sonuçlar popup pencerede açılırsa o pencereye geçer."""
    drw_prefix = f"DRW_{part_number}"

    # Sonuçların yüklenmesi için birkaç kez dene (popup + frame'ler)
    for attempt in range(8):
        # Yeni pencere açıldıysa sonuncusuna geç
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])
        driver.switch_to.default_content()

        if _click_drw_recursive(driver, drw_prefix):
            return
        time.sleep(2)

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


def get_credentials():
    """Kimlik bilgilerini ortam değişkeninden ya da cmd'den (gizli) alır.
    Repoda hiçbir şifre saklanmaz."""
    username = os.environ.get("PLM_USER")
    password = os.environ.get("PLM_PASS")
    if not username:
        username = input("PLM kullanici adi: ").strip()
    if not password:
        password = getpass.getpass("PLM sifre: ")
    return username, password


def login(driver, username, password):
    """PLM login formunu (j_username / password) doldurup gönderir."""
    driver.switch_to.default_content()

    user_field = None
    user_els = driver.find_elements(By.NAME, "j_username")
    if not user_els:
        user_els = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
    if user_els:
        user_field = user_els[0]

    pass_els = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")

    if not user_field or not pass_els:
        print("Login formu bulunamadı (zaten giriş yapılmış olabilir).")
        return

    pass_field = pass_els[0]
    user_field.click()
    paste_text(user_field, username)
    pass_field.click()
    paste_text(pass_field, password)
    pass_field.send_keys(Keys.RETURN)
    print("Giriş bilgileri gönderildi, bekleniyor...")
    time.sleep(8)


def main():
    # Kimlik bilgilerini Edge açılmadan önce al
    username, password = get_credentials()

    print("Edge başlatılıyor...")
    driver = open_edge_and_connect()
    print(f"Bağlanıldı. Sayfa: {driver.title}")

    print("Login deneniyor...")
    login(driver, username, password)

    print("PLM sayfasının tam yüklenmesi bekleniyor...")
    time.sleep(5)
    dismiss_alerts(driver, "sayfa yükleme sonrası")

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
