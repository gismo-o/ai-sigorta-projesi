# Sağlık Sigortası Fiyat Tahmin Sistemi

**Makine Öğrenmesi Bootcamp Bitirme Projesi** kapsamında geliştirilen bu proje, geleneksel ve manuel sigorta fiyatlandırma süreçlerini, Yapay Zeka ve Modern Web Teknolojileri ile otomatize eden uçtan uca (End-to-End) bir çözüm sunar.

🔗 **Canlı Demo:** [https://ai-sigorta-projesi.onrender.com](https://ai-sigorta-projesi.onrender.com)

Geliştirilen sistem, geçmiş müşteri verilerini analiz ederek karmaşık risk faktörlerini (Örn: Sigara ve Obezite etkileşimi) öğrenen bir Makine Öğrenmesi modeli üzerine kurulmuştur. Bu model, Dockerize edilmiş bir REST API aracılığıyla saniyeler içinde fiyat teklifi sunan modern bir web arayüzüne dönüştürülmüştür.

## Kullanılan Teknolojiler (Tech Stack)

*   **Model Eğitimi:** Python, Scikit-Learn, Pandas, NumPy
*   **Backend & API:** FastAPI, Pydantic, Uvicorn
*   **Frontend:** HTML5, JavaScript (Fetch API), Tailwind CSS
*   **DevOps & Deployment:** Docker, Docker Compose, uv (Package Manager), Render
*   **Versiyon Kontrol:** Git & GitHub



## Veri Bilimi Süreci ve Metodoloji

### 1. Keşifçi Veri Analizi (EDA)
*   **Veri Seti:** [Medical Cost Personal Datasets (Kaggle)](https://www.kaggle.com/datasets/mirichoi0218/insurance)
*   **Kritik Bulgu:** Sigara içen ve BMI değeri 30'un üzerinde (Obez) olan bireylerin sağlık masraflarının, diğer gruplara göre katlanarak arttığı görselleştirildi.
*   **İstatistiksel Kanıt:** Sigara içenler ve içmeyenler arasındaki maliyet farkının tesadüf olmadığı **T-Testi (p < 0.05)** ile kanıtlandı.

### 2. Veri Ön İşleme ve Özellik Mühendisliği
*   **Feature Engineering:** Modelin "Sigara + Obezite" riskini daha iyi kavraması için **`bmi_smoker`** adında etkileşimli yeni bir değişken türetildi.
*   **Transformation:** Hedef değişken (`charges`) logaritmik dönüşümle normal dağılıma yaklaştırıldı.
*   **Scaling:** Veriler `StandardScaler` ile ölçeklendi.

### 3. Modelleme ve Performans
*   **Algoritma Seçimi:** Linear Regression, Ridge, XGBoost, LightGBM, CatBoost ve Random Forest modelleri kıyaslandı.
*   **Şampiyon Model:** En yüksek başarıyı ve genelleme yeteneğini gösteren **Random Forest Regressor** seçildi.
*   **Optimizasyon:** `GridSearchCV` ile hiperparametre optimizasyonu yapıldı.
*   **Sonuçlar:**
    *   **R² Skoru:** %87.7
    *   **MAPE (Ortalama Hata Payı):** %17.14
    *   **Güvenilirlik:** 5-Katlı Çapraz Doğrulama (Cross-Validation) ile modelin kararlılığı test edildi.

## Yazılım Mimarisi

Sistem, **SOLID** prensiplerine uygun modüler bir yapıda tasarlanmıştır:

1.  **Service Layer Pattern:** ML mantığı (`InsuranceModelService`) ile API mantığı birbirinden izole edilmiştir.
2.  **Singleton Pattern:** Model dosyaları (`.pkl`) uygulama başlangıcında belleğe bir kez yüklenerek performans optimize edilmiştir.
3.  **Data Validation:** `Pydantic` şemaları ile API'ye gelen veriler (Örn: Yaş < 0 veya Yaş > 120) sıkı bir denetimden geçirilir.
4.  **Dinamik Frontend:** Kullanıcı arayüzü, modelden gelen sonuca göre (Yüksek Risk / Normal Risk) renk değiştiren dinamik bir yapıya sahiptir. Entegre **BMI Hesaplayıcı** modülü içerir.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz.

### Seçenek 1: Docker ile Çalıştırma (Önerilen)
Bilgisayarınızda Python kurulu olmasa bile Docker sayesinde tek komutla çalıştırabilirsiniz.

```bash
# 1. Repoyu klonlayın
git clone https://github.com/gismo-o/ai-sigorta-projesi.git
cd ai-sigorta-projesi

# 2. Docker konteynerini başlatın
docker compose up --build
```
Tarayıcıda: `http://localhost:8000`

### Seçenek 2: uv veya pip ile Çalıştırma

```bash
# 1. Bağımlılıkları yükleyin
pip install -r requirements.txt
# Veya uv kullanıyorsanız: uv sync

# 2. Uygulamayı başlatın
uvicorn main:app --reload
```

---

## 📂 Proje Yapısı

```text
ai-sigorta-projesi/
├── .venv/                   # Sanal ortam (Git'e yüklenmez)
├── insurance_model_rf.pkl   # Eğitilmiş Random Forest Modeli
├── scaler.pkl               # Eğitilmiş Ölçekleyici (StandardScaler)
├── main.py                  # FastAPI Backend Kodları
├── index.html               # Frontend Arayüzü
├── Dockerfile               # Docker İmaj Dosyası
├── docker-compose.yml       # Docker Orkestrasyonu
├── requirements.txt         # Kütüphane Bağımlılıkları
├── health_insurance_ai_model.ipynb # EDA, İstatistiksel Testler, Model Benchmarking ve Hiperparametre Optimizasyonu
└── README.md                # Proje Dokümantasyonu
```
