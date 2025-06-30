import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
from fpdf import FPDF
import os
import urllib.request

RENK_ARKAPLAN = "#f0f4f8"
RENK_BASLIK = "#2d6a4f"
RENK_BUTON = "#40916c"
RENK_BUTON_YAZI = "#fff"
RENK_ENTRY = "#e9ecef"
RENK_TABLO_BASLIK = "#b7e4c7"
RENK_TABLO = "#fff"

class LastikUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Lastik Parçalama Takip Uygulaması")
        self.root.configure(bg=RENK_ARKAPLAN)
        self.veriler = []
        self.gonderildi_durum = []  # Her satır için gönderildi mi?
        # Varsayılan birimler
        self.birimler = {
            "Lastik": "kg",
            "Tel": "kg",
            "Tekstil": "kg",
            "Kauçuk": "kg"
        }
        self.setup_ui()

    def setup_ui(self):
        # Başlık
        baslik = tk.Label(self.root, text="Lastik Parçalama Takip Uygulaması", font=("Arial", 18, "bold"), bg=RENK_BASLIK, fg="white", pady=10)
        baslik.pack(fill="x", pady=(0, 10))

        # Ayarlar butonu
        ayar_btn = tk.Button(self.root, text="Ayarlar (Birim Seç)", command=self.ayarlar_penceresi, bg="#577590", fg="white", font=("Arial", 11, "bold"), relief="raised", bd=2, activebackground="#43aa8b", activeforeground="white", cursor="hand2")
        ayar_btn.pack(pady=(0, 10))

        # Giriş alanı (sadece Lastik)
        frame = tk.Frame(self.root, bg=RENK_ARKAPLAN)
        frame.pack(padx=20, pady=10)
        label_opts = {"bg": RENK_ARKAPLAN, "font": ("Arial", 12)}
        entry_opts = {"bg": RENK_ENTRY, "font": ("Arial", 12), "relief": "solid", "bd": 1, "width": 18}
        tk.Label(frame, text="Lastik (kg):", **label_opts).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.lastik_entry = tk.Entry(frame, **entry_opts)
        self.lastik_entry.grid(row=0, column=1, pady=5, padx=5)
        ekle_btn = tk.Button(frame, text="Ekle", command=self.veri_ekle, bg=RENK_BUTON, fg=RENK_BUTON_YAZI, font=("Arial", 12, "bold"), relief="raised", bd=2, activebackground="#52b788", activeforeground="white", cursor="hand2")
        ekle_btn.grid(row=1, column=0, columnspan=2, pady=10)
        ekle_btn.grid_configure(ipadx=20, ipady=5)

        # Tablo
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", background=RENK_TABLO_BASLIK, foreground="#222", font=("Arial", 12, "bold"))
        style.configure("Treeview", background=RENK_TABLO, fieldbackground=RENK_TABLO, font=("Arial", 11), rowheight=28)
        style.map("Treeview", background=[('selected', '#95d5b2')])
        tablo_frame = tk.Frame(self.root, bg=RENK_ARKAPLAN)
        tablo_frame.pack(padx=20, pady=10, fill="x")
        self.tablo = ttk.Treeview(tablo_frame, columns=("lastik", "tel", "tekstil", "kaucuk"), show="headings", height=8)
        self.tablo.heading("lastik", text="Lastik")
        self.tablo.heading("tel", text="Tel")
        self.tablo.heading("tekstil", text="Tekstil")
        self.tablo.heading("kaucuk", text="Kauçuk")
        self.tablo.column("lastik", width=120, anchor="center")
        self.tablo.column("tel", width=120, anchor="center")
        self.tablo.column("tekstil", width=120, anchor="center")
        self.tablo.column("kaucuk", width=120, anchor="center")
        self.tablo.pack(side="left", fill="x", expand=True)
        scrollbar = ttk.Scrollbar(tablo_frame, orient="vertical", command=self.tablo.yview)
        self.tablo.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tablo.bind("<<TreeviewSelect>>", self.satir_secildi)

        # Sil, Düzenle ve Gönderildi butonları
        btn_edit_frame = tk.Frame(self.root, bg=RENK_ARKAPLAN)
        btn_edit_frame.pack(pady=5)
        self.duzenle_btn = tk.Button(btn_edit_frame, text="Düzenle", command=self.satir_duzenle, state="disabled", bg="#f9c74f", fg="#222", font=("Arial", 12, "bold"), relief="raised", bd=2, activebackground="#f9844a", activeforeground="white", cursor="hand2")
        self.duzenle_btn.pack(side="left", padx=10)
        self.sil_btn = tk.Button(btn_edit_frame, text="Sil", command=self.satir_sil, state="disabled", bg="#d90429", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=2, activebackground="#ef233c", activeforeground="white", cursor="hand2")
        self.sil_btn.pack(side="left", padx=10)
        self.gonderildi_btn = tk.Button(btn_edit_frame, text="Gönderildi / Geri Al", command=self.satir_gonderildi_toggle, state="disabled", bg="#40916c", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=2, activebackground="#52b788", activeforeground="white", cursor="hand2")
        self.gonderildi_btn.pack(side="left", padx=10)

        # Dışa Aktarma Butonları
        btn_frame = tk.Frame(self.root, bg=RENK_ARKAPLAN)
        btn_frame.pack(pady=10)
        btn_opts = {"bg": RENK_BUTON, "fg": RENK_BUTON_YAZI, "font": ("Arial", 12, "bold"), "relief": "raised", "bd": 2, "activebackground": "#52b788", "activeforeground": "white", "cursor": "hand2"}
        excel_btn = tk.Button(btn_frame, text="Excel'e Aktar", command=self.excel_aktar, **btn_opts)
        excel_btn.pack(side="left", padx=10)
        excel_btn.pack_configure(ipadx=20, ipady=5)
        pdf_btn = tk.Button(btn_frame, text="PDF'e Aktar", command=self.pdf_aktar, **btn_opts)
        pdf_btn.pack(side="left", padx=10)
        pdf_btn.pack_configure(ipadx=20, ipady=5)
        secilen_excel_btn = tk.Button(btn_frame, text="Seçilenleri Excel'e Aktar", command=self.secilenleri_excel_aktar, **btn_opts)
        secilen_excel_btn.pack(side="left", padx=10)
        secilen_excel_btn.pack_configure(ipadx=20, ipady=5)
        secilen_pdf_btn = tk.Button(btn_frame, text="Seçilenleri PDF'e Aktar", command=self.secilenleri_pdf_aktar, **btn_opts)
        secilen_pdf_btn.pack(side="left", padx=10)
        secilen_pdf_btn.pack_configure(ipadx=20, ipady=5)

    def ayarlar_penceresi(self):
        pencere = tk.Toplevel(self.root)
        pencere.title("Birim Ayarları")
        pencere.grab_set()
        pencere.resizable(False, False)
        frame = tk.Frame(pencere, padx=20, pady=20)
        frame.pack()
        birim_ops = ["kg", "gr", "ton", "mg"]
        entries = {}
        for i, isim in enumerate(["Lastik", "Tel", "Tekstil", "Kauçuk"]):
            tk.Label(frame, text=f"{isim} birimi:", font=("Arial", 12)).grid(row=i, column=0, sticky="e", pady=5, padx=5)
            var = tk.StringVar(value=self.birimler[isim])
            entries[isim] = var
            ttk.Combobox(frame, textvariable=var, values=birim_ops, state="readonly", width=7, font=("Arial", 12)).grid(row=i, column=1, pady=5, padx=5)
        def kaydet():
            for isim in entries:
                self.birimler[isim] = entries[isim].get()
            pencere.destroy()
        tk.Button(frame, text="Kaydet", command=kaydet, bg="#40916c", fg="white", font=("Arial", 12, "bold"), relief="raised", bd=2, activebackground="#52b788", activeforeground="white", cursor="hand2").grid(row=4, column=0, columnspan=2, pady=15, ipadx=20, ipady=5)

    def veri_ekle(self):
        lastik = self.lastik_entry.get()
        if not lastik:
            messagebox.showwarning("Uyarı", "Lütfen lastik miktarını girin.")
            return
        tel = simpledialog.askstring("Girdi", "Tel miktarı:", parent=self.root)
        if tel is None:
            return
        tekstil = simpledialog.askstring("Girdi", "Tekstil miktarı:", parent=self.root)
        if tekstil is None:
            return
        kaucuk = simpledialog.askstring("Girdi", "Kauçuk miktarı:", parent=self.root)
        if kaucuk is None:
            return
        yeni_veri = {
            "Lastik": f"{lastik} {self.birimler['Lastik']}",
            "Tel": f"{tel} {self.birimler['Tel']}",
            "Tekstil": f"{tekstil} {self.birimler['Tekstil']}",
            "Kauçuk": f"{kaucuk} {self.birimler['Kauçuk']}"
        }
        self.veriler.append(yeni_veri)
        item_id = self.tablo.insert("", "end", values=(yeni_veri["Lastik"], yeni_veri["Tel"], yeni_veri["Tekstil"], yeni_veri["Kauçuk"]))
        self.gonderildi_durum.append(False)
        self.tablo.item(item_id, tags=("gonderilmedi",))
        self.tablo.tag_configure("gonderilmedi", foreground="#d90429")
        self.tablo.tag_configure("gonderildi", foreground="#40916c")
        self.lastik_entry.delete(0, tk.END)

    def satir_secildi(self, event):
        secili = self.tablo.selection()
        if secili:
            self.duzenle_btn.config(state="normal")
            self.sil_btn.config(state="normal")
            self.gonderildi_btn.config(state="normal")
        else:
            self.duzenle_btn.config(state="disabled")
            self.sil_btn.config(state="disabled")
            self.gonderildi_btn.config(state="disabled")

    def satir_gonderildi_toggle(self):
        secili = self.tablo.selection()
        for item in secili:
            idx = self.tablo.index(item)
            if self.gonderildi_durum[idx]:
                # Geri al
                self.gonderildi_durum[idx] = False
                self.tablo.item(item, tags=("gonderilmedi",))
            else:
                # Gönderildi
                self.gonderildi_durum[idx] = True
                self.tablo.item(item, tags=("gonderildi",))

    def satir_duzenle(self):
        secili = self.tablo.selection()
        if not secili:
            return
        idx = self.tablo.index(secili[0])
        veri = self.veriler[idx]
        def ayir(deger_str, birim):
            parcalar = deger_str.split()
            if len(parcalar) == 2:
                return parcalar[0], parcalar[1]
            elif len(parcalar) == 1:
                return parcalar[0], birim
            else:
                return "", birim
        tel_deger, _ = ayir(veri["Tel"], self.birimler['Tel'])
        tekstil_deger, _ = ayir(veri["Tekstil"], self.birimler['Tekstil'])
        kaucuk_deger, _ = ayir(veri["Kauçuk"], self.birimler['Kauçuk'])
        tel = simpledialog.askstring("Düzenle", "Tel miktarı:", initialvalue=tel_deger)
        if tel is None:
            return
        tekstil = simpledialog.askstring("Düzenle", "Tekstil miktarı:", initialvalue=tekstil_deger)
        if tekstil is None:
            return
        kaucuk = simpledialog.askstring("Düzenle", "Kauçuk miktarı:", initialvalue=kaucuk_deger)
        if kaucuk is None:
            return
        self.veriler[idx]["Tel"] = f"{tel} {self.birimler['Tel']}"
        self.veriler[idx]["Tekstil"] = f"{tekstil} {self.birimler['Tekstil']}"
        self.veriler[idx]["Kauçuk"] = f"{kaucuk} {self.birimler['Kauçuk']}"
        self.tablo.item(secili[0], values=(veri["Lastik"], veri["Tel"], veri["Tekstil"], veri["Kauçuk"]))
        self.gonderildi_durum[idx] = False
        self.tablo.item(secili[0], tags=("gonderilmedi",))

    def satir_sil(self):
        secili = self.tablo.selection()
        if not secili:
            return
        idx = self.tablo.index(secili[0])
        self.tablo.delete(secili[0])
        del self.veriler[idx]
        del self.gonderildi_durum[idx]
        self.duzenle_btn.config(state="disabled")
        self.sil_btn.config(state="disabled")
        self.gonderildi_btn.config(state="disabled")

    def excel_aktar(self):
        if not self.veriler:
            messagebox.showinfo("Bilgi", "Aktarılacak veri yok.")
            return
        secili = self.tablo.selection()
        if secili:
            secili_indeksler = [self.tablo.index(item) for item in secili]
            veriler = [self.veriler[i] for i in secili_indeksler]
            gonderildi_kolon = ["Evet" if self.gonderildi_durum[i] else "Hayır" for i in secili_indeksler]
        else:
            veriler = self.veriler
            gonderildi_kolon = ["Evet" if durum else "Hayır" for durum in self.gonderildi_durum]
        dosya = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx")])
        if dosya:
            df = pd.DataFrame(veriler)
            df["Gönderildi"] = gonderildi_kolon
            df.to_excel(dosya, index=False)
            messagebox.showinfo("Başarılı", "Excel dosyası kaydedildi.")

    def pdf_aktar(self):
        if not self.veriler:
            messagebox.showinfo("Bilgi", "Aktarılacak veri yok.")
            return
        secili = self.tablo.selection()
        if secili:
            secili_indeksler = [self.tablo.index(item) for item in secili]
            veriler = [self.veriler[i] for i in secili_indeksler]
            gonderildi_kolon = ["Evet" if self.gonderildi_durum[i] else "Hayır" for i in secili_indeksler]
        else:
            veriler = self.veriler
            gonderildi_kolon = ["Evet" if durum else "Hayır" for durum in self.gonderildi_durum]
        dosya = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if dosya:
            font_path = "DejaVuSans.ttf"
            if not os.path.exists(font_path):
                messagebox.showerror("Hata", "PDF çıktısı için DejaVuSans.ttf dosyasını proje klasörüne koymalısınız!\nhttps://dejavu-fonts.github.io/Download.html adresinden indirip zipten çıkarabilirsiniz.")
                return
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('DejaVu', '', font_path, uni=True)
            pdf.set_font('DejaVu', '', 12)
            pdf.cell(200, 10, txt="Lastik Parçalama Raporu", ln=True, align="C")
            pdf.ln(10)
            basliklar = ["Lastik", "Tel", "Tekstil", "Kauçuk", "Gönderildi"]
            for baslik in basliklar:
                pdf.cell(40, 10, baslik, border=1)
            pdf.ln()
            for i, veri in enumerate(veriler):
                gonderildi = gonderildi_kolon[i]
                satir = [veri["Lastik"], veri["Tel"], veri["Tekstil"], veri["Kauçuk"], gonderildi]
                for deger in satir:
                    pdf.cell(40, 10, str(deger), border=1)
                pdf.ln()
            pdf.output(dosya)
            messagebox.showinfo("Başarılı", "PDF dosyası kaydedildi.")

    def secilenleri_excel_aktar(self):
        self._aktar_sadece_secili(excel=True)

    def secilenleri_pdf_aktar(self):
        self._aktar_sadece_secili(excel=False)

    def _aktar_sadece_secili(self, excel=True):
        if not self.veriler:
            messagebox.showinfo("Bilgi", "Aktarılacak veri yok.")
            return
        secili = self.tablo.selection()
        if not secili:
            messagebox.showinfo("Bilgi", "Lütfen aktarılacak satır(lar)ı seçin.")
            return
        secili_indeksler = [self.tablo.index(item) for item in secili]
        veriler = [self.veriler[i] for i in secili_indeksler]
        gonderildi_kolon = ["Evet" if self.gonderildi_durum[i] else "Hayır" for i in secili_indeksler]
        if excel:
            dosya = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx")])
            if dosya:
                df = pd.DataFrame(veriler)
                df["Gönderildi"] = gonderildi_kolon
                df.to_excel(dosya, index=False)
                messagebox.showinfo("Başarılı", "Excel dosyası kaydedildi.")
        else:
            dosya = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Dosyası", "*.pdf")])
            if dosya:
                font_path = "DejaVuSans.ttf"
                if not os.path.exists(font_path):
                    messagebox.showerror("Hata", "PDF çıktısı için DejaVuSans.ttf dosyasını proje klasörüne koymalısınız!\nhttps://dejavu-fonts.github.io/Download.html adresinden indirip zipten çıkarabilirsiniz.")
                    return
                pdf = FPDF()
                pdf.add_page()
                pdf.add_font('DejaVu', '', font_path, uni=True)
                pdf.set_font('DejaVu', '', 12)
                pdf.cell(200, 10, txt="Lastik Parçalama Raporu", ln=True, align="C")
                pdf.ln(10)
                basliklar = ["Lastik", "Tel", "Tekstil", "Kauçuk", "Gönderildi"]
                for baslik in basliklar:
                    pdf.cell(40, 10, baslik, border=1)
                pdf.ln()
                for i, veri in enumerate(veriler):
                    gonderildi = gonderildi_kolon[i]
                    satir = [veri["Lastik"], veri["Tel"], veri["Tekstil"], veri["Kauçuk"], gonderildi]
                    for deger in satir:
                        pdf.cell(40, 10, str(deger), border=1)
                    pdf.ln()
                pdf.output(dosya)
                messagebox.showinfo("Başarılı", "PDF dosyası kaydedildi.")

def main():
    root = tk.Tk()
    app = LastikUygulamasi(root)
    root.mainloop()

if __name__ == "__main__":
    main() 