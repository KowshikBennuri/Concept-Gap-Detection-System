# Concept Gap Detection System

A Streamlit-based education analytics platform for detecting concept gaps in student verbal responses using multi-modal AI. Faculty can upload curriculum materials, generate knowledge base concepts, and students can submit audio explanations to receive comparative mastery feedback.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Notes](#notes)

---

## Project Overview

This project is designed to identify and measure conceptual gaps in student understanding by comparing student speech against ideal answers derived from course material. It combines:

- Speech-to-text transcription (`whisper`)
- AI knowledge extraction from PDFs/PPTX via Gemini
- Semantic similarity scoring with transformer embeddings
- Statistical and research-grade evaluation metrics
- Faculty dashboards for content ingestion and analytics
- Student practice workflows with feedback and scoring

---

## Key Features

- User authentication with Supabase
- Faculty subject creation and knowledge base generation
- Automatic concept extraction from curriculum documents
- Student course enrollment
- Audio-based concept practice and assessment
- Multi-metric scoring:
  - TF-IDF
  - Sentence-transformer similarity (MiniLM, MPNET, RoBERTa)
  - ROUGE
  - BERTScore
- Progress analytics and comparative results

---

## Architecture

- `app.py` — Streamlit frontend controlling login, faculty/student flows, and evaluation logic
- `src/auth_manager.py` — Supabase auth integration and profile registration
- `src/db_manager.py` — Supabase table operations and analytics queries
- `src/kb_generator.py` — Document parsing + Gemini knowledge base generation
- `src/evaluator.py` — Comparative scoring engine
- `src/audio_utils.py` — Whisper-based speech guard and transcript validation
- `src/asr_module.py` — ASR transcription utility
- `src/nlp_processor.py` — NLP cleanup and keyword matching
- `src/similarity_core.py` — semantic similarity helper
- `src/kb_handler.py` — local JSON knowledge base loader for tests

---

## Requirements

Install Python 3.11+ and then:

```bash 
pip install -r requirements.txt 
```

---

## Setup

#### Clone or copy the repo.

- Create and activate a Python virtual environment.
- Install dependencies:

```bash 
python -m venv .venv .\.venv\Scripts\activate pip install -r requirements.txt 
```

- Ensure `ffmpeg` is installed and available on your PATH.

#### Prepare Streamlit secrets in secrets.toml:

```toml 
SUPABASE_URL = *your_supabase_url_here*
SUPABASE_KEY = *your_supabase_key_here*
GEMINI_API_KEY = *your_api_key_here* 
```

#### Configure Supabase with the required tables and policies.

- The project includes 20260809063057_remote_schema.sql for schema reference.

---
## Configuration

Required secrets:

- `SUPABASE_URL` — Supabase project **URL**
- `SUPABASE_KEY` — Supabase service key
- `GEMINI_API_KEY` — Google Gemini **API** key for document parsing

The app expects these secrets in secrets.toml.

---

## Usage

Run the app:

```bash 
streamlit run app.py 
```

#### Faculty Flow - Register or log in as faculty

- Create a subject
- Upload PDFs/PPTX 
- Generate knowledge base concepts 
- View analytics and model comparison results

#### Student Flow - Register or log in as student

- Enroll in available subjects
- Select a concept to practice
- Upload spoken response audio 
- Receive a mastery score and keyword feedback

---

## Project Structure

- app.py — Main application
- requirements.txt — Python dependencies
- knowledge_base.json — Local concept dataset used by tests
- src
    - auth_manager.py
    - db_manager.py
    - evaluator.py
    - audio_utils.py
    - asr_module.py
    - kb_generator.py
    - kb_handler.py
    - nlp_processor.py
    - similarity_core.py
- supabase
  - `migrations/20260809063057_remote_schema.sql`
- test_kb.py — Knowledge-base **JSON** validation
- test_logic.py — Logic and similarity validation

---

## Database Schema

Key tables:

- `profiles` — user names + roles
- `subjects` — courses created by faculty
- `knowledge_base` — extracted concept definitions and keywords
- `enrollments` — student subject enrollment
- `attempts` — student practice attempts and scores

The migration file also includes:

- row-level policies for authenticated access
- foreign keys linking students, concepts, and subjects
- metrics storage for **TF-IDF**, **MPNET**, **RoBERTa**, **ROUGE**, **BERTScore**

---

## Testing

Run the available tests:

```bash 
python test_kb.py python test_logic.py 
```

- test_kb.py validates local concept lookup from knowledge_base.json
- test_logic.py verifies semantic similarity and keyword gap detection

---

## Troubleshooting

- Missing `GEMINI_API_KEY` will break document ingestion.
- Make sure `ffmpeg` is installed for audio handling.
- Whisper model downloads may take time on first run.
- If Supabase auth fails, verify `SUPABASE_URL` and `SUPABASE_KEY`.

---

## Notes

- The system stores temporary files like temp.pdf and temp_audio.wav during ingestion/evaluation.
- Faculty analytics are powered by joined Supabase queries and may require proper table relationships.
- The evaluation engine combines classical **TF-IDF** and transformer-based semantic scoring for richer feedback.