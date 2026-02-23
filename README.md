# Offer Letter Data Extractor

A production-ready web application to bulk extract structured data from Offer Letters (DOCX & PDF).

## Features
- **Batch Processing**: Upload 20-100 files at once.
- **Format Support**: Native DOCX and text-based PDF parsing.
- **Smart Extraction**: Hybrid anchor-based + Regex logic.
- **Export**: Download results as CSV or Excel.
- **Privacy**: In-memory processing, no permanent storage.

## Tech Stack
- **Backend**: FastAPI, Python 3.11, PyMuPDF, python-docx, Pandas.
- **Frontend**: React (Vite), Tailwind CSS, Framer Motion.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (or the port shown in terminal).

## Deployment
See `deployment_guide.md`.
