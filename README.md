# 🧠 PDF Semantic Section Extractor Pipeline

A full-stack microservice pipeline for intelligent scientific document parsing. Converts PDFs into structured, semantically rich JSON using GROBID for structure parsing, a custom FastAPI service for section segmentation, and LLMSherpa + Docling for extracting tables, summaries, and semantic annotations.

---
<img width="1448" height="680" alt="Screenshot 2025-07-19 at 2 29 58 PM" src="https://github.com/user-attachments/assets/c2df2f64-d779-4d43-aa6c-765635c3995b" />


## 🧭 Architecture Overview

```
         PDF File
             ↓
       [GROBID Container]
     → Structured TEI XML
             ↓
  [Section Extractor (FastAPI)]
     → Cleaned Sections (JSON)
             ↓
 [Table Extractor (Built-in)]
     → Tables, Sections, Methods
             ↓
   Final Enriched JSON Output
```

---

## ⚙️ Services and Ports

| Service            | Description                                                              | Port   |
|--------------------|--------------------------------------------------------------------------|--------|
| `grobid`           | Parses PDF and outputs TEI XML                                            | 8070   |
| `section-extractor`| FastAPI app that segments TEI XML into high-level sections                | 8000   |
| `llmsherpa`        | Flask app that handles LLM-based summarization and table extraction       | 5001   |
| `docling`          | Document interaction and table-based pipeline controller                  | 5010   |

---

## 🚀 Getting Started

1. **Clone the repo**:

```bash
git clone <repo-url>
cd <repo-name>
```

2. **Start services with Docker Compose**:

```bash
docker-compose up --build
```

Ensure Docker is allocated at least **4–6GB RAM**, as GROBID and LLMs can be memory-intensive.

---

## 🔌 API Endpoints

### 1. Extract Document Sections

```bash
curl -X POST "http://localhost:8000/extract_all" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/file.pdf"
```

### 2. Trigger LLM-Based Table/Summary Extraction

```bash
curl -X POST "http://localhost:5010/api/parseDocument?renderFormat=all" \
  -H "accept: application/json" \
  -F "file=@path/to/your/file.pdf"
```

---

## 🧪 Troubleshooting

| Problem                                  | Solution                                                                 |
|------------------------------------------|--------------------------------------------------------------------------|
| `grobid` not starting                     | Make sure port 8070 is free and enough RAM is allocated in Docker        |
| `llmsherpa` shows `could not convert string to float: '¾'` | Check for fractional unicode chars and patch with `safe_float_conversion` |
| Missing output or broken JSON            | Check logs from all containers: `docker-compose logs -f`                 |
| UI not loading at port 5010              | Confirm `docling` container is healthy and `.env` has correct URL        |

---

## 🧱 Directory Structure

```
.
grobid_methods/
├── Dockerfile
├── README.md
├── docker-compose.yml
├── llmsherpa_output.json
├── requirements.txt
├── app/
│   ├── grobid_client.py
│   ├── main.py
│   ├── models.py
│   ├── outputs/
│   ├── utils/
│   │   ├── logger.py
│   │   ├── semantic_utils.py
│   │   ├── tei_helpers.py
│   ├── extractors/
│   │   ├── methods_extractor.py
│   │   ├── table_extractor.py
│   │   ├── section_extractor.py
│   ├── routes/
│   │   ├── extract_all.py
│   │   ├── extract_methods.py
│   │   ├── extract_sections.py
│   │   ├── extract_tables.py
│   └── static/
│       └── index.html
└── .venv/
```

---

## 🔍 Example Output

```json
{
  "filename": "example_paper.pdf",
  "tei_xml": "<TEI>...</TEI>",
  "extracted_sections": {
    "title": {
      "heading": "A Study on Protein Folding",
      "content": "A Study on Protein Folding"
    },
    "abstract": {
      "heading": "Abstract",
      "content": [
        "Protein folding is a fundamental process in molecular biology...",
        "This study explores the mechanisms and influencing factors..."
      ]
    },
    "methods": {
      "heading": "Materials and Methods",
      "content": [
        "## Sample Preparation",
        "Proteins were purified using affinity chromatography...",
        "## Experimental Setup",
        "All experiments were conducted at room temperature...",
        "## Data Analysis",
        "Statistical analysis was performed using Python and R."
      ],
      "metadata": {
        "similarity_score": 0.98,
        "subheadings": [
          "Sample Preparation",
          "Experimental Setup",
          "Data Analysis"
        ]
      }
    },
    "results": {
      "heading": "Results",
      "content": [
        "The folding rates increased with temperature...",
        "A significant difference was observed between wild-type and mutant proteins."
      ]
    },
    "discussion": {
      "heading": "Discussion",
      "content": [
        "Our findings suggest a new pathway for protein folding...",
        "Further research is needed to validate these results."
      ]
    }
  }
}
```

---

## 📚 Technologies Used

- **Python** – FastAPI & Flask for service APIs
- **Docker** – container orchestration
- **GROBID** – for scientific PDF parsing
- **LLMSherpa** – LLM wrapper for semantic processing
- **Docling** – UI + microservice orchestration

---

## 🧠 Lessons Learned

- Concurrency issues were resolved by managing thread pools and limiting LLM calls per request.
- A critical production bug involved `string to float` conversion due to Unicode fractions like `'¾'`; handled via a sanitization function.
- Logs across containers were unified for easier debugging.

---

## 🪪 License

MIT License — fork and adapt as needed.

---

## 🙌 Acknowledgements

- GROBID for powerful PDF parsing
- Open-source LLM frameworks
- FastAPI and Flask communities
