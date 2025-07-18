# app/routes/extract_tables.py
from fastapi import APIRouter, UploadFile, File
from typing import List, Dict, Any
import os, json
from datetime import datetime


from app.extractors.table_extractor import extract_tables_from_bytes

router = APIRouter(prefix="/extract-tables", tags=["Extract Tables"])


@router.post("/")
async def extract_tables(files: List[UploadFile] = File(...)) -> List[Dict[str, Any]]:
    """
    Upload one or more PDFs and receive their tables.
    The heavy Docling pass is skipped entirely for PDFs without tables.
    """
    responses = []
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)

    for up in files:
        pdf_bytes = await up.read()
        tables = extract_tables_from_bytes(pdf_bytes)  # <-- uses new logic

        # Persist results (optional; mirrors other routes)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = up.filename.replace(" ", "_").replace("/", "_")

        json_path = os.path.join(output_dir, f"{safe_name}_{timestamp}_tables.json")
        with open(json_path, "w", encoding="utf-8") as fp:
            json.dump(tables, fp, indent=2, ensure_ascii=False)

        txt_path = os.path.join(output_dir, f"{safe_name}_{timestamp}_tables.txt")
        with open(txt_path, "w", encoding="utf-8") as fp:
            for tbl in tables:
                caption = tbl.get("caption") or ""
                fp.write(f"### TABLE {tbl['table_index']}: {caption}\n")
                for row in tbl["rows"]:
                    fp.write(" | ".join(row) + "\n")
                if tbl.get("footnotes"):
                    fp.write("\n*Footnotes:* " + " ".join(tbl["footnotes"]) + "\n")
                fp.write("\n")

        responses.append({"filename": up.filename, "tables": tables})

    return responses
