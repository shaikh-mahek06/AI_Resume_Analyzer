import pdfplumber

def extract_text_from_pdf(uploaded_file):
    if uploaded_file is None:
        return ""

    text = ""

    try:
        uploaded_file.seek(0)
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        return ""

    return text
