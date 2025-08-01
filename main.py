# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all your new routers
from pancard_routes import router as pan_router
from aadharcard_routes import router as aadhar_router
from marksheet_routes import router as marksheet_router # <-- ADD THIS

app = FastAPI(
    title="ID Extractor API",
    description="Extract info from PAN, Aadhaar, and Marksheet images using Gemini",
    version="2.0.1" # Version bump
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the routers with their correct prefixes
app.include_router(pan_router, prefix="/pan", tags=["PAN Card"])
app.include_router(aadhar_router, prefix="/aadhaar", tags=["Aadhaar Card"])
app.include_router(marksheet_router, prefix="/marksheet", tags=["Marksheet"]) 

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Unified API is running."}