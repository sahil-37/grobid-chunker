from fastapi import APIRouter, UploadFile, File
from typing import List
import os
from datetime import datetime

from app.grobid_client import send_to_grobid_async  # ✅ Use async version
from app.extractors.methods_extractor import extract_methods_with_subsections

router = APIRouter()

@router.post("/extract-methods")
async def extract_methods_api(files: List[UploadFile] = File(...)):
    responses = []
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    for up in files:
        pdf_bytes = await up.read()
        xml_str = await send_to_grobid_async(pdf_bytes)  # ✅ Await the async GROBID call

        if not xml_str:
            responses.append({"filename": up.filename, "error": "Failed to parse with GROBID"})
            continue

        methods, score, matched_heading, fallback_heads = extract_methods_with_subsections(xml_str)
        resp = {
            "filename": up.filename,
            "tei_xml": xml_str,
            "matched_section": matched_heading,
            "similarity_score": round(score, 3),
            "fallback_subsections": fallback_heads
        }

        if methods:
            methods_text = "\n\n".join(methods)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_safe = up.filename.replace(" ", "_").replace("/", "_")
            save_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_methods.txt")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(methods_text)
            resp["methods_section"] = methods_text
        else:
            resp["error"] = "No valid Methods section found."

        responses.append(resp)

    return responses
