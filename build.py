#!/usr/bin/env python3
"""OH Temizlik sitesini üretir.

Ortak üst/alt bilgi, hizmet listesi ve ilçe listesi tek yerde durur;
`python3 build.py` çalıştırınca tüm HTML sayfaları yeniden yazılır.
"""
import html
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
SITE_URL = "https://ohtemizlik.com"
PHONE_DISPLAY = "0532 120 53 38"
PHONE_TEL = "+905321205338"
WA_NUMBER = "905321205338"
EMAIL = "info@ohtemizlik.com"
ARMUT_PDF = "https://s3.eu-central-1.amazonaws.com/prokit-materials/live/50714e292cb1916131ade2221dec7c2d.pdf"
VERSION = "1"


def wa(msg="Merhaba, temizlik hizmeti için teklif almak istiyorum."):
    return f"https://wa.me/{WA_NUMBER}?text={quote(msg)}"


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- ikonlar
_P = {
    "home": '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v9.5h13V10"/><path d="M10 19.5v-5h4v5"/>',
    "villa": '<path d="M2.5 12 9 6.5l6.5 5.5"/><path d="M4.5 10.5v9h9v-9"/><path d="M15.5 12h6v7.5h-6"/><path d="M7.5 19.5v-4h3v4"/>',
    "building": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5h6v2"/><path d="M3 12.5h18"/>',
    "store": '<path d="M4 9.5V20h16V9.5"/><path d="M3.5 9.5 5.5 4h13l2 5.5Z"/><path d="M10 20v-5h4v5"/>',
    "cup": '<path d="M4 9h12v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5Z"/><path d="M16 10.5h1.5a2.5 2.5 0 0 1 0 5H16"/><path d="M8 3.5v2.5M12 3.5v2.5"/>',
    "cross": '<path d="M9 3.5h6v5.5h5.5v6H15v5.5H9V15H3.5V9H9Z"/>',
    "hardhat": '<path d="M3.5 17.5h17"/><path d="M5 17.5V15a7 7 0 0 1 14 0v2.5"/><path d="M10 8.3V6h4v2.3"/>',
    "crane": '<path d="M6 21V4h14"/><path d="M6 8l4-4"/><path d="M16 4v6"/><path d="M14 10h4v3.5h-4Z"/><path d="M3 21h6"/>',
    "machine": '<path d="M10 3h4"/><path d="M12 3v10"/><path d="M5 17.5a7 4.5 0 0 1 14 0V20H5Z"/>',
    "booth": '<path d="M3 7h18"/><path d="M5 7v13M19 7v13"/><path d="M3 20h18"/><path d="M9 11h6v5H9Z"/><path d="M5 4h14v3H5Z"/>',
    "boat": '<path d="M3 15h18l-2.5 4.5h-13Z"/><path d="M12 3v12"/><path d="M12 4.5l6 8.5h-6"/>',
    "container": '<rect x="2.5" y="7" width="19" height="11" rx="1"/><path d="M7 7v11M11.5 7v11M16 7v11"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "doc": '<path d="M7 3h7l5 5v13H7Z"/><path d="M14 3v5h5"/><path d="M10 13h6M10 17h4"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "map": '<path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6Z"/><path d="M9 4v14M15 6v14"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4Z"/><path d="M8 9.5h8M8 12.5h5"/>',
}
_WA = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.46-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.18.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.91-2.2-.25-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.42-.08-.12-.27-.2-.57-.34m-5.42 7.4h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88m8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89a11.82 11.82 0 0 0-3.48-8.41Z"/></svg>')


def icon(name):
    if name == "wa":
        return _WA
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_P[name]}</svg>')


LOGO = ('<svg viewBox="0 0 48 48" aria-hidden="true">'
        '<rect width="48" height="48" rx="13" fill="#0f6e6a"/>'
        '<path d="M11 24c5 10 21 10 26 0" fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round"/>'
        '<path d="M33 8.5l1.6 4 4 1.6-4 1.6-1.6 4-1.6-4-4-1.6 4-1.6Z" fill="#f4c84a"/>'
        '<path d="M15 13.5l.9 2.2 2.2.9-2.2.9-.9 2.2-.9-2.2-2.2-.9 2.2-.9Z" fill="#f4c84a"/>'
        '</svg>')

# ---------------------------------------------------------------- içerik
GROUPS = [
    {
        "id": "yasam-alanlari",
        "title": "Yaşam alanları",
        "intro": "Ev, villa ve apartmanlarda düzenli ya da tek seferlik temizlik.",
        "services": [
            ("ev-temizligi", "Ev temizliği", "home",
             "Odalar, mutfak, banyo ve ortak yaşam alanlarının baştan sona temizliği.",
             ["Mutfak dolapları, tezgâh ve ocak çevresi", "Banyo ve tuvaletlerde kireç ve leke temizliği",
              "Zemin, kapı, pencere ve süpürgelik silme"]),
            ("villa-temizligi", "Villa temizliği", "villa",
             "Çok katlı ve geniş yaşam alanları için ekip olarak planlanan temizlik.",
             ["Tüm katlar ve odalar", "Geniş cam yüzeyler ve korkuluklar", "Teras ve balkon alanları"]),
            ("apartman-temizligi", "Apartman temizliği", "building",
             "Bina girişleri, merdivenler ve ortak alanlar için düzenli temizlik.",
             ["Merdiven ve sahanlıklar", "Giriş, asansör ve korkuluklar", "Haftalık veya aylık periyot"]),
        ],
    },
    {
        "id": "isyerleri",
        "title": "İşyerleri",
        "intro": "Ofis, mağaza, kafe ve klinikler için iş akışını bozmayan temizlik.",
        "services": [
            ("ofis-temizligi", "Ofis temizliği", "briefcase",
             "Çalışma alanları, toplantı odaları, mutfak ve ıslak hacimlerin temizliği.",
             ["Mesai dışı saatlerde planlama", "Masa, ekipman çevresi ve zemin", "Düzenli periyotla bakım temizliği"]),
            ("magaza-showroom-temizligi", "Mağaza ve showroom temizliği", "store",
             "Müşterinin gördüğü her yüzeyin parlak ve düzenli kalması için.",
             ["Vitrin ve cam yüzeyler", "Raf, teşhir ve zemin temizliği", "Açılış öncesi veya kapanış sonrası"]),
            ("kafe-restoran-temizligi", "Kafe ve restoran temizliği", "cup",
             "Salon, mutfak, cam ve zemin temizliği tek ekipten.",
             ["Kafe cam temizliği: vitrin ve cephe camları", "Kafe zemin temizliği ve yağ çözme",
              "Salon ve mutfak genel temizliği"]),
            ("eczane-klinik-temizligi", "Eczane ve klinik temizliği", "cross",
             "Hijyenin öncelikli olduğu alanlarda özenli yüzey ve zemin temizliği.",
             ["Bekleme ve muayene alanları", "Sık dokunulan yüzeyler", "Islak hacimler ve zemin"]),
        ],
    },
    {
        "id": "proje-isleri",
        "title": "Proje ve özel işler",
        "intro": "İnşaat sonrası, şantiye, fuar ve deniz araçları gibi özel kapsamlı işler.",
        "services": [
            ("insaat-sonrasi-temizlik", "İnşaat sonrası temizlik", "hardhat",
             "Tadilat ya da inşaat bitiminde alanı oturulabilir ve kullanılabilir hale getirme.",
             ["İnce inşaat tozunun alınması", "Boya, harç ve silikon kalıntıları", "Cam, doğrama ve zemin temizliği"]),
            ("santiye-temizligi", "Şantiye temizliği", "crane",
             "Devam eden projelerde ara temizlik ve teslim öncesi toplu temizlik.",
             ["Moloz ve atık toplama alanlarının düzeni", "Ortak alan ve koridorlar", "Teslim öncesi son temizlik"]),
            ("makineli-zemin-yikama", "Makineli zemin yıkama", "machine",
             "Geniş zeminler için makineyle yıkama ve kurulama.",
             ["Otopark, depo ve atölye zeminleri", "Mağaza ve ofis zeminleri", "Yoğun kir ve leke çözme"]),
            ("fuar-stant-temizligi", "Fuar ve stant temizliği", "booth",
             "Kurulum sonrası, fuar süresince ve söküm sonrasında stant temizliği.",
             ["Açılış öncesi detaylı temizlik", "Fuar günlerinde günlük bakım", "Cam, teşhir ve zemin yüzeyleri"]),
            ("yat-tekne-temizligi", "Yat ve tekne temizliği", "boat",
             "Güverte, kabin ve iç mekânlar için temizlik.",
             ["Güverte ve korkuluklar", "Kabin, mutfak ve banyo", "Sezon açılışı ve kapanışı"]),
            ("konteyner-temizligi", "Konteyner temizliği", "container",
             "Yaşam ve ofis konteynerlerinin iç ve dış temizliği.",
             ["Şantiye ve ofis konteynerleri", "İç yüzey, zemin ve camlar", "Teslim öncesi veya periyodik"]),
        ],
    },
]
ALL_SERVICES = [s for g in GROUPS for s in g["services"]]

EUROPE = ["Arnavutköy", "Avcılar", "Bağcılar", "Bahçelievler", "Bakırköy", "Başakşehir", "Bayrampaşa",
          "Beşiktaş", "Beylikdüzü", "Beyoğlu", "Büyükçekmece", "Çatalca", "Esenler", "Esenyurt",
          "Eyüpsultan", "Fatih", "Gaziosmanpaşa", "Güngören", "Kağıthane", "Küçükçekmece", "Sarıyer",
          "Silivri", "Sultangazi", "Şişli", "Zeytinburnu"]
ANATOLIA = ["Adalar", "Ataşehir", "Beykoz", "Çekmeköy", "Kadıköy", "Kartal", "Maltepe", "Pendik",
            "Sancaktepe", "Sultanbeyli", "Şile", "Tuzla", "Ümraniye", "Üsküdar"]

FAQ = [
    ("Hangi temizlik hizmetlerini veriyorsunuz?",
     "Ev, villa, apartman, ofis, mağaza, kafe, restoran, eczane ve klinik temizliği yapıyoruz. "
     "Bunlara ek olarak inşaat sonrası, şantiye, fuar ve stant, yat ve tekne, konteyner temizliği "
     "ile makineli zemin yıkama hizmeti veriyoruz."),
    ("İstanbul'un hangi ilçelerinde hizmet veriyorsunuz?",
     "Avrupa ve Anadolu yakasındaki 39 ilçenin tamamında hizmet veriyoruz. "
     "Adresinizi paylaştığınızda ekip ve tarih planlamasını buna göre yapıyoruz."),
    ("Teklif ücretli mi?",
     "Hayır, teklif ücretsizdir. Alanı, büyüklüğü ve istediğiniz hizmeti telefonla ya da WhatsApp'tan "
     "anlatmanız yeterli. Gerekirse fotoğraf veya video göndererek teklifi netleştirebilirsiniz."),
    ("Hizmet günü ve kapsamı nasıl belirleniyor?",
     "İhtiyacınızı ve alanın özelliklerini konuştuktan sonra yapılacak işleri birlikte listeliyoruz. "
     "Tarihi ve saati size uygun zamana göre planlıyoruz."),
]

NAV = [
    ("hizmetler.html", "Hizmetler"),
    ("hizmet-bolgeleri.html", "Hizmet bölgeleri"),
    ("referanslar.html", "Referanslar"),
    ("hakkimizda.html", "Hakkımızda"),
    ("iletisim.html", "İletişim"),
]


# ---------------------------------------------------------------- parçalar
def head(title, description, path, extra_schema=None):
    canonical = f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"
    schemas = [BUSINESS_SCHEMA] + (extra_schema or [])
    ld = "\n".join(
        f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0f6e6a">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:site_name" content="OH Temizlik">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/assets/img/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/style.css?v={VERSION}">
{ld}
</head>
<body>
<a class="skip" href="#icerik">İçeriğe geç</a>
"""


def header(active):
    items = "\n".join(
        f'<li><a href="/{href}"{" aria-current=\"page\"" if href == active else ""}>{label}</a></li>'
        for href, label in NAV)
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="OH Temizlik ana sayfa">{LOGO}<span class="brand-name">OH Temizlik<small>İstanbul temizlik hizmetleri</small></span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Menüyü aç">{icon("menu")}</button>
    <nav class="nav" id="site-nav" aria-label="Ana menü">
      <ul>
{items}
      </ul>
    </nav>
    <a class="btn btn-primary header-call" href="tel:{PHONE_TEL}">{icon("phone")}{PHONE_DISPLAY}</a>
  </div>
</header>
<main id="icerik">
"""


def footer():
    svc_links = "\n".join(
        f'<li><a href="/hizmetler.html#{g["id"]}">{g["title"]}</a></li>' for g in GROUPS)
    nav_links = "\n".join(f'<li><a href="/{h}">{l}</a></li>' for h, l in NAV)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <a class="brand" href="/">{LOGO}<span class="brand-name">OH Temizlik<small>Temizliğin ferahlığı, içiniz rahat.</small></span></a>
      <p>İstanbul'un 39 ilçesinde ev, işyeri ve proje temizliği.</p>
    </div>
    <div>
      <h2>Sayfalar</h2>
      <ul>
<li><a href="/">Ana sayfa</a></li>
{nav_links}
      </ul>
    </div>
    <div>
      <h2>İletişim</h2>
      <ul>
        <li><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></li>
        <li><a href="{wa()}" target="_blank" rel="noopener">WhatsApp'tan yazın</a></li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li>Hizmet alanı: İstanbul geneli</li>
      </ul>
      <h2 style="margin-top:1.5rem">Hizmetler</h2>
      <ul>
{svc_links}
      </ul>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span data-year>2026</span> OH Temizlik. Tüm hakları saklıdır.</span>
    <span>Temizliğin ferahlığı, içiniz rahat.</span>
  </div>
</footer>
<div class="mobile-bar" aria-label="Hızlı iletişim">
  <a class="btn btn-primary" href="tel:{PHONE_TEL}">{icon("phone")}Ara</a>
  <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{icon("wa")}WhatsApp</a>
</div>
<script src="/assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def quote_form(heading="Ücretsiz teklif alın", sub="Bilgileri seçin, mesajınız WhatsApp'ta hazır açılsın.",
               fid="teklif", h_tag="h2"):
    svc_opts = "\n".join(
        f'<optgroup label="{g["title"]}">' + "".join(
            f'<option value="{esc(s[1])}">{esc(s[1])}</option>' for s in g["services"]) + "</optgroup>"
        for g in GROUPS)
    district_opts = (
        '<optgroup label="Avrupa Yakası">' + "".join(f'<option>{d}</option>' for d in EUROPE) + "</optgroup>"
        + '<optgroup label="Anadolu Yakası">' + "".join(f'<option>{d}</option>' for d in ANATOLIA) + "</optgroup>")
    return f"""<form class="quote" data-quote id="{fid}" novalidate>
  <{h_tag}>{heading}</{h_tag}>
  <p>{sub}</p>
  <p class="form-error" role="alert"></p>
  <div class="field">
    <label for="{fid}-hizmet">Hizmet</label>
    <select id="{fid}-hizmet" name="hizmet" required>
      <option value="">Seçin</option>
      {svc_opts}
      <option>Diğer</option>
    </select>
  </div>
  <div class="field-row">
    <div class="field">
      <label for="{fid}-ilce">İlçe</label>
      <select id="{fid}-ilce" name="ilce" required>
        <option value="">Seçin</option>
        {district_opts}
      </select>
    </div>
    <div class="field">
      <label for="{fid}-ad">Adınız <span class="opt">(isteğe bağlı)</span></label>
      <input id="{fid}-ad" name="ad" type="text" autocomplete="name">
    </div>
  </div>
  <div class="field">
    <label for="{fid}-not">Alan hakkında kısa bilgi <span class="opt">(isteğe bağlı)</span></label>
    <textarea id="{fid}-not" name="not" placeholder="Örnek: 3+1 daire, yaklaşık 120 m², tadilat sonrası"></textarea>
  </div>
  <button class="btn btn-wa" type="submit">{icon("wa")}WhatsApp'ta gönder</button>
  <p class="form-note">Telefonla konuşmayı tercih ederseniz: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
</form>"""


def crumbs(label):
    return f"""<nav class="crumbs" aria-label="Sayfa konumu"><ol><li><a href="/">Ana sayfa</a></li><li aria-current="page">{label}</li></ol></nav>"""


def page_head(label, h1, lead):
    return f"""<section class="page-head">
  <div class="wrap">
    {crumbs(label)}
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>
"""


def cta_band(title="Temizlik ihtiyacınızı konuşalım",
             text="Alanı ve istediğiniz hizmeti anlatın, ücretsiz teklifinizi hazırlayalım."):
    return f"""<section class="cta-band">
  <div class="wrap">
    <div>
      <h2>{title}</h2>
      <p>{text}</p>
    </div>
    <div class="btn-row">
      <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{icon("wa")}WhatsApp'tan yazın</a>
      <a class="btn btn-light" href="tel:{PHONE_TEL}">{icon("phone")}{PHONE_DISPLAY}</a>
    </div>
  </div>
</section>
"""


def district_links(names):
    return "\n".join(
        f'<li><a href="{wa(f"Merhaba, {d} için temizlik teklifi almak istiyorum.")}" target="_blank" rel="noopener">{d}</a></li>'
        for d in names)


def doc_block():
    return f"""<div class="doc">
  <div class="doc-icon">{icon("doc")}</div>
  <div>
    <h3>Armut hizmet veren belgesi</h3>
    <p>OH Temizlik, Armut platformunda kayıtlı hizmet verendir. Belgeyi açıp inceleyebilirsiniz.</p>
  </div>
  <a class="btn btn-ghost" href="{ARMUT_PDF}" target="_blank" rel="noopener">Belgeyi aç (PDF)</a>
</div>"""


# ---------------------------------------------------------------- şema
BUSINESS_SCHEMA = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": f"{SITE_URL}/#isletme",
    "name": "OH Temizlik",
    "description": "İstanbul genelinde ev, işyeri, inşaat sonrası ve proje temizliği.",
    "url": f"{SITE_URL}/",
    "telephone": PHONE_TEL,
    "email": EMAIL,
    "image": f"{SITE_URL}/assets/img/og-image.png",
    "logo": f"{SITE_URL}/assets/img/apple-touch-icon.png",
    "address": {"@type": "PostalAddress", "addressLocality": "İstanbul", "addressCountry": "TR"},
    "areaServed": [{"@type": "City", "name": "İstanbul"}]
    + [{"@type": "AdministrativeArea", "name": f"{d}, İstanbul"} for d in EUROPE + ANATOLIA],
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Temizlik hizmetleri",
        "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s[1], "description": s[3]}}
            for s in ALL_SERVICES],
    },
}


def faq_schema():
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }


def breadcrumb_schema(label, path):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ana sayfa", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": label, "item": f"{SITE_URL}/{path}"},
        ],
    }


# ---------------------------------------------------------------- sayfalar
def page_index():
    groups = []
    for g in GROUPS:
        items = "\n".join(
            f'<li><a href="/hizmetler.html#{s[0]}">{icon(s[2])}{s[1]}</a></li>' for s in g["services"])
        groups.append(f"""<div class="group">
      <h3>{g["title"]}</h3>
      <p>{g["intro"]}</p>
      <ul class="svc-list">
{items}
      </ul>
    </div>""")
    faq = "\n".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)

    body = f"""<section class="hero">
  <svg class="hero-wipe" viewBox="0 0 1440 720" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <path d="M-120 520 C 260 160, 620 120, 900 300 S 1380 520, 1600 180"/>
  </svg>
  <div class="wrap hero-inner">
    <div>
      <h1>İstanbul'da profesyonel ve güvenilir temizlik</h1>
      <p class="lead">Ev, villa ve apartmanlardan ofis, mağaza, kafe ve kliniklere kadar her alan için titiz, planlı ve zamanında temizlik.</p>
      <div class="btn-row">
        <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{icon("wa")}WhatsApp'tan teklif alın</a>
        <a class="btn btn-ghost" href="tel:{PHONE_TEL}">{icon("phone")}Hemen arayın</a>
      </div>
      <ul class="hero-points">
        <li>{icon("check")}Ücretsiz teklif</li>
        <li>{icon("check")}İstanbul'un 39 ilçesi</li>
        <li>{icon("check")}Armut belgeli hizmet veren</li>
      </ul>
    </div>
    {quote_form()}
  </div>
</section>

<section class="section" aria-labelledby="hizmetler-baslik">
  <div class="wrap">
    <div class="section-head">
      <h2 id="hizmetler-baslik">Her alan için temizlik</h2>
      <p>Evinizden işyerinize, inşaat sonrasından fuar standına kadar 13 farklı hizmet.</p>
    </div>
    <div class="groups">
{chr(10).join(groups)}
    </div>
    <p style="margin-top:2rem"><a class="btn btn-ghost" href="/hizmetler.html">Tüm hizmetlerin ayrıntıları</a></p>
  </div>
</section>

<section class="section section-alt" aria-labelledby="surec-baslik">
  <div class="wrap">
    <div class="section-head">
      <h2 id="surec-baslik">Teklif almak üç adım</h2>
      <p>Telefon ya da WhatsApp üzerinden birkaç dakikada başlar.</p>
    </div>
    <ol class="steps">
      <li><h3>İhtiyacınızı anlatın</h3><p>Temizlenecek alanı, büyüklüğünü ve istediğiniz hizmeti bize iletin. Fotoğraf göndermek teklifi hızlandırır.</p></li>
      <li><h3>Teklifi netleştirelim</h3><p>İşin kapsamını birlikte listeleyelim, ücretsiz teklifimizi size iletelim.</p></li>
      <li><h3>Günü planlayalım</h3><p>Size uygun tarih ve saatte ekibimiz gelip işi teslim etsin.</p></li>
    </ol>
  </div>
</section>

<section class="section" aria-labelledby="bolge-baslik">
  <div class="wrap">
    <div class="section-head">
      <h2 id="bolge-baslik">İstanbul'un iki yakasında</h2>
      <p>İlçenize dokunun, teklif mesajınız WhatsApp'ta hazır açılsın.</p>
    </div>
    <div class="areas">
      <div class="area">
        <h3>Avrupa Yakası <span>{len(EUROPE)} ilçe</span></h3>
        <ul class="district-list">
{district_links(EUROPE)}
        </ul>
      </div>
      <div class="area">
        <h3>Anadolu Yakası <span>{len(ANATOLIA)} ilçe</span></h3>
        <ul class="district-list">
{district_links(ANATOLIA)}
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt" aria-labelledby="sss-baslik">
  <div class="wrap">
    <div class="section-head">
      <h2 id="sss-baslik">Sık sorulan sorular</h2>
    </div>
    <div class="faq">
{faq}
    </div>
    <div style="margin-top:2.5rem">
{doc_block()}
    </div>
  </div>
</section>
{cta_band()}"""
    return (head("OH Temizlik | İstanbul'da Profesyonel Temizlik Hizmeti",
                 "İstanbul'un 39 ilçesinde ev, villa, apartman, ofis, kafe, inşaat sonrası ve proje temizliği. "
                 "WhatsApp veya telefonla ücretsiz teklif alın.", "", [faq_schema()])
            + header("") + body + footer())


def page_services():
    sections = []
    for g in GROUPS:
        rows = []
        for sid, name, ic, desc, bullets in g["services"]:
            lis = "".join(f"<li>{b}</li>" for b in bullets)
            rows.append(f"""<article class="svc" id="{sid}">
      <div class="svc-icon">{ic and icon(ic)}</div>
      <div>
        <h3>{name}</h3>
        <p>{desc}</p>
        <ul>{lis}</ul>
      </div>
      <a class="btn btn-wa" href="{wa(f"Merhaba, {name.lower()} için teklif almak istiyorum.")}" target="_blank" rel="noopener">{icon("wa")}Teklif alın</a>
    </article>""")
        sections.append(f"""<section class="svc-section" id="{g["id"]}" aria-labelledby="{g["id"]}-baslik">
    <h2 id="{g["id"]}-baslik">{g["title"]}</h2>
    <p class="muted">{g["intro"]}</p>
{chr(10).join(rows)}
  </section>""")
    # eski bağlantılar için uyumluluk (#ofis-temizligi zaten var)
    body = page_head("Hizmetler", "Temizlik hizmetlerimiz",
                     "Yaşam alanları, işyerleri ve özel projeler için 13 hizmet. Her biri için ücretsiz teklif alabilirsiniz.") + f"""
<div class="section">
  <div class="wrap">
{chr(10).join(sections)}
  </div>
</div>
{cta_band("Aradığınız hizmeti bulamadınız mı?", "Listede olmayan işler için de bize yazın, uygun çözümü birlikte bulalım.")}"""
    return (head("Temizlik Hizmetleri | OH Temizlik İstanbul",
                 "Ev, villa, apartman, ofis, mağaza, kafe, klinik, inşaat sonrası, şantiye, fuar, yat ve konteyner "
                 "temizliği. İstanbul geneli, ücretsiz teklif.", "hizmetler.html",
                 [breadcrumb_schema("Hizmetler", "hizmetler.html")])
            + header("hizmetler.html") + body + footer())


def page_areas():
    body = page_head("Hizmet bölgeleri", "İstanbul'un tüm ilçelerinde hizmet",
                     f"Avrupa Yakası'nda {len(EUROPE)}, Anadolu Yakası'nda {len(ANATOLIA)} ilçe olmak üzere İstanbul'un "
                     "39 ilçesinin tamamına hizmet veriyoruz.") + f"""
<section class="section" aria-labelledby="ilceler-baslik">
  <div class="wrap">
    <div class="section-head">
      <h2 id="ilceler-baslik">İlçenizi seçin</h2>
      <p>İlçenize dokunduğunuzda teklif mesajınız WhatsApp'ta hazır açılır.</p>
    </div>
    <div class="areas">
      <div class="area">
        <h3>Avrupa Yakası <span>{len(EUROPE)} ilçe</span></h3>
        <ul class="district-list">
{district_links(EUROPE)}
        </ul>
      </div>
      <div class="area">
        <h3>Anadolu Yakası <span>{len(ANATOLIA)} ilçe</span></h3>
        <ul class="district-list">
{district_links(ANATOLIA)}
        </ul>
      </div>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap cols">
    <div>
      <h2>Planlama nasıl yapılıyor?</h2>
      <p>Ekip ve ekipman planlamasını adresinize, alanın büyüklüğüne ve hizmet türüne göre yapıyoruz. Teklif aşamasında ilçenizi ve tercih ettiğiniz tarihi belirtmeniz yeterli.</p>
      <p>Adalar gibi ulaşımı farklı planlanan bölgeler için tarih ve saat seçeneklerini ayrıca konuşuyoruz.</p>
    </div>
    {quote_form("İlçeniz için teklif alın", "Hizmeti ve ilçeyi seçin, mesajınız WhatsApp'ta hazır açılsın.", "teklif-bolge")}
  </div>
</section>
{cta_band()}"""
    return (head("Hizmet Bölgeleri | İstanbul'un 39 İlçesinde Temizlik | OH Temizlik",
                 "Kadıköy, Beşiktaş, Şişli, Üsküdar, Ataşehir, Bakırköy ve İstanbul'un diğer tüm ilçelerinde "
                 "temizlik hizmeti. Ücretsiz teklif alın.", "hizmet-bolgeleri.html",
                 [breadcrumb_schema("Hizmet bölgeleri", "hizmet-bolgeleri.html")])
            + header("hizmet-bolgeleri.html") + body + footer())


def page_refs():
    sectors = [
        ("home", "Ev, villa ve apartmanlar"),
        ("briefcase", "Ofisler ve işyerleri"),
        ("cup", "Kafe ve restoranlar"),
        ("cross", "Eczane ve klinikler"),
        ("hardhat", "İnşaat ve tadilat projeleri"),
        ("booth", "Fuar ve stant alanları"),
    ]
    items = "\n".join(f'<li>{icon(i)}<span>{t}</span></li>' for i, t in sectors)
    body = page_head("Referanslar", "Belgelerimiz ve hizmet verdiğimiz alanlar",
                     "OH Temizlik, Armut platformunda kayıtlı hizmet verendir. Belgemizi aşağıdan inceleyebilirsiniz.") + f"""
<section class="section">
  <div class="wrap">
{doc_block()}
  </div>
</section>
<section class="section section-alt" aria-labelledby="alanlar-baslik">
  <div class="wrap cols">
    <div>
      <h2 id="alanlar-baslik">Hizmet verdiğimiz alanlar</h2>
      <p>Yaşam alanlarından işyerlerine ve proje temizliğine kadar farklı ölçekte işler üstleniyoruz. Benzer bir iş için örnek ve ayrıntı isterseniz bize yazın.</p>
      <a class="btn btn-wa" href="{wa("Merhaba, yaptığınız işlerle ilgili bilgi almak istiyorum.")}" target="_blank" rel="noopener">{icon("wa")}Örnek işleri sorun</a>
    </div>
    <ul class="check-list">
{items}
    </ul>
  </div>
</section>
{cta_band()}"""
    return (head("Referanslar | OH Temizlik İstanbul",
                 "OH Temizlik'in Armut hizmet veren belgesi ve hizmet verdiği alanlar.",
                 "referanslar.html", [breadcrumb_schema("Referanslar", "referanslar.html")])
            + header("referanslar.html") + body + footer())


def page_about():
    principles = [
        ("İşi önce birlikte tanımlarız", "Hangi alanların, hangi yüzeylerin temizleneceğini teklif aşamasında netleştiririz. Sürprizle karşılaşmazsınız."),
        ("Size uyan zamanda çalışırız", "Evlerde size uygun gün ve saatte, işyerlerinde iş akışını bozmayacak şekilde mesai dışında planlarız."),
        ("Alana uygun ekip ve ekipman", "Ev temizliğinden makineli zemin yıkamaya kadar her iş için uygun malzemeyi getiririz."),
        ("Ulaşılabilir kalırız", "Teklif, planlama ve hizmet günü boyunca telefon ve WhatsApp'tan bize doğrudan ulaşırsınız."),
    ]
    items = "\n".join(f'<li>{icon("check")}<div><strong>{t}</strong><br><span class="muted">{d}</span></div></li>'
                      for t, d in principles)
    body = page_head("Hakkımızda", "Temizlikte özenli ve anlaşılır hizmet",
                     "OH Temizlik, İstanbul genelinde ev, işyeri ve proje temizliği yapan bir temizlik firmasıdır.") + f"""
<section class="section">
  <div class="wrap cols">
    <div>
      <h2>Ne yapıyoruz?</h2>
      <p>Ev, villa ve apartmanlardan ofis, mağaza, kafe, restoran, eczane ve kliniklere kadar farklı alanlarda temizlik hizmeti veriyoruz. İnşaat sonrası, şantiye, fuar ve stant, yat ve tekne, konteyner temizliği ile makineli zemin yıkama da hizmetlerimiz arasında.</p>
      <p>Her işe ihtiyacı dinleyerek başlıyoruz. Alanın büyüklüğünü, kullanım şeklini ve beklentinizi öğrenip kapsamı buna göre planlıyoruz.</p>
      <p><a href="/hizmetler.html">Tüm hizmetlerimizi inceleyin</a></p>
    </div>
    <div>
      <h2>Nasıl çalışıyoruz?</h2>
      <ul class="check-list">
{items}
      </ul>
    </div>
  </div>
</section>
<section class="section section-alt">
  <div class="wrap">
{doc_block()}
  </div>
</section>
{cta_band()}"""
    return (head("Hakkımızda | OH Temizlik İstanbul",
                 "OH Temizlik'in çalışma şekli: ihtiyacı birlikte tanımlama, size uygun planlama ve İstanbul genelinde özenli temizlik.",
                 "hakkimizda.html", [breadcrumb_schema("Hakkımızda", "hakkimizda.html")])
            + header("hakkimizda.html") + body + footer())


def page_contact():
    body = page_head("İletişim", "Temizlik ihtiyacınız için bize ulaşın",
                     "Telefon, WhatsApp veya e-posta ile yazın. Teklif ücretsizdir.") + f"""
<section class="section">
  <div class="wrap cols">
    <div>
      <h2>İletişim bilgileri</h2>
      <ul class="contact-list">
        <li><a href="tel:{PHONE_TEL}"><span class="ci">{icon("phone")}</span><div><span>Telefon</span><strong>{PHONE_DISPLAY}</strong></div></a></li>
        <li><a href="{wa()}" target="_blank" rel="noopener"><span class="ci">{icon("wa")}</span><div><span>WhatsApp</span><strong>Mesaj gönderin</strong></div></a></li>
        <li><a href="mailto:{EMAIL}"><span class="ci">{icon("mail")}</span><div><span>E-posta</span><strong>{EMAIL}</strong></div></a></li>
        <li><div><span class="ci">{icon("map")}</span><div><span>Hizmet alanı</span><strong>İstanbul'un 39 ilçesi</strong></div></div></li>
      </ul>
      <p style="margin-top:1.5rem" class="muted">Teklifi hızlandırmak için alanın fotoğraflarını veya kısa bir videosunu WhatsApp'tan gönderebilirsiniz.</p>
    </div>
    {quote_form("Teklif formu", "Bilgileri seçin, mesajınız WhatsApp'ta hazır açılsın.", "teklif-iletisim")}
  </div>
</section>
"""
    return (head("İletişim ve Ücretsiz Teklif | OH Temizlik",
                 f"OH Temizlik'e telefon ({PHONE_DISPLAY}), WhatsApp veya {EMAIL} adresinden ulaşın. "
                 "İstanbul genelinde ücretsiz teklif.", "iletisim.html",
                 [breadcrumb_schema("İletişim", "iletisim.html")])
            + header("iletisim.html") + body + footer())


def page_404():
    body = f"""<section class="section notfound">
  <div class="wrap">
    <h1>Bu sayfa bulunamadı</h1>
    <p class="lead">Aradığınız sayfa taşınmış veya kaldırılmış olabilir. Ana sayfadan devam edebilir ya da bize doğrudan yazabilirsiniz.</p>
    <div class="btn-row">
      <a class="btn btn-primary" href="/">Ana sayfaya dönün</a>
      <a class="btn btn-wa" href="{wa()}" target="_blank" rel="noopener">{icon("wa")}WhatsApp'tan yazın</a>
    </div>
  </div>
</section>
"""
    h = head("Sayfa bulunamadı | OH Temizlik", "Aradığınız sayfa bulunamadı.", "404.html")
    h = h.replace("<head>\n", '<head>\n<meta name="robots" content="noindex">\n', 1)
    return h + header("") + body + footer()


PAGES = {
    "index.html": page_index,
    "hizmetler.html": page_services,
    "hizmet-bolgeleri.html": page_areas,
    "referanslar.html": page_refs,
    "hakkimizda.html": page_about,
    "iletisim.html": page_contact,
    "404.html": page_404,
}


def main():
    for name, fn in PAGES.items():
        (ROOT / name).write_text(fn(), encoding="utf-8")
    urls = [""] + [p for p in PAGES if p not in ("index.html", "404.html")]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{SITE_URL}/{u}</loc></url>" for u in urls]
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "CNAME").write_text("ohtemizlik.com\n", encoding="utf-8")
    (ROOT / "assets/img/favicon.svg").write_text(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'), encoding="utf-8")
    print("Sayfalar üretildi:", ", ".join(PAGES))


if __name__ == "__main__":
    main()
