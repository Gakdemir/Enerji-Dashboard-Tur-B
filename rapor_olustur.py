from fpdf import FPDF

class Rapor(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "VALEO Enerji Dashboard - Proje Raporu", align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Sayfa {self.page_no()}/{{nb}}", align="C")

    def baslik(self, text, size=16):
        if self.get_y() > 240:
            self.add_page()
        self.set_font("DejaVu", "B", size)
        self.set_text_color(21, 101, 192)
        self.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(21, 101, 192)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def altbaslik(self, text):
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def govde(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def madde(self, text):
        self.set_font("DejaVu", "", 10)
        self.set_text_color(50, 50, 50)
        self.cell(6, 6, chr(8226))
        self.multi_cell(0, 6, text)
        self.ln(1)

    def prompt_kutusu(self, baslik, icerik):
        self.set_fill_color(240, 244, 248)
        self.set_draw_color(21, 101, 192)
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(21, 101, 192)
        self.cell(0, 7, baslik, new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 9)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5.5, icerik, fill=True, border=1)
        self.ln(4)


pdf = Rapor()
pdf.alias_nb_pages()

pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
pdf.add_font("DejaVu", "I", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

pdf.set_auto_page_break(auto=True, margin=20)

# ── KAPAK ──
pdf.add_page()
pdf.ln(70)
pdf.set_font("DejaVu", "B", 36)
pdf.set_text_color(21, 101, 192)
pdf.cell(0, 18, "VALEO", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 18, "Enerji Dashboard (S6)", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)
pdf.set_draw_color(21, 101, 192)
line_w = 80
pdf.line((pdf.w - line_w) / 2, pdf.get_y(), (pdf.w + line_w) / 2, pdf.get_y())
pdf.ln(8)
pdf.set_font("DejaVu", "", 16)
pdf.set_text_color(100, 100, 100)
pdf.cell(0, 10, "Tur B - Proje Raporu", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(40)

pdf.set_text_color(60, 60, 60)
bilgiler = [
    ("Ad-Soyad:", "Gürsan Akdemir"),
    ("Ekip:", "Ar-ge"),
    ("Kullanılan Araç:", "Claude (Anthropic)"),
    ("Senaryo:", "S6 - Enerji Tüketim Takibi"),
    ("Tarih:", "Haziran 2025"),
]
for etiket, deger in bilgiler:
    pdf.set_font("DejaVu", "B", 13)
    pdf.cell(65, 10, etiket, align="R")
    pdf.set_font("DejaVu", "", 13)
    pdf.cell(0, 10, f"  {deger}", new_x="LMARGIN", new_y="NEXT")

# ── BÖLÜM 1 + 2: aynı sayfada başlasın ──
pdf.add_page()
pdf.baslik("1. Kapak Bilgileri")
pdf.govde(
    "Bu proje, VALEO üretim tesisinin enerji tüketimini izlemek amacıyla "
    "geliştirilen interaktif bir dashboard çalışmasıdır. Proje bireysel olarak "
    "yürütülmüş ve yapay zeka aracı olarak Claude (Anthropic) kullanılmıştır."
)
pdf.govde(
    "Senaryo: S6 - Enerji Tüketim Takibi. Dashboard, üretim hatlarının elektrik "
    "ve doğalgaz tüketimini gerçek zamanlı olarak izler, hedef değerlerle karşılaştırır "
    "ve sapmaları görselleştirir."
)

pdf.baslik("2. Senaryo ve Persona")
pdf.altbaslik("Pano kimin için?")
pdf.govde(
    "VALEO üretim tesisinin enerji yöneticisi ve vardiya mühendisleri için tasarlanmıştır. "
    "Bu kişiler günlük olarak hangi hattın ne kadar enerji tükettiğini, hedeflerin aşılıp "
    "aşılmadığını ve CO2 etkisini takip etmek zorundadır."
)
pdf.altbaslik("Hangi karar için?")
pdf.govde(
    "Enerji yöneticisi bu pano ile şu kararları alır:\n"
    "- Hangi üretim hattı hedefin üzerinde tüketiyor ve müdahale gerekiyor?\n"
    "- Elektrik mi doğalgaz mı daha fazla sapma gösteriyor?\n"
    "- Haftalık/aylık enerji trendi iyiye mi kötüye mi gidiyor?"
)
pdf.altbaslik("Panodaki 3 temel soru")
pdf.madde("Birim başına enerji tüketimi hedefin ne kadar üzerinde/altında?")
pdf.madde("Hangi hat en çok enerji tüketiyor (Pareto analizi)?")
pdf.madde("Zaman içinde tüketim trendi nasıl değişiyor?")

# ── BÖLÜM 3: MİMARİ ŞEMA ── (yeni sayfa - kutular kesilmesin)
pdf.add_page()
pdf.baslik("3. Mimari Şeması")
pdf.govde(
    "Aşağıdaki şema, sistemin dört ana katmanını ve aralarındaki veri akışını gösterir:"
)

pdf.set_auto_page_break(auto=False)

y = pdf.get_y() + 4
bw, bh = 80, 14
bx = (pdf.w - bw) / 2
gap = 8

boxes = [
    ("CANLI VERİ", "(Google Sheets - CSV)", (21, 101, 192)),
    ("VERİ İŞLEME", "(Ayrıştır - Dönüştür)", (46, 125, 50)),
    ("KURALLAR & STANDART", "(Hedef, Formül, Eşik)", (198, 40, 40)),
    ("BAĞLAM (UI)", "(KPI, Grafik, Tablo)", (249, 168, 37)),
]

for i, (baslik_txt, alt, renk) in enumerate(boxes):
    by = y + i * (bh + gap)
    pdf.set_fill_color(*renk)
    pdf.set_draw_color(*renk)
    pdf.rect(bx, by, bw, bh, style="F")
    pdf.set_xy(bx, by + 1.5)
    pdf.set_font("DejaVu", "B", 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(bw, 5, baslik_txt, align="C")
    pdf.set_xy(bx, by + 7)
    pdf.set_font("DejaVu", "", 7)
    pdf.cell(bw, 5, alt, align="C")

    if i < len(boxes) - 1:
        ax = pdf.w / 2
        ay1 = by + bh
        ay2 = by + bh + gap
        pdf.set_draw_color(100, 100, 100)
        pdf.line(ax, ay1, ax, ay2)
        pdf.line(ax - 2, ay2 - 3, ax, ay2)
        pdf.line(ax + 2, ay2 - 3, ax, ay2)

pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_y(y + len(boxes) * (bh + gap) + 4)

pdf.govde(
    "Akış: Google Sheets'ten her 5 dakikada CSV olarak veri çekilir. "
    "Veri işleme katmanında TR locale dönüşümü ve sütun eşleme yapılır. "
    "Kurallar katmanında hedef sapma, CO2 ve durum hesaplanır. "
    "Son olarak kullanıcı arayüzünde filtreler, KPI kartları, grafikler ve tablo olarak sunulur."
)

# ── BÖLÜM 4: BAĞLAM ── (devam, yeni sayfa yok)
pdf.baslik("4. Bağlamı Sade Tutmak ve Önemi")
pdf.govde(
    "Claude ile çalışırken bağlamı (context) sade tutmak projenin en kritik başarı "
    "faktörlerinden biriydi. Bunun NEDEN önemli olduğu:"
)
pdf.madde(
    "Odak kaybını önler: AI'ya tek seferde tüm dashboard'u tarif etmek yerine, "
    "her seferinde tek bir bileşen (KPI paneli, grafik, tablo) üzerinde çalışmak "
    "çok daha tutarlı sonuçlar verdi."
)
pdf.madde(
    "Hata ayıklamayı kolaylaştırır: Bir hesaplama hatası çıktığında (örneğin üretim "
    "adedinin çift sayılması), sorunu izole edip sadece o fonksiyonu düzeltmek "
    "mümkün oldu."
)
pdf.madde(
    "Tekrarlanabilirlik sağlar: Kalıcı talimat dosyası (kalici-talimat.md) ve üretim "
    "standardı (uretim-standardi.md) ayrı dosyalarda tutularak her yeni iterasyonda "
    "aynı kuralların uygulanması garanti edildi."
)
pdf.govde(
    "Nasıl sade tuttuk: Her prompt'ta yalnızca o anki göreve ait bilgiyi verdik. "
    "Kuralları ayrı dosyalarda sakladık. Veriyi kod içine gömmek yerine Google Sheets'ten "
    "canlı çektik, böylece veri bağlamı kirletmedi."
)

# ── BÖLÜM 5: TUR A / TUR B ── (devam, yeni sayfa yok)
pdf.baslik("5. Tur A ile Tur B Karşılaştırması")

pdf.set_font("DejaVu", "B", 10)
pdf.set_fill_color(21, 101, 192)
pdf.set_text_color(255, 255, 255)
col_w = [45, 70, 70]
headers = ["Kriter", "Tur A", "Tur B"]
for i, h in enumerate(headers):
    pdf.cell(col_w[i], 8, h, border=1, fill=True, align="C")
pdf.ln()

pdf.set_font("DejaVu", "", 9)
pdf.set_text_color(50, 50, 50)
rows = [
    ("Veri kaynağı", "Statik / gömülü veri", "Canlı Google Sheets"),
    ("Kural yönetimi", "Prompt içinde dağınık", "Ayrı .md dosyalarında"),
    ("Hesaplama", "Basit toplam/ort.", "Ağırlıklı sapma, CO2"),
    ("Grafik çeşidi", "Tek grafik", "Trend + Pareto + Tablo"),
    ("Yenileme", "Manuel", "5 dk otomatik"),
    ("Hata yönetimi", "Yok/minimal", "Boş veri ve hata mesajları"),
    ("Tasarım standardı", "Yoktu", "uretim-standardi.md"),
    ("İterasyon sayısı", "1-2", "6+ (git geçmişi)"),
]
for kriter, a, b in rows:
    pdf.set_fill_color(245, 247, 250)
    pdf.cell(col_w[0], 7, kriter, border=1)
    pdf.cell(col_w[1], 7, a, border=1, align="C")
    pdf.cell(col_w[2], 7, b, border=1, align="C")
    pdf.ln()

pdf.ln(4)
pdf.govde(
    "En büyük fark: Tur A'da her şey tek seferde üretilip bırakılırken, "
    "Tur B'de kalıcı kurallar, üretim standardı ve canlı veri bağlantısı sayesinde "
    "iteratif bir geliştirme süreci izlendi. Her commit bir iyileştirme adımıydı."
)

# ── BÖLÜM 6: ETKİLİ PROMPTLAR ── (devam)
pdf.baslik("6. En Etkili 3-5 Prompt")

pdf.prompt_kutusu(
    "Prompt 1 - Canlı Veri Bağlantısı",
    "\"Google Sheets'teki veriyi CSV olarak fetch ile çek. Ayracı otomatik tespit et "
    "(; veya ,). Sütun adlarını esnek eşle (büyük/küçük harf, boşluk farketmesin). "
    "TR locale sayı formatını (1.234,56) doğru parse et. 5 dakikada bir otomatik yenile.\""
)
pdf.govde(
    "NEDEN etkili: Veri bağlantısının tüm edge case'lerini tek prompt'ta tanımladık. "
    "Ayraç tespiti ve esnek kolon eşleme sayesinde Google Sheets formatı değişse bile "
    "dashboard çalışmaya devam etti."
)

pdf.prompt_kutusu(
    "Prompt 2 - S6 Formül Tanımı",
    "\"Birim başına kWh = Tüketim (kWh) / Üretim Adedi formülünü kullan. "
    "Hedef Sapma % = ((Birim kWh - Hedef) / Hedef) x 100. "
    "Aynı hat+tarih'te birden fazla enerji tipi varsa üretim adedini çift sayma. "
    "Toplam sapma hesabında enerji tiplerinin ağırlıklı ortalamasını al.\""
)
pdf.govde(
    "NEDEN etkili: İş mantığını matematiksel formüllerle net tanımlamak belirsizliği "
    "sıfıra indirdi. Özellikle 'çift sayma' uyarısı kritik bir bug'ı önledi."
)

pdf.prompt_kutusu(
    "Prompt 3 - Durum Renklendirme Kuralı",
    "\"Sapma % hesapla: hedefin altındaysa yeşil + 'İyi', +-5% arasındaysa sarı + 'Normal', "
    "%5 üzerindeyse kırmızı + 'Kötü' yaz. Renk tek başına anlam taşımasın, "
    "yanına mutlaka metin etiketi koy (erişilebilirlik).\""
)
pdf.govde(
    "NEDEN etkili: Hem iş kuralını (eşik değerleri) hem de tasarım kuralını "
    "(erişilebilirlik) tek prompt'ta birleştirdik. Claude her iki kuralı da tutarlı uyguladı."
)

pdf.prompt_kutusu(
    "Prompt 4 - Pareto Grafiği",
    "\"Hat bazında toplam tüketimi bar grafik olarak göster, büyükten küçüğe sırala. "
    "Üzerine kümülatif % çizgisi ekle (Pareto). Chart.js kullan, "
    "ikinci y ekseni % için olsun.\""
)
pdf.govde(
    "NEDEN etkili: Grafik tipini, sıralamayı ve çift eksen detayını vermek "
    "Claude'un doğru grafik yapısını ilk seferde üretmesini sağladı."
)

pdf.prompt_kutusu(
    "Prompt 5 - Geri Alma ve Sadeleştirme",
    "\"Son eklenen sparkline ve haftalık trend özelliklerini geri al. "
    "KPI kartlarını sade versiyona döndür. Fazla bilgi kullanıcıyı bunaltıyor, "
    "tek ekranda okunabilir olması öncelikli.\""
)
pdf.govde(
    "NEDEN etkili: 'Daha fazla özellik = daha iyi' yanılgısından dönmek önemli bir karardı. "
    "Bu prompt, tasarım ilkesini (sadelik) teknik talimatla birleştirdi."
)

# ── BÖLÜM 7: ZORLUKLAR ── (devam)
pdf.baslik("7. Karşılaşılan Zorluklar")

pdf.altbaslik("Zorluk 1: Üretim Adedinin Çift Sayılması")
pdf.govde(
    "Sorun: Aynı hat ve tarihte hem elektrik hem doğalgaz kaydı olduğunda, üretim adedi "
    "iki kez toplanıyordu. Bu da birim başına kWh değerini yarıya düşürüyordu."
)
pdf.govde(
    "Çözüm: Benzersiz hat+tarih kombinasyonlarını takip eden bir Set yapısı kullanıldı. "
    "Üretim adedi yalnızca ilk karşılaşmada toplama eklendi. Bu düzeltme git geçmişinde "
    "\"fix: üretim çift sayımını düzelt\" commit'inde görülebilir."
)

pdf.altbaslik("Zorluk 2: Google Sheets CSV Format Uyumsuzluğu")
pdf.govde(
    "Sorun: Google Sheets CSV export'u bazen noktalı virgül (;), bazen virgül (,) ayracı "
    "kullanıyordu. Ayrıca TR locale'de sayılar 1.234,56 formatındaydı ve standart "
    "parseFloat() bu formatı anlayamıyordu."
)
pdf.govde(
    "Çözüm: Otomatik ayraç tespiti eklendi (ilk satırda hangi karakter daha çok geçiyorsa "
    "o ayraç olarak seçildi). Sayı dönüşümü için özel parseNum() fonksiyonu yazıldı: "
    "önce nokta (binlik ayraç) kaldırılıp, virgül noktaya çevrildi. Bu iteratif süreç "
    "birkaç commit aldı ama sonunda sağlam bir çözüme ulaşıldı."
)

# ── BÖLÜM 8: KENDİNE NOT ── (devam)
pdf.baslik("8. Kendime Notlarım")

pdf.altbaslik("Neyi iyi yaptım?")
pdf.madde(
    "Kuralları ayrı dosyalarda tutmak (kalici-talimat.md, uretim-standardi.md) "
    "baştan doğru bir karardı. Her iterasyonda tutarlılığı korudu."
)
pdf.madde(
    "Git kullanarak her adımı commit'lemek, hataları geri almayı ve ilerlemeyi "
    "takip etmeyi çok kolaylaştırdı (örn: sparkline eklendi, sonra geri alındı)."
)
pdf.madde(
    "Canlı veri bağlantısı kurmak dashboard'u gerçek bir araç haline getirdi, "
    "statik bir demo olmaktan çıkardı."
)

pdf.altbaslik("Neyi geliştirebilirim?")
pdf.madde(
    "Prompt'ları daha erken aşamada belgelemeliydim. Hangi prompt'un hangi "
    "sonucu verdiğini sonradan hatırlamak zor oldu."
)
pdf.madde(
    "Mobil uyumluluk (responsive design) eksik kaldı. Dashboard masaüstü için "
    "optimize edildi ama tablet/telefonda kullanılabilirlik düşük."
)
pdf.madde(
    "Test senaryoları yazmalıydım. Boş veri, eksik sütun, çok büyük sayılar gibi "
    "edge case'leri sistematik test etmek yerine manuel deneme ile ilerledim."
)

pdf.output("/home/user/Enerji-Dashboard-Tur-B/rapor.pdf")
print("rapor.pdf oluşturuldu!")
