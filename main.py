import flet as ft
from datetime import datetime

def main(page: ft.Page):
    # --- TEMİZLİK (Sadece bir kere çalışır) ---
    # Eğer veriler bozuksa bunu açıp bir kere çalıştır, sonra kapat.
    # page.client_storage.clear()
    
    page.title = "StudyMate"
    page.theme_mode = "dark" # String kullandık
    page.scroll = "adaptive"

    # --- VERİLERİ YÜKLE ---
    if not page.client_storage.contains_key("dersler"):
        page.client_storage.set("dersler", [])
    dersler = page.client_storage.get("dersler")

    # --- GRID ---
    grid = ft.GridView(
        expand=1, 
        max_extent=200, 
        child_aspect_ratio=1.0,
        spacing=10,
        run_spacing=10
    )

    # --- YARDIMCI FONKSİYONLAR ---
    def kalan_gun_hesapla(tarih_str):
        try:
            hedef = datetime.strptime(tarih_str, "%d.%m.%Y")
            bugun = datetime.now()
            fark = hedef - bugun
            if fark.days < 0:
                return "Süre Bitti"
            return f"{fark.days} Gün"
        except:
            return "Hata"

    # --- SİLME FONKSİYONU ---
    def ders_sil(ders_verisi):
        if ders_verisi in dersler:
            dersler.remove(ders_verisi)
            page.client_storage.set("dersler", dersler)
            ekrani_guncelle()
            page.snack_bar = ft.SnackBar(ft.Text("Ders Silindi!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # --- KART OLUŞTURMA ---
    def kart_olustur(ders):
        # Renk mantığı
        renk = "yellow"
        try:
            hedef = datetime.strptime(ders["tarih"], "%d.%m.%Y")
            bugun = datetime.now()
            fark = hedef - bugun
            if 0 <= fark.days <= 3:
                renk = "red"
        except:
            pass

        return ft.Container(
            content=ft.Column([
                # Silme Butonu
                ft.Row(
                    [ft.IconButton(icon="delete", icon_color="red", 
                                   on_click=lambda e: ders_sil(ders))],
                    alignment="end"
                ),
                ft.Text(ders["adi"], size=20, weight="bold", color="white"),
                ft.Icon(name="timelapse", color="white", size=40),
                ft.Text(kalan_gun_hesapla(ders["tarih"]), size=16, color=renk),
                ft.Text(ders["tarih"], size=12, color="white70"),
            ], alignment="center", horizontal_alignment="center"),
            bgcolor="bluegrey", # String renk
            border_radius=15,
            padding=10,
            alignment=ft.alignment.center
        )

    # --- EKRANI GÜNCELLEME ---
    def ekrani_guncelle():
        grid.controls.clear()
        for ders in dersler:
            if isinstance(ders, dict) and "tarih" in ders:
                grid.controls.append(kart_olustur(ders))
        page.update()

    ekrani_guncelle()

    # ==========================================
    # --- YENİ DATE PICKER (GÜNCEL SÜRÜM) ---
    # ==========================================

    def takvimden_secildi(e):
        if e.control.value: # Eğer tarih seçildiyse (İptal edilmediyse)
            tarih_kutusu.value = e.control.value.strftime("%d.%m.%Y")
            page.update()

    # DatePicker'ı tanımlıyoruz
    date_picker = ft.DatePicker(
        on_change=takvimden_secildi,
        first_date=datetime.now(),
        cancel_text="İptal",
        confirm_text="Seç"
    )
    
    # DİKKAT: Artık page.overlay.append YAPMIYORUZ.
    # page.open() bunu kendi halledecek.

    # --- GİRİŞ KUTULARI ---
    isim_kutusu = ft.TextField(label="Ders Adı", max_length=20)
    tarih_kutusu = ft.TextField(
        label="Sınav Tarihi",
        read_only=True,
        hint_text="Takvimi kullan ->",
        suffix_icon="calendar_month"
    )

    def kaydet_tusuna_basinca(e):
        if not isim_kutusu.value or not tarih_kutusu.value:
            page.snack_bar = ft.SnackBar(ft.Text("Lütfen alanları doldurun!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        yeni_veri = {"adi": isim_kutusu.value, "tarih": tarih_kutusu.value}
        dersler.append(yeni_veri)
        page.client_storage.set("dersler", dersler)

        ekrani_guncelle()
        
        isim_kutusu.value = ""
        tarih_kutusu.value = ""
        dialog_penceresi.open = False
        page.update()

    dialog_penceresi = ft.AlertDialog(
        title=ft.Text("Ders Ekle"),
        content=ft.Column([
            isim_kutusu,
            ft.Row([
                ft.Container(tarih_kutusu, expand=True),
                # KRİTİK DEĞİŞİKLİK BURADA:
                # date_picker.pick_date() YERİNE page.open(date_picker)
                ft.IconButton(icon="calendar_today", on_click=lambda _: page.open(date_picker))
            ])
        ], height=200),
        actions=[ft.ElevatedButton("Kaydet", on_click=kaydet_tusuna_basinca)]
    )

    page.appbar = ft.AppBar(
        title=ft.Text("StudyMate"),
        bgcolor="bluegrey900",
        actions=[
            ft.TextButton("EKLE", on_click=lambda e: page.open(dialog_penceresi)),
            ft.Container(width=10)
        ]
    )

    page.add(grid)

ft.app(target=main)