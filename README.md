# Lastik Parçalama Takip Uygulaması

Bu uygulama, gelen lastiklerin parçalanması sonrası çıkan tel, tekstil ve kauçuk miktarlarını kaydetmenizi ve bu verileri Excel veya PDF olarak dışa aktarmanızı sağlar.

## Kurulum

1. Python 3 yüklü olmalıdır.
2. Gerekli kütüphaneleri yüklemek için:

```
pip install -r requirements.txt
```

## Kullanım

```
python main.py
```

## .exe'ye Dönüştürme

1. PyInstaller'ı yükleyin:
```
pip install pyinstaller
```
2. .exe oluşturmak için:
```
pyinstaller --onefile --noconsole main.py
```
3. `dist` klasörü içinde `main.exe` dosyasını bulabilirsiniz.

## Özellikler
- Birden fazla giriş ekleyebilirsiniz.
- Verileri tablo halinde görebilirsiniz.
- Excel veya PDF olarak dışa aktarabilirsiniz.

Herhangi bir sorun olursa bana ulaşabilirsiniz. 