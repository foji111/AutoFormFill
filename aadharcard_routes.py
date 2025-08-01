# aadharcard_routes.py
import os
import io
import json
import base64
import binascii
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import google.generativeai as genai

# --- Router Initialization ---
router = APIRouter()

# --- Google API Key Setup ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not found.")
if not GOOGLE_API_KEY.startswith("AIza"):
    raise ValueError("Invalid Google API key format.")

genai.configure(api_key=GOOGLE_API_KEY)

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
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Convert image to PNG bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

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

        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/png",
                "data": image_bytes
            }
        ])

        json_output = response.text.strip()

        # Clean up potential markdown formatting
        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()

        parsed_data = json.loads(json_output)
        return parsed_data

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to parse JSON output from Gemini.",
                "raw_output": response.text
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": f"An unexpected error occurred: {str(e)}"}
        )

# --- API Endpoints ---

@router.post("/extract-from-file", response_model=AadharData)
async def extract_from_file(file: UploadFile = File(...)):
    """
    Accepts a direct image file upload (jpg, png), and extracts Aadhar card details.
    """
    try:
        image_data = await file.read()
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
    except IOError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")

    aadhar_data = extract_aadhar_info_from_image(img)
    validated_data = AadharData(**aadhar_data)
    return validated_data

@router.post("/extract-from-base64", response_model=AadharData)
async def extract_from_base64(request: AadharRequest):
    """
    Accepts a base64 encoded image string, decodes it, and extracts Aadhar card details.
    """
    try:
        image_data = base64.b64decode(request.image_base64)
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
    except (binascii.Error, IOError):
        raise HTTPException(status_code=400, detail="Invalid or corrupted base64 image data.")

    aadhar_data = extract_aadhar_info_from_image(img)
    validated_data = AadharData(**aadhar_data)
    return validated_data
