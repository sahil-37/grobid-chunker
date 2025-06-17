from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import json
from datetime import datetime

from app.grobid_client import send_to_grobid
from app.extractors.methods_extractor import extract_methods_with_subsections
from app.extractors.section_extractor import extract_structured_sections
from app.extractors.table_extractor import extract_tables_from_bytes  # NEW

router = APIRouter(prefix="/extract-all", tags=["Extract All"])


@router.post("/")
async def extract_all_sections(files: List[UploadFile] = File(...)):
    responses = []
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    for up in files:
        pdf_bytes = await up.read()
        xml_str = send_to_grobid(pdf_bytes)

        if not xml_str:
            responses.append({"filename": up.filename, "error": "Failed to parse with GROBID"})
            continue

        methods, score, methods_heading, _ = extract_methods_with_subsections(xml_str)
        sections = extract_structured_sections(xml_str)

        # Inject methods into TEI-derived sections
        sections["methods"] = {
            "heading": methods_heading or "Methods",
            "similarity_score": round(score, 3),
            "content": methods
        }

        # Extract tables independently
        tables = extract_tables_from_bytes(pdf_bytes)

        # Construct final output object (not just `sections`)
        output = {
            "filename": up.filename,
            "tei_xml": xml_str,
            "extracted_sections": sections,
            "tables": tables
        }

        # Save JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_safe = up.filename.replace(" ", "_").replace("/", "_")
        json_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_all.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # Save TXT (human-readable)
        txt_path = os.path.join(output_dir, f"{filename_safe}_{timestamp}_all.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            for key, sec in sections.items():
                f.write(f"### {sec.get('heading', key).upper()}\n\n")

                if key == "methods":
                    for sub, paras in sec.get("content", {}).items():
                        f.write(f"#### {sub}\n")
                        for para in paras:
                            f.write(para + "\n\n")

                elif key == "results_discussion":
                    for subsec in sec.get("subsections", []):
                        f.write(f"#### {subsec['subheading']}\n")
                        for para in subsec["content"]:
                            f.write(para + "\n\n")

                elif isinstance(sec.get("content"), list):
                    for para in sec.get("content", []):
                        f.write(para + "\n\n")
                else:
                    f.write(sec.get("content", "") + "\n\n")

            # Write tables separately at the end
            if tables:
                f.write("\n### TABLES\n\n")
                for tbl in tables:
                    f.write(f"#### TABLE {tbl['table_index']}: {tbl.get('caption','')}\n")
                    for row in tbl["rows"]:
                        f.write(" | ".join(row) + "\n")
                    if tbl.get("footnotes"):
                        f.write("\n*Footnotes:* " + " ".join(tbl["footnotes"]) + "\n")
                    f.write("\n")

        # Add to response
        responses.append(output)

    return responses
