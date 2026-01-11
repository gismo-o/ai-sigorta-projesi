import os
import joblib
import numpy as np
import pandas as pd
import logging
from fastapi.responses import FileResponse
from enum import Enum
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# AYARLAR VE LOGLAMA (CONFIGURATION & LOGGING)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SigortaAPI")

# ENUM SINIFLARI (TYPE SAFETY) 
class SexEnum(str, Enum):
    MALE = "Erkek"
    FEMALE = "Kadın"

class SmokerEnum(str, Enum):
    YES = "Evet"
    NO = "Hayır"

class RegionEnum(str, Enum):
    SOUTHWEST = "southwest"
    SOUTHEAST = "southeast"
    NORTHWEST = "northwest"
    NORTHEAST = "northeast"

# PYDANTIC ŞEMALARI (DATA TRANSFER OBJECTS - DTO)
class InsuranceInput(BaseModel):
    age: int = Field(..., gt=0, lt=120, description="Kişinin yaşı (0-120 arası)")
    sex: SexEnum
    bmi: float = Field(..., gt=10.0, lt=100.0, description="Vücut Kitle İndeksi")
    children: int = Field(..., ge=0, lt=20, description="Çocuk sayısı") 
    smoker: SmokerEnum
    region: RegionEnum

    class Config:
        json_schema_extra = {
            "example": {
                "age": 30,
                "sex": "Erkek",
                "bmi": 25.5,
                "children": 0,
                "smoker": "Hayır",
                "region": "southwest"
            }
        }

class InsuranceOutput(BaseModel):
    prediction_usd: float
    currency: str = "USD"
    risk_level: str

# SERVİS KATMANI (BUSINESS LOGIC LAYER)
# Tüm makine öğrenmesi mantığı bu sınıfta toplanır.
class InsuranceModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_artifacts()

    def _load_artifacts(self):
        """Model ve Scaler dosyalarını diskten yükler."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "insurance_model_rf.pkl")
            scaler_path = os.path.join(base_dir, "scaler.pkl")

            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                raise FileNotFoundError("Model veya Scaler dosyası bulunamadı.")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            logger.info("ML Modeli ve Scaler başarıyla yüklendi.")
        except Exception as e:
            logger.critical(f"Model yükleme hatası: {e}")
            raise RuntimeError("Servis başlatılamadı, model dosyaları eksik.")

    def _preprocess(self, data: InsuranceInput) -> np.ndarray:
        """Gelen veriyi modelin anlayacağı formata (Encoding/Scaling) çevirir."""
        # Encoding
        sex_enc = 1 if data.sex == SexEnum.MALE else 0
        smoker_enc = 1 if data.smoker == SmokerEnum.YES else 0
        bmi_smoker = data.bmi * smoker_enc
        
        # Region One-Hot Encoding
        regions = {
            'region_northwest': 1 if data.region == RegionEnum.NORTHWEST else 0,
            'region_southeast': 1 if data.region == RegionEnum.SOUTHEAST else 0,
            'region_southwest': 1 if data.region == RegionEnum.SOUTHWEST else 0
        }
        
        # Feature Listesi oluşturma
        features = [
            data.age,
            sex_enc,
            data.bmi,
            data.children,
            smoker_enc,
            regions['region_northwest'],
            regions['region_southeast'],
            regions['region_southwest'],
            bmi_smoker
        ]

        # DataFrame oluşturma
        columns = ['age', 'sex', 'bmi', 'children', 'smoker', 
                   'region_northwest', 'region_southeast', 'region_southwest', 
                   'bmi_smoker']
        
        input_df = pd.DataFrame([features], columns=columns)
        
        # Scaling
        return self.scaler.transform(input_df)

    def predict(self, data: InsuranceInput) -> InsuranceOutput:
        """Tahmin işlemini gerçekleştirir."""
        if not self.model:
            raise RuntimeError("Model yüklü değil!")

        try:
            # Ön işleme
            processed_data = self._preprocess(data)
            
            # Tahmin (Logaritmik sonuç)
            pred_log = self.model.predict(processed_data)
            
            # Ters Dönüşüm (Log -> USD)
            pred_usd = float(np.expm1(pred_log)[0])
            
            # Basit Risk Analizi (Business Logic)
            risk = "Yüksek Risk" if pred_usd > 10000 else "Normal Risk"

            return InsuranceOutput(
                prediction_usd=round(pred_usd, 2),
                risk_level=risk
            )
        except Exception as e:
            logger.error(f"Tahmin sırasında hata: {e}")
            raise e

# BAĞIMLILIK ENJEKSİYONU (DEPENDENCY INJECTION)
# Modeli global değişken yerine bir "state" olarak yönetiyoruz.
ml_service: Optional[InsuranceModelService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlarken modeli yükler, kapanırken temizler."""
    global ml_service
    ml_service = InsuranceModelService() # Başlangıçta yükle
    yield
    ml_service = None # Kapanışta temizle

def get_ml_service():
    """Endpointlere servisi enjekte etmek için kullanılır."""
    if not ml_service:
        raise HTTPException(status_code=503, detail="Model servisi henüz hazır değil.")
    return ml_service

# UYGULAMA VE ENDPOINTLER (FastAPI APP & ENDPOINTS)
app = FastAPI(
    title="Sigorta Fiyat Tahmin API",
    version="2.0.0",
    lifespan=lifespan
)

# Güvenlik: CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/") # Sağlık Kontrolü Endpointi
def read_root():
    return FileResponse('index.html')

@app.post("/predict", response_model=InsuranceOutput) # Tahmin Endpointi
def predict_endpoint( 
    input_data: InsuranceInput, 
    service: InsuranceModelService = Depends(get_ml_service)
):
    try: # Tahmin işlemi
        result = service.predict(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sunucu hatası oluştu.")