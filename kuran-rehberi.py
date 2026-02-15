import customtkinter as ctk
import json
import random
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap


class KuranRehberi(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kur'an-ı Kerim Dijital Rehber v9.0")
        self.geometry("1200x850")

        self.veriyi_yukle()
        self.favori_dosyasi = "favorilerim.txt"

        # --- Veri Sözlükleri ---
        self.kategoriler = {
            "İman & Tevhid": ["iman", "allah", "tek", "ortak", "tevhid"],
            "Güzel Ahlak": ["ahlak", "iyilik", "anne", "baba", "emanet"],
            "Zorluk ve Sabır": ["sabır", "zorluk", "kolaylık", "imtihan"],
            "İbadet ve Dua": ["namaz", "dua", "hac", "oruç", "zikir"]
        }

        self.ruh_halleri = {
            "Hüzünlü": ["üzülme", "gevşeme", "ferah", "göğüs", "müjde"],
            "Yalnız": ["yakın", "şah damarı", "beraber", "dost", "yardım"],
            "Şükür Dolu": ["nimet", "bolluk", "sevinç", "hamd", "şükür"]
        }

        # --- Arayüz Yapısı ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar_frame, text="REHBER v9.0", font=("Ubuntu", 24, "bold")).pack(pady=30)

        self.tabs = ["Keşfet", "Ruh Hali", "Arama", "Kütüphane", "Favoriler"]
        for t in self.tabs:
            ctk.CTkButton(self.sidebar_frame, text=t, command=lambda x=t: self.tab_degistir(x)).pack(pady=8, padx=20)

        self.tab_panel = ctk.CTkTabview(self)
        self.tab_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        for t in self.tabs: self.tab_panel.add(t)

        self.setup_tabs()

    def setup_tabs(self):
        self.setup_content_tab("Keşfet", self.kategoriler, self.konulu_ayet_getir)
        self.setup_content_tab("Ruh Hali", self.ruh_halleri, self.mod_ayeti_getir)
        self.setup_arama_tab()
        self.setup_kutuphane_tab()
        self.setup_favori_tab()

    # --- KÜTÜPHANE (ETKİLEŞİMLİ) ---
    def setup_kutuphane_tab(self):
        tab = self.tab_panel.tab("Kütüphane")

        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(header_frame, text="Sıra", width=50).pack(side="left")
        ctk.CTkLabel(header_frame, text="Sure İsmi (Okumak için tıklayın)", width=200).pack(side="left", padx=20)
        ctk.CTkLabel(header_frame, text="Ayet Sayısı", width=100).pack(side="left")

        # Kaydırılabilir liste
        self.scroll_fihrist = ctk.CTkScrollableFrame(tab)
        self.scroll_fihrist.pack(expand=True, fill="both", padx=10, pady=10)

        for i, sure in enumerate(self.data['sures'], 1):
            s_frame = ctk.CTkFrame(self.scroll_fihrist, fg_color="transparent")
            s_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(s_frame, text=str(i), width=50).pack(side="left")

            # Sure ismi bir butondur, basınca detay açar
            btn_sure = ctk.CTkButton(s_frame, text=sure['name'].strip(), width=200,
                                     fg_color="transparent", text_color=("black", "white"),
                                     anchor="w", hover_color=("gray80", "gray25"),
                                     command=lambda s=sure: self.sure_detay_ac(s))
            btn_sure.pack(side="left", padx=20)

            ctk.CTkLabel(s_frame, text=str(len(sure['ayetler'])), width=100).pack(side="left")

    def sure_detay_ac(self, sure_verisi):
        detay_pencere = ctk.CTkToplevel(self)
        detay_pencere.title(f"{sure_verisi['name'].strip()} Suresi")
        detay_pencere.geometry("700x600")
        detay_pencere.attributes("-topmost", True)

        txt_full = ctk.CTkTextbox(detay_pencere, font=("FreeSerif", 18), wrap="word")
        txt_full.pack(expand=True, fill="both", padx=20, pady=20)

        icerik = f"--- {sure_verisi['name'].strip().upper()} SURESİ ---\n\n"
        for ayet in sure_verisi['ayetler']:
            icerik += f"[{ayet[0]}] {ayet[1]}\n\n"

        txt_full.insert("0.0", icerik)
        txt_full.configure(state="disabled")

    # --- ARAMA SEKMESİ ---
    def setup_arama_tab(self):
        tab = self.tab_panel.tab("Arama")
        search_frame = ctk.CTkFrame(tab, fg_color="transparent")
        search_frame.pack(pady=15, fill="x", padx=20)
        self.entry_arama = ctk.CTkEntry(search_frame, placeholder_text="Arama kelimesi...", width=400)
        self.entry_arama.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="🔍 Ara", command=self.detayli_arama).pack(side="left")
        self.txt_arama_sonuc = ctk.CTkTextbox(tab, font=("FreeSerif", 18), wrap="word")
        self.txt_arama_sonuc.pack(expand=True, fill="both", padx=15, pady=10)

    def detayli_arama(self):
        anahtar = self.entry_arama.get().lower().strip()
        if len(anahtar) < 3: return
        sonuclar = []
        for sure in self.data['sures']:
            for ayet in sure['ayetler']:
                if anahtar in ayet[1].lower():
                    sonuclar.append(f"📖 {sure['name'].strip()} {ayet[0]}: {ayet[1]}")
        self.txt_arama_sonuc.delete("0.0", "end")
        self.txt_arama_sonuc.insert("0.0", f"{len(sonuclar)} sonuç bulundu:\n\n" + "\n\n".join(
            sonuclar) if sonuclar else "Sonuç yok.")

    # --- AKILLI FAVORİ SİSTEMİ ---
    def favori_ekle(self, source):
        icerik = source.get("0.0", "end").strip()
        if not icerik or "📍" not in icerik: return
        mevcut = ""
        if os.path.exists(self.favori_dosyasi):
            with open(self.favori_dosyasi, "r", encoding="utf-8") as f: mevcut = f.read()
        if icerik in mevcut:
            os.system('notify-send "Uyarı" "Bu kayıt zaten favorilerde mevcut."')
            return
        with open(self.favori_dosyasi, "a", encoding="utf-8") as f:
            f.write(icerik + "\n" + "=" * 40 + "\n\n")
        os.system('notify-send "Başarılı" "Favorilere kaydedildi."')

    # --- STANDART FONKSİYONLAR ---
    def setup_content_tab(self, tab_name, sozluk, komut):
        tab = self.tab_panel.tab(tab_name)
        menu = ctk.CTkOptionMenu(tab, values=list(sozluk.keys()), width=350)
        menu.pack(pady=15)
        if tab_name == "Keşfet":
            self.konu_menu = menu
        else:
            self.mod_menu = menu
        ctk.CTkButton(tab, text="Ayet Getir", command=komut).pack(pady=5)
        display = ctk.CTkTextbox(tab, font=("FreeSerif", 21), wrap="word")
        display.pack(expand=True, fill="both", padx=15, pady=15)
        if tab_name == "Keşfet":
            self.txt_kesfet_display = display
        else:
            self.txt_mod_display = display
        f = ctk.CTkFrame(tab, fg_color="transparent");
        f.pack(pady=10)
        ctk.CTkButton(f, text="⭐ Favori", command=lambda: self.favori_ekle(display), fg_color="darkgoldenrod").pack(
            side="left", padx=5)
        ctk.CTkButton(f, text="🖼️ Görsel", command=lambda: self.resim_yap(display), fg_color="purple").pack(side="left",
                                                                                                            padx=5)

    def setup_favori_tab(self):
        tab = self.tab_panel.tab("Favoriler")
        self.txt_fav_display = ctk.CTkTextbox(tab, font=("FreeSerif", 16), wrap="word")
        self.txt_fav_display.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkButton(tab, text="🗑️ Temizle", command=self.favori_temizle, fg_color="indianred").pack(pady=5)

    def resim_yap(self, source):
        txt = source.get("0.0", "end").strip()
        if "📍" not in txt: return
        img = Image.new('RGB', (1080, 1080), color='#121212')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSerif.ttf", 45)
        except:
            font = ImageFont.load_default()
        draw.multiline_text((540, 540), textwrap.fill(txt, width=45), font=font, fill="#E0E0E0", anchor="mm",
                            align="center")
        img = ImageOps.expand(img, border=15, fill='#3498db')
        fname = f"ayet_{random.randint(1000, 9999)}.png"
        img.save(fname);
        os.system(f'notify-send "Görsel kaydedildi: {fname}"')

    def veriyi_yukle(self):
        with open('Diyanet Vakfı.json', 'r', encoding='utf-8') as f: self.data = json.load(f)

    def tab_degistir(self, isim):
        self.tab_panel.set(isim)
        if isim == "Favoriler": self.favorileri_yansit()

    def ayet_bul(self, anahtar_listesi):
        havuz = []
        for s in self.data['sures']:
            for a in s['ayetler']:
                if any(k in a[1].lower() for k in anahtar_listesi): havuz.append((s['name'], a[0], a[1]))
        return random.choice(havuz) if havuz else None

    def konulu_ayet_getir(self):
        res = self.ayet_bul(self.kategoriler[self.konu_menu.get()])
        self.yazdir(self.txt_kesfet_display, res, self.konu_menu.get())

    def mod_ayeti_getir(self):
        res = self.ayet_bul(self.ruh_halleri[self.mod_menu.get()])
        self.yazdir(self.txt_mod_display, res, self.mod_menu.get())

    def yazdir(self, target, res, baslik):
        target.delete("0.0", "end")
        if res: target.insert("0.0", f"📍 {baslik.upper()}\n\n\"{res[2]}\"\n\n📖 {res[0].strip()} Suresi, {res[1]}. Ayet")

    def favorileri_yansit(self):
        self.txt_fav_display.delete("0.0", "end")
        if os.path.exists(self.favori_dosyasi):
            with open(self.favori_dosyasi, "r", encoding="utf-8") as f: self.txt_fav_display.insert("0.0", f.read())

    def favori_temizle(self):
        if os.path.exists(self.favori_dosyasi): os.remove(self.favori_dosyasi); self.favorileri_yansit()


if __name__ == "__main__":
    app = KuranRehberi()
    app.mainloop()