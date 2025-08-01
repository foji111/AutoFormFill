// pancard.py
import os
import json
import base64
import binascii
import io

from fastapi import FastAPI, HTTPException, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
import google.generativeai as genai

# --- Configuration ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it.")

if not GOOGLE_API_KEY.startswith("AIza"):
    raise ValueError("Invalid Google API key format. Please check your API key.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="PAN Card Extractor API",
    description="An API to extract information from a PAN card image using Gemini.",
    version="1.0.1" # Version updated
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class PANCardRequest(BaseModel):
    image_base64: str

class PANCardData(BaseModel):
    name: str = Field(..., description="Full name of the cardholder.")
    pan_number: str = Field(..., description="Permanent Account Number (10 characters, alphanumeric).")
    date_of_birth: str = Field(..., description="Cardholder's date of birth in DD/MM/YYYY format.")
    fathers_name: str = Field(..., description="Cardholder's father's name.")

# --- Gemini Extraction Logic ---
def extract_pancard_info_from_image(img: Image.Image):
    """
    Analyzes an image using the Gemini model to extract PAN card details.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analyze this PAN card image and extract the following information in a clean JSON format:
        {
            "name": "Full Name of the cardholder",
            "pan_number": "PAN Number (10 characters, alphanumeric)",
            "date_of_birth": "Date of Birth in DD/MM/YYYY format",
            "fathers_name": "Father's Name"
        }
        If a field is not clearly visible or found, use an empty string "" for its value.
        Ensure the output is ONLY the raw JSON object, without any markdown formatting like ```json ... ```.
        """

        response = model.generate_content([prompt, img])

        # --- THIS IS THE CORRECTED PART ---
        # Use the more robust cleanup logic from your Aadhar script
        json_output = response.text.strip()
        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()
        # --- END OF CORRECTION ---
            
        parsed_data = json.loads(json_output)
        return parsed_data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Failed to parse JSON output from the model.",
                "raw_output": response.text
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"An unexpected error occurred: {str(e)}"})

# --- API Endpoints ---
@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "Welcome to the PAN Card Extractor API!"}

@app.post("/extract-pancard-from-file/", response_model=PANCardData, summary="Extract PAN Card Info From File")
async def extract_pancard_from_file(file: UploadFile = File(...)):
    """
    Accepts a direct image file upload (jpg, png) and extracts PAN card details.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        image_data = await file.read()
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
    except IOError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")
    
    pancard_data = extract_pancard_info_from_image(img)
    validated_data = PANCardData(**pancard_data)
    return validated_data

@app.post("/extract-pancard-from-base64/", response_model=PANCardData, summary="Extract PAN Card Info (Base64)")
async def extract_pancard_from_base64(request: PANCardRequest):
    """
    Accepts a base64 encoded image string, decodes it, and extracts PAN card details.
    """
    try:
        image_data = base64.b64decode(request.image_base64)
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
    except (binascii.Error, IOError):
        raise HTTPException(status_code=400, detail="Invalid or corrupted base64 image data.")
    
    pancard_data = extract_pancard_info_from_image(img)
    validated_data = PANCardData(**pancard_data)
    return validated_data

# Health check for deployment environments
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)