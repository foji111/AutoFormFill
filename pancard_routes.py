# pancard_routes.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from PIL import Image
import base64, binascii, io, os, json
import logging
import google.generativeai as genai

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key setup
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

class PANCardRequest(BaseModel):
    image_base64: str

class PANCardData(BaseModel):
    name: str = Field(..., description="Full name of the cardholder.")
    pan_number: str = Field(..., description="PAN number (10 characters, alphanumeric).")
    date_of_birth: str = Field(..., description="Date of Birth in DD/MM/YYYY format.")

def extract_pancard_info_from_image(img: Image.Image):
    model = genai.GenerativeModel('gemini-1.5-flash')
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    prompt = """Analyze this PAN card image and extract this info in JSON:
    {
      "name": "...",
      "pan_number": "...",
      "date_of_birth": "..."
    }"""

    response = model.generate_content([
        prompt,
        { "mime_type": "image/png", "data": image_bytes }
    ])
    text = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(text)

@router.post("/extract-from-file", response_model=PANCardData)
async def extract_pan_from_file(file: UploadFile = File(...)):
    # Sentinel: Enforce file size limit to prevent DoS
    try:
        file.file.seek(0, 2)
        if file.file.tell() > MAX_FILE_SIZE:
             raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        file.file.seek(0)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.warning(f"File seek failed during size check: {e}")
        pass

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")
    try:
        img = Image.open(io.BytesIO(await file.read()))
    except Exception as e:
        logger.error(f"Error opening PAN image: {e}")
        raise HTTPException(status_code=400, detail="Invalid image")
    return PANCardData(**extract_pancard_info_from_image(img))

@router.post("/extract-from-base64", response_model=PANCardData)
async def extract_pan_from_base64(request: PANCardRequest):
    try:
        img = Image.open(io.BytesIO(base64.b64decode(request.image_base64)))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64")
    return PANCardData(**extract_pancard_info_from_image(img))
