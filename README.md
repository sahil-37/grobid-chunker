# PDF Section Extractor

A tool for extracting sections from PDF documents using GROBID for PDF parsing and custom logic for section identification.

## Prerequisites

- Docker
- Docker Compose

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Start the services:
```bash
docker-compose up --build
```

This will start:
- GROBID service on port 8070
- Section Extractor API on port 8000

## Usage

### API Endpoints

1. Extract sections from a PDF:
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/file.pdf"
```

2. Extract all sections from a PDF:
```bash
curl -X POST "http://localhost:8000/extract_all" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/file.pdf"
```

### Response Format

The API returns JSON with the following structure:

```json
{
  "sections": [
    {
      "title": "Section Title",
      "content": "Section content...",
      "start_page": 1,
      "end_page": 2
    }
  ]
}
```

## Development

The project structure:
```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── methods_extractor.py # Section extraction logic
│   └── utils.py            # Utility functions
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Troubleshooting

1. If GROBID fails to start:
   - Check if port 8070 is available
   - Ensure you have enough memory allocated to Docker

2. If the section extractor fails:
   - Check the logs: `docker-compose logs section-extractor`
   - Verify the PDF file is not corrupted
   - Ensure the PDF has proper section headers

## License

[Your License]
