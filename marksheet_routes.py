# marksheet_routes.py
import os
import json
import base64
import binascii
import io
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Body, File, UploadFile
from pydantic import BaseModel, Field
from PIL import Image
import google.generativeai as genai

# --- Router Setup ---
# Use APIRouter instead of FastAPI
router = APIRouter()

# --- Configuration (remains the same) ---
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


# --- Pydantic Models (remains the same) ---
class SubjectResult(BaseModel):
    subject_code: Optional[str] = Field(None, description="Course or subject code.")
    subject_name: str = Field(..., description="Name of the subject or course.")
    grade: str = Field(..., description="Grade, marks, or score obtained.")
    credits: Optional[float] = Field(None, description="Credits for the subject.")

class MarksheetData(BaseModel):
    student_name: str = Field(..., description="Full name of the student.")
    enrollment_number: str = Field(..., description="Student's enrollment or roll number.")
    university_name: str = Field(..., description="Name of the University or Institution.")
    program_name: str = Field(..., description="Name of the degree or program.")
    semester: Optional[str] = Field(None, description="The semester or examination period.")
    results: List[SubjectResult] = Field(..., description="List of subjects with their results.")
    overall_score: Optional[float] = Field(None, alias="spi", description="SPI, SGPA, CGPA, or Percentage.")
    result_status: str = Field(..., description="Overall result status (e.g., 'Pass', 'First Class').")
    date_of_issue: Optional[str] = Field(None, description="Marksheet issue date in DD-MM-YYYY format.")

class ImageRequest(BaseModel):
    image_base64: str


# --- Gemini Extraction Logic (remains the same) ---
def extract_marksheet_info_from_image(img: Image.Image) -> dict:
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = """
Your primary task is to act as a highly accurate data extraction tool. Analyze the provided university marksheet image and convert the information into a structured JSON object.

**Key Instructions:**
1.  **Extract All Fields**: Carefully extract the student's name, enrollment number, university, program, and semester.
2.  **Subject List**: Create a JSON array for the 'results', capturing each subject's code, name, grade, and credits.
3.  **Find the SPI**: Pay special attention to the "Semester Performance Index" section. Locate the value explicitly labeled 'SPI' and place its numerical value into the 'overall_score' field.
4.  **Final Details**: Capture the overall 'result_status' (e.g., 'Pass') and the 'date_of_issue'.
5.  **Strict Formatting**: The output must be ONLY the raw JSON object. Do not include any extra text, explanations, or markdown formatting like ```json.

**Target JSON Structure:**
{
    "student_name": "...",
    "enrollment_number": "...",
    "university_name": "...",
    "program_name": "...",
    "semester": "...",
    "results": [
        {
            "subject_code": "...",
            "subject_name": "...",
            "grade": "...",
            "credits": 0.0
        }
    ],
    "overall_score": 0.0,
    "result_status": "...",
    "date_of_issue": "..."
}
"""
        response = model.generate_content([prompt, img])
        json_output = response.text.strip()
        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()
            
        parsed_data = json.loads(json_output)
        
        if 'spi' in parsed_data and 'overall_score' not in parsed_data:
            parsed_data['overall_score'] = parsed_data.pop('spi')
            
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


# --- API Endpoints ---
# IMPORTANT: Change decorators from @app.post to @router.post
# and simplify the paths to be combined with the prefix in main.py

@router.post("/extract-from-file", response_model=MarksheetData)
async def extract_marksheet_from_file(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        img = Image.open(io.BytesIO(await file.read()))
    except IOError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")
    
    marksheet_data = extract_marksheet_info_from_image(img)
    return MarksheetData(**marksheet_data)


@router.post("/extract-from-base64", response_model=MarksheetData)
async def extract_marksheet_from_base64(request: ImageRequest):
    try:
        img = Image.open(io.BytesIO(base64.b64decode(request.image_base64)))
    except (binascii.Error, IOError):
        raise HTTPException(status_code=400, detail="Invalid base64 image data.")
    
    marksheet_data = extract_marksheet_info_from_image(img)
    return MarksheetData(**marksheet_data)