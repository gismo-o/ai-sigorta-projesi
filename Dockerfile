# 'slim' versiyonu gereksiz Linux araçlarını içermez, imaj boyutunu küçültür ve saldırı yüzeyini azaltır.
FROM python:3.10-slim

# 2. Environment Variables (Python Ayarları)
# PYTHONDONTWRITEBYTECODE: .pyc dosyalarının oluşmasını engeller (Docker'da gereksizdir).
# PYTHONUNBUFFERED: Logların anında terminale düşmesini sağlar (Hata takibi için kritik).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Çalışma Dizinini Ayarla
WORKDIR /app

# 4. Bağımlılıkları Yükle (Layer Caching Stratejisi)
# Önce SADECE requirements.txt'yi kopyalıyoruz.
# Kodda bir harf değişse bile requirements değişmediyse Docker bu adımı tekrar yapmaz (Cache'ten çeker). Hız kazandırır.
COPY requirements.txt .

# --no-cache-dir: Pip'in indirdiği önbellek dosyalarını tutmaz (İmaj boyutunu düşürür).
RUN pip install --no-cache-dir -r requirements.txt

# 5. Güvenlik: Root Olmayan Kullanıcı Oluştur (Best Practice)
# Konteyner ele geçirilirse saldırganın root yetkisi olmaması için.
RUN adduser --disabled-password --gecos "" appuser

# 6. Uygulama Kodlarını Kopyala
COPY . .

# 7. Dosya Sahipliğini Değiştir
# Kopyalanan dosyaların sahibini yeni oluşturduğumuz kullanıcı yapıyoruz.
RUN chown -R appuser:appuser /app

# 8. Kullanıcıya Geçiş Yap
USER appuser

# 9. Portu Bildir (Dokümantasyon amaçlı)
EXPOSE 8000

# 10. Başlatma Komutu
# host 0.0.0.0: Dış dünyadan gelen isteklere cevap ver demektir.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]