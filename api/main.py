from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.homepage import info as home_info
from routers.mapspage import info as maps_info
from routers.predictpage import info as predict_info
from routers.mappingpage import info as mapping_info
from routers.recommendpage import info as recommend_info
from routers.foodpage import info as food_info

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

# Home Page Router
app.include_router(home_info.router, prefix="/api/home", tags=["home"])
# Maps Page Router
app.include_router(maps_info.router, prefix="/api/maps", tags=["maps"])
# Predict Page Router
app.include_router(predict_info.router, prefix="/api/predict", tags=["predict"])
# Mapping Page Router
app.include_router(mapping_info.router, prefix="/api/mapping", tags=["mapping"])
# Recommend Page Router
app.include_router(recommend_info.router, prefix="/api/recommend", tags=["recommend"])
# Food Page Router
app.include_router(food_info.router, prefix="/api/food", tags=["food"])
