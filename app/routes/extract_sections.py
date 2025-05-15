from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import json
from datetime import datetime

from app.grobid_client import send_to_grobid
from app.extractors.section_extractor import extract_structured_sections

router = APIRouter()

@router.post("/extract-sections")
async def extract_sections_api(files: List[UploadFile] = File(...)):
    responses = []
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    for up in files:
        pdf_bytes = await up.read()
        xml_str = send_to_grobid(pdf_bytes)

        if not xml_str:
            responses.append({"filename": up.filename, "error": "Failed to parse with GROBID"})
            continue

        sections = extract_structured_sections(xml_str)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_safe = up.filename.replace(" ", "_").replace("/", "_")
        save_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_sections.json")

        with open(save_path, "w") as f:
            json.dump(sections, f, indent=2)

        txt_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_sections.txt")
        with open(txt_path, "w") as f:
            for key, sec in sections.items():
                f.write(f"### {sec.get('heading', key).upper()}\n")
                content = sec.get("content", [])
                if isinstance(content, list):
                    for para in content:
                        f.write(para + "\n\n")
                elif isinstance(content, str):
                    f.write(content + "\n\n")

        responses.append({
            "filename": up.filename,
            "tei_xml": xml_str,
            "extracted_sections": sections
        })

    return responses
