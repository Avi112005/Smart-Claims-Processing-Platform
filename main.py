import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from google import generativeai as genai
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Allow CORS (for frontend dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-file")
async def analyze_file(
    claim_type: str = Form(None),
    priority: str = Form(None),
    document: UploadFile = File(...)
):
    print(f"Received file: {document.filename}, content_type: {document.content_type}")
    content = await document.read()
    print(f"File size: {len(content)} bytes")

    file_text = None
    vision_part = None

    # Handle PDFs
    if document.content_type == "application/pdf":
        try:
            temp_path = f"temp_{document.filename}"
            with open(temp_path, "wb") as f:
                f.write(content)
            reader = PdfReader(temp_path)
            file_text = "\n".join([page.extract_text() or "" for page in reader.pages])
            os.remove(temp_path)
            if not file_text.strip():
                return JSONResponse({"error": "Could not extract text from PDF."}, status_code=400)
        except Exception as e:
            print("PDF error:", e)
            return JSONResponse({"error": "Failed to read PDF."}, status_code=400)

    # Handle plain text files
    elif document.content_type == "text/plain":
        file_text = content.decode("utf-8")
        print(f"Extracted text length: {len(file_text)}")

    # Handle images
    elif document.content_type in ["image/jpeg", "image/png"]:
        try:
            vision_part = {
                "mime_type": document.content_type,
                "data": content
            }
            print("Prepared image for Gemini Vision")
        except Exception as e:
            print("Failed to prepare image part:", e)
            return JSONResponse({"error": "Image handling failed."}, status_code=400)
    else:
        return JSONResponse({"error": "Unsupported file type."}, status_code=400)

    # Updated Gemini prompt including Policy Compliance
    prompt_instructions = """
You are an AI insurance claim analyst.

1. Extract the following fields from the claim document (if present):  
- claimant_name  
- claim_date  
- claim_amount  
- claim_description  
- damages  
- policy_number

2. Classify the claim type (e.g. "Auto", "Home", "Health", "Life", "Other").  

3. Determine the claim priority (e.g. "High", "Medium", "Low") based on urgency and damages described.  

4. Assess policy compliance:  
- Evaluate if the claim follows the rules and terms of the relevant insurance policy.  
- Identify any policy exclusions or conditions that might affect the claim's approval.  
- If possible, indicate if the claim is compliant, partially compliant, or non-compliant.  

5. Provide a brief summary of the claim.

Return the result in strict JSON format like:

{
  "claimant_name": "...",
  "claim_date": "...",
  "claim_amount": "...",
  "claim_description": "...",
  "damages": "...",
  "policy_number": "...",
  "claim_type": "...",
  "priority": "...",
  "policy_compliance": {
    "status": "Compliant / Partially Compliant / Non-Compliant / Unknown",
    "notes": "Details on any rules or exclusions applied"
  },
  "summary": "..."
}

If a field is missing, return null for it.
"""

    # Choose model
    if vision_part:
        model_name = "models/gemini-1.5-flash"
        prompt_parts = [
            vision_part,
            {"text": prompt_instructions}
        ]
    else:
        model_name = "models/gemini-1.5-pro"
        prompt_parts = [
            {"text": file_text[:12000]},
            {"text": prompt_instructions}
        ]

    print(f"Calling Gemini with model: {model_name}")

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt_parts)
        print("Gemini response:", response.text)

        # Strip ```json or ``` code block formatting
        clean_text = (
            response.text
            .strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        return json.loads(clean_text)
    except Exception as e:
        print("Gemini error:", e)
        return JSONResponse({"error": f"Gemini API error: {str(e)}"}, status_code=500)

@app.get("/")
def root():
    return {"status": "✅ Smart Claims Processing Backend Running"}
