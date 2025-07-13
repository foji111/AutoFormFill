import os
import json
import base64
import binascii
import io

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import google.generativeai as genai

# --- Configuration ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Aadhar Card Extractor API",
    description="An API to extract information from an Aadhar card image using Gemini.",
    version="1.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class AadharRequest(BaseModel):
    image_base64: str

class AadharData(BaseModel):
    name: str
    aadhar_number: str
    date_of_birth: str
    gender: str
    guardian_or_care_of: str
    address: str

# --- Gemini Extraction Logic ---
def extract_aadhar_info_from_image(img: Image.Image):
    """
    Analyzes an image using the Gemini model to extract Aadhar card details.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = """
        Analyze this Aadhar card image and extract the following information in a clean JSON format:
        {
            "name": "Full Name of the cardholder",
            "aadhar_number": "12-digit Aadhar number without any spaces",
            "date_of_birth": "Date of Birth in DD/MM/YYYY format",
            "gender": "Male or Female or Other",
            "guardian_or_care_of": "Guardian's or C/O name (if present, otherwise empty string)",
            "address": "Full address as a single, complete string"
        }
        If a field is not clearly visible or found, use an empty string "" for its value.
        Ensure the output is ONLY the raw JSON object, without any markdown formatting like ```json ... ```.
        """

        response = model.generate_content([prompt, img])

        # Clean up the response
        json_output = response.text.strip()
        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()
            
        parsed_data = json.loads(json_output)
        return parsed_data

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw model output: {response.text}")
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Failed to parse JSON output from the model.",
                "raw_output": response.text
            }
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail={"error": f"An unexpected error occurred: {str(e)}"})

# --- API Endpoints ---
@app.get("/", summary="Health Check")
def read_root():
    return {"status": "ok", "message": "Welcome to the Aadhar Extractor API!"}

@app.post("/extract-aadhar/", response_model=AadharData, summary="Extract Aadhar Information")
async def extract_from_aadhar(request: AadharRequest):
    """
    Accepts a base64 encoded image, decodes it, and extracts Aadhar card details.
    """
    try:
        # Decode the base64 string
        image_data = base64.b64decode(request.image_base64)
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)

    except (base64.binascii.Error, binascii.Error, IOError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted image data: {e}")

    # Process the image and get the data
    aadhar_data = extract_aadhar_info_from_image(img)
    
    # Validate the extracted data
    validated_data = AadharData(**aadhar_data)
    
    return validated_data

# Health check for deployment
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))