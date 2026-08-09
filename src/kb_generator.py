import pymupdf4llm
import google.generativeai as genai
import json
import streamlit as st

def process_document_to_kb(file_path, subject_name):
    # 1. Verification
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Gemini API Key missing in secrets.toml!")
        return []

    # 2. Configure Gemini
    genai.configure(api_key=api_key)
    
    # 3. Explicitly use Gemini 2.0 Flash
    # This model is optimized for 2026 performance and stable API routing
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 4. Convert PPT/PDF to Markdown
    try:
        md_text = pymupdf4llm.to_markdown(file_path)
    except Exception as e:
        st.error(f"File Reading Error: {e}")
        return []

    # 5. Build the Expert Prompt
    prompt = f"""
    Act as an expert professor in {subject_name}.
    Analyze the lecture material and extract the 3-5 most critical concepts for theoretical concepts and in case of numerical/problem-solving topics, extract it as only one concept.

    Important for numerical/problem-solving topics:
    - Preserve equations/formulas exactly if they appear in the source.
    - Include stepwise solution language in the ideal answer when relevant.
    - Keep technical symbols (like V, I, R, sigma, integral, derivative) when present.

    Return ONLY a valid JSON list. Each object must have:
    - "concept_name": short title
    - "ideal_answer": 3-5 sentence explanation that can guide scoring of student verbal answers, including formula context where needed
    - "keywords": exactly 7 key terms, and include formula tokens/units when numericals are involved

    Material:
    {md_text[:9000]}
    """
    
    try:
        # Generate Content
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Near-zero temperature for strict JSON output
                response_mime_type="application/json" # Forces the model to output JSON
            )
        )
        
        # 6. Parse JSON directly
        # Modern Gemini models with 'application/json' mime-type return clean strings
        return json.loads(response.text)
        
    except Exception as e:
        st.error(f"AI Generation Error: {e}")
        return []