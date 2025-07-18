# app/routers/extract_all.py

from fastapi import APIRouter, UploadFile, File
from typing import List
import os
import json
from datetime import datetime
import asyncio

from app.grobid_client import send_to_grobid_async
from app.extractors.methods_extractor import extract_methods_with_subsections
from app.extractors.section_extractor import extract_structured_sections
from app.extractors.table_extractor import extract_tables_from_bytes

from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/extract-all", tags=["Extract All"])

# Limit to 1 concurrent GROBID request (sequential processing)
grobid_semaphore = asyncio.Semaphore(1)

async def send_to_grobid_with_retries(pdf_bytes, retries=3, delay=10):
    for attempt in range(retries):
        try:
            async with grobid_semaphore:
                return await send_to_grobid_async(pdf_bytes)
        except Exception as e:
            logger.warning(f"Retry {attempt + 1}/{retries} after error: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

async def process_file(up: UploadFile, output_dir: str, error_log_path: str):
    filename = up.filename
    try:
        logger.info(f"📥 Processing file: {filename}")
        pdf_bytes = await up.read()

        logger.info("🚀 Sending PDF to GROBID...")
        xml_str = await send_to_grobid_with_retries(pdf_bytes)

        if not xml_str or "<TEI" not in xml_str:
            logger.warning("⚠️ GROBID returned empty or invalid TEI XML.")
            raise ValueError("Empty or invalid TEI XML returned.")

        logger.info("✅ GROBID response received")
        logger.info("🧪 Extracting methods section...")
        methods, score, methods_heading, _ = extract_methods_with_subsections(xml_str)

        logger.info("🧬 Extracting structured sections...")
        sections = extract_structured_sections(xml_str)
        sections["methods"] = {
            "heading": methods_heading or "Methods",
            "similarity_score": round(score, 3),
            "content": methods
        }

        try:
            logger.info("📊 Extracting tables...")
            tables = extract_tables_from_bytes(pdf_bytes)
        except Exception as te:
            logger.warning(f"⚠️ Table extraction failed for {filename}: {te}")
            tables = []

        output = {
            "filename": filename,
            "tei_xml": xml_str,
            "extracted_sections": sections,
            "tables": tables
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = filename.replace(" ", "_").replace("/", "_")
        json_path = os.path.join(output_dir, f"{safe_name}_{timestamp}_all.json")
        txt_path = os.path.join(output_dir, f"{safe_name}_{timestamp}_all.txt")

        try:
            with open(json_path, "w", encoding="utf-8") as f_json:
                json.dump(output, f_json, indent=2, ensure_ascii=False)
            logger.info(f"💾 JSON written to: {json_path}")
        except Exception as jf:
            logger.error(f"❌ JSON write failed for {filename}: {jf}")

        try:
            with open(txt_path, "w", encoding="utf-8") as f_txt:
                for key, sec in sections.items():
                    f_txt.write(f"### {sec.get('heading', key).upper()}\n\n")
                    if key == "methods":
                        for sub, paras in sec.get("content", {}).items():
                            f_txt.write(f"#### {sub}\n")
                            for para in paras:
                                f_txt.write(para + "\n\n")
                    elif key == "results_discussion":
                        for subsec in sec.get("subsections", []):
                            f_txt.write(f"#### {subsec['subheading']}\n")
                            for para in subsec["content"]:
                                f_txt.write(para + "\n\n")
                    elif isinstance(sec.get("content"), list):
                        for para in sec.get("content", []):
                            f_txt.write(para + "\n\n")
                    else:
                        f_txt.write(sec.get("content", "") + "\n\n")

                if tables:
                    f_txt.write("\n### TABLES\n\n")
                    for tbl in tables:
                        f_txt.write(f"#### TABLE {tbl['table_index']}: {tbl.get('caption','')}\n")
                        for row in tbl["rows"]:
                            f_txt.write(" | ".join(str(cell) if cell is not None else "" for cell in row) + "\n")
                        if tbl.get("footnotes"):
                            f_txt.write("\n*Footnotes:* " + " ".join(tbl["footnotes"]) + "\n")
                        f_txt.write("\n")
            logger.info(f"📝 TXT written to: {txt_path}")
        except Exception as tf:
            logger.error(f"❌ TXT write failed for {filename}: {tf}")

        return output

    except Exception as e:
        logger.exception(f"❌ Error processing {filename}: {e}")
        with open(error_log_path, "a", encoding="utf-8") as logf:
            logf.write(json.dumps({
                "filename": filename,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }) + "\n")
        return {"filename": filename, "error": str(e)}

@router.post("/")
async def extract_all_sections(files: List[UploadFile] = File(...)):
    output_dir = os.path.join(os.path.dirname(__file__), "..", "outputs")
    os.makedirs(output_dir, exist_ok=True)
    error_log_path = os.path.join(output_dir, "extract_errors.jsonl")

    responses = []
    for up in files:
        result = await process_file(up, output_dir, error_log_path)
        responses.append(result)

    return responses
