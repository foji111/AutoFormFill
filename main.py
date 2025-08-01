from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pancard_routes import router as pan_router
from aadharcard_routes import router as aadhar_router

app = FastAPI(
    title="ID Extractor API",
    description="Extract info from PAN and Aadhaar card images using Gemini",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pan_router, prefix="/pan", tags=["PAN Card"])
app.include_router(aadhar_router, prefix="/aadhaar", tags=["Aadhaar Card"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Unified API is running."}
