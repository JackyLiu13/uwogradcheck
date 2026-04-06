from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os

from backend.validator import ValidatorEngine

app = FastAPI(title="UWO Graduation Checker API")

# Setup validator engine
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
validator = ValidatorEngine(data_dir=data_dir)

class EvaluationRequest(BaseModel):
    module_id: str
    student_courses: List[str]

@app.get("/api/modules")
def get_modules():
    """Returns a simplified list of modules for a search dropdown."""
    modules = []
    for mid, mdata in validator.modules_data.get('modules', {}).items():
        if isinstance(mdata, dict) and "error" not in mdata:
            modules.append({
                "id": mid,
                "name": mdata.get("name"),
                "type": mdata.get("type"),
                "faculty": mdata.get("faculty"),
                "department": mdata.get("department")
            })
    return {"modules": modules}

@app.post("/api/evaluate")
def evaluate_module(request: EvaluationRequest):
    """Evaluates a student's courses against a specific module."""
    if request.module_id not in validator.modules_data.get('modules', {}):
        raise HTTPException(status_code=404, detail="Module not found")
        
    result = validator.evaluate(request.module_id, request.student_courses)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    return result

@app.get("/")
def read_root():
    return {"message": "UWO Graduation Checker API is running. See /docs for Swagger UI."}
