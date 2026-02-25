from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Dict, Any
import uvicorn
import shutil
import os
import uuid
import time
import pandas as pd
import io
import json
from datetime import datetime

# Local imports
try:
    from extractor.text_extractor import TextExtractor
    from extractor.field_parser import FieldParser
except ImportError:
    # For local running without package install
    from .extractor.text_extractor import TextExtractor
    from .extractor.field_parser import FieldParser


app = FastAPI(title="Offer Letter Data Extractor", version="1.0.0")

# CORS Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
extractor = TextExtractor()
parser = FieldParser()

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/parse")
async def parse_files(files: List[UploadFile] = File(...)):
    job_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Limits
    if len(files) > 120:
        raise HTTPException(status_code=413, detail="Too many files. Max 120.")
        
    results = []
    summary = {
        "success": 0,
        "failed": 0,
        "scanned_pdf": 0,
        "invalid_type": 0,
        "processing_seconds": 0.0
    }
    
    for file in files:
        file_result = {
            "file_name": file.filename,
            "fields": {},
            "confidence": {},
            "methods": {},
            "error_code": None,
            "error_message": None
        }
        
        # Size Limit (10MB) - Approximate check based on spooled file
        # Note: UploadFile size might not be available immediately if spooled
        # We'll read it into memory (safe for <10MB)
        
        try:
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:
                file_result["error_code"] = "FILE_TOO_LARGE"
                file_result["error_message"] = "File exceeds 10MB limit."
                summary["failed"] += 1
                results.append(file_result)
                continue

            # Extract Text
            try:
                text = extractor.extract_text(content, file.filename)
            except ValueError as ve:
                err_str = str(ve)
                if "SCANNED_PDF" in err_str:
                     file_result["error_code"] = "SCANNED_PDF"
                     summary["scanned_pdf"] += 1
                elif "INVALID_TYPE" in err_str:
                     file_result["error_code"] = "INVALID_TYPE"
                     summary["invalid_type"] += 1
                else:
                     file_result["error_code"] = "PARSE_FAILED"
                     summary["failed"] += 1
                
                file_result["error_message"] = err_str
                results.append(file_result)
                continue

            # Parse Fields
            try:
                sections = extractor.split_sections(text)
                parsed_data = parser.parse(sections)
                file_result.update(parsed_data) # fields, confidence, methods
                
                # Check for empty document (heuristic)
                if len(text) < 200:
                    file_result["error_code"] = "SCANNED_OR_EMPTY"
                    file_result["error_message"] = "Extracted text is too short. Might be an image/scanned PDF."
                    summary["scanned_pdf"] += 1
                else:
                    summary["success"] += 1
                    
            except Exception as e:
                file_result["error_code"] = "UNKNOWN_ERROR"
                file_result["error_message"] = f"Extraction login failed: {str(e)}"
                summary["failed"] += 1
            
            results.append(file_result)
            
        except Exception as e:
            file_result["error_code"] = "UNKNOWN_ERROR"
            file_result["error_message"] = str(e)
            summary["failed"] += 1
            results.append(file_result)

    summary["processing_seconds"] = round(time.time() - start_time, 2)
    
    return {
        "job_id": job_id,
        "count": len(files),
        "results": results,
        "summary": summary
    }

@app.post("/export/csv")
async def export_csv(data: Dict[str, Any] = Body(...)):
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=400, detail="No data provided to export")
    
    # Flatten the data for CSV
    flat_data = []
    for item in results:
        row = {"File Name": item.get("file_name")}
        
        # Add fields
        fields = item.get("fields", {})
        for k, v in fields.items():
            row[k] = v
            
        # Add Error info
        if item.get("error_code"):
            row["Error Code"] = item.get("error_code")
            row["Error Message"] = item.get("error_message")
            
        flat_data.append(row)

    df = pd.DataFrame(flat_data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(iter([stream.getvalue()]),
                                 media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=export.csv"
    return response

@app.post("/export/xlsx")
async def export_xlsx(data: Dict[str, Any] = Body(...)):
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=400, detail="No data provided to export")
        
    flat_data = []
    
    # Pre-collect all unique salary components to create stable columns
    all_components = set()
    for item in results:
        rows = item.get("fields", {}).get("salary_table_rows", [])
        for r in rows:
            all_components.add(r.get("component"))
            
    # Sort them alphabetically for consistent ordering
    sorted_components = sorted(list(all_components))
            
    for item in results:
        fname = item.get("file_name")
        fields = item.get("fields", {})
        
        row = {
            "File Name": fname,
            "Name": fields.get("scheduleA_name"),
            "Entity": fields.get("scheduleA_entity"),
            "Designation": fields.get("designation"),
            "City": fields.get("location_city"),
            "State": fields.get("location_state"),
            "Joining Date": fields.get("date_of_joining_raw"),
            "Total CTC (INR)": fields.get("comp_total_annual_inr"),
            "Joining Bonus (INR)": fields.get("bonus_joining_inr"),
            "Retention Bonus (INR)": fields.get("bonus_retention_inr"),
            "ESOP Amount (INR)": fields.get("esop_amount_inr"),
            "Department": fields.get("scheduleA_department"),
            "Sub-Department": fields.get("scheduleA_sub_department"),
            "BYOD": fields.get("byod_clause"),
            "Band": fields.get("scheduleA_band"),
            "Grade": fields.get("scheduleA_grade"),
            "Table Gross Salary": fields.get("salary_table_totals", {}).get("gross_salary"),
            "Table Long Term Benefits": fields.get("salary_table_totals", {}).get("long_term_benefits"),
            "Table Fixed CTC": fields.get("salary_table_totals", {}).get("fixed_ctc"),
            "Table Total CTC": fields.get("salary_table_totals", {}).get("total_ctc")
        }
        
        # Denormalize dynamic salary components as columns
        salary_rows = fields.get("salary_table_rows", [])
        for comp in sorted_components:
            # Find if this file has this specific component
            match = next((r for r in salary_rows if r.get("component") == comp), None)
            row[f"{comp} (Per Annum)"] = match.get("per_annum") if match else None
            row[f"{comp} (Per Month)"] = match.get("per_month") if match else None

        if item.get("error_code"):
            row["Error Code"] = item.get("error_code")
            row["Error Message"] = item.get("error_message")
            
        flat_data.append(row)

    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df = pd.DataFrame(flat_data)
        df.to_excel(writer, index=False, sheet_name='Extracted Data')
        
    output.seek(0)
    
    response = StreamingResponse(output, 
                                 media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=export.xlsx"
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
