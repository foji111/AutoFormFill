// marksheet.py
import os
import json
import base64
import binascii
import io
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Body, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image
import google.generativeai as genai

# --- Configuration ---
# It's recommended to load the API key from environment variables for security
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not found. Please set it.")

genai.configure(api_key=GOOGLE_API_KEY)

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Marksheet Extractor API",
    description="An API to extract structured information from a marksheet image using Gemini.",
    version="1.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Marksheet Data ---

class SubjectResult(BaseModel):
    """Defines the structure for a single subject's result."""
    subject_code: Optional[str] = Field(None, description="Course or subject code, if available.")
    subject_name: str = Field(..., description="Name of the subject or course.")
    grade: str = Field(..., description="Grade, marks, or score obtained in the subject.")
    credits: Optional[float] = Field(None, description="Credits assigned to the subject, if available.")

class MarksheetData(BaseModel):
    """Defines the main structure for the extracted marksheet information."""
    student_name: str = Field(..., description="Full name of the student.")
    enrollment_number: str = Field(..., description="Student's unique enrollment or roll number.")
    university_name: str = Field(..., description="Name of the University, College, or Institution.")
    program_name: str = Field(..., description="Name of the degree or program (e.g., Master of Computer Applications).")
    semester: Optional[str] = Field(None, description="The semester or examination period (e.g., 'Summer - 2024', 'Semester V').")
    results: List[SubjectResult] = Field(..., description="A list of all subjects with their corresponding results.")
    overall_score: Optional[float] = Field(None, alias="spi", description="The final Semester Performance Index (SPI), SGPA, CGPA, or Percentage. Extract only the numerical value.")
    result_status: str = Field(..., description="Overall result status (e.g., 'Pass', 'Fail', 'First Class with Distinction').")
    date_of_issue: Optional[str] = Field(None, description="The date the marksheet was issued in DD-MM-YYYY format.")

class ImageRequest(BaseModel):
    """Model for receiving a base64 encoded image."""
    image_base64: str

# --- Gemini Extraction Logic ---

def extract_marksheet_info_from_image(img: Image.Image) -> dict:
    """
    Analyzes a marksheet image using the Gemini model to extract structured details.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        # This robust prompt guides the model to extract key fields and handle variations.
        prompt = """
        Analyze the provided marksheet, statement of marks, or semester performance report image.
        Extract the following information and structure it in a clean JSON format.

        IMPORTANT:
        1.  Identify key details like the student's name, enrollment/roll number, university name, and program name.
        2.  For the results, create a JSON array for the 'results' field. Each item in the array should be an object representing one subject, containing its code, name, grade/marks, and credits (if available).
        3.  Find the overall performance score. This might be labeled as SPI, SGPA, CGPA, or Percentage. Extract only the numerical value for the 'overall_score' field.
        4.  Determine the final result status (e.g., 'Pass', 'First Class with Distinction').
        5.  If a field is not clearly visible or present, use `null` for its value.
        6.  The final output must be ONLY the raw JSON object, without any markdown formatting like ```json ... ```.

        Here is the target JSON structure:
        {
          "student_name": "Full Name of the student",
          "enrollment_number": "The enrollment or roll number",
          "university_name": "Name of the University/College",
          "program_name": "The degree or program name",
          "semester": "The semester or exam period",
          "results": [
            {
              "subject_code": "The subject code",
              "subject_name": "The name of the first subject",
              "grade": "Grade/marks for the first subject",
              "credits": 3.0
            }
          ],
          "overall_score": 8.13,
          "result_status": "The final pass/fail/class status",
          "date_of_issue": "The issue date in DD-MM-YYYY format"
        }
        """

        response = model.generate_content([prompt, img])

        # Clean up potential markdown formatting from the model's response
        json_output = response.text.strip()
        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()
            
        parsed_data = json.loads(json_output)
        
        # Manually alias spi to overall_score if model uses it
        if 'spi' in parsed_data and 'overall_score' not in parsed_data:
            parsed_data['overall_score'] = parsed_data.pop('spi')
            
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
    return {"status": "ok", "message": "Welcome to the Marksheet Extractor API!"}

@app.post("/extract-marksheet-from-file/", response_model=MarksheetData, summary="Extract Marksheet Info From File")
async def extract_marksheet_from_file(file: UploadFile = File(...)):
    """
    Accepts a direct marksheet image file (jpg, png) and extracts its details.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        image_data = await file.read()
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
    except IOError:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")
    
    marksheet_data = extract_marksheet_info_from_image(img)
    validated_data = MarksheetData(**marksheet_data)
    return validated_data

@app.post("/extract-marksheet-from-base64/", response_model=MarksheetData, summary="Extract Marksheet Info (Base64)")
async def extract_marksheet_from_base64(request: ImageRequest):
    """
    Accepts a base64 encoded image string, decodes it, and extracts marksheet details.
    """
    try:
        image_data = base64.b64decode(request.image_base64)
        image_stream = io.BytesIO(image_data)
        img = Image.open(image_stream)
    except (binascii.Error, IOError):
        raise HTTPException(status_code=400, detail="Invalid or corrupted base64 image data.")
    
    marksheet_data = extract_marksheet_info_from_image(img)
    validated_data = MarksheetData(**marksheet_data)
    return validated_data

# Health check for deployment environments
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)