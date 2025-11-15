import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        # Try direct text extraction
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"Direct text extraction failed: {e}")
    
    # Fallback to OCR for image-based PDFs
    print("Falling back to OCR for image-based PDF.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")
    return text.strip()

# Function to get response from Gemini AI
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model = genai.GenerativeModel("gemini-2.5-flash")

    base_prompt = f"""
    You are an experienced HR with technical experience in one of these fields:
    Data Science, Data Analyst, DevOps, Machine Learning Engineer, Prompt Engineer, AI Engineer,
    Full Stack Web Development, Big Data Engineering, Marketing Analyst, Human Resource Manager, Software Developer.
    
    Review the provided resume and share a professional evaluation:
    - Does the candidate’s profile align with the role?
    - List the skills they already have.
    - Suggest skills to improve their resume.
    - Recommend courses to strengthen those skills.
    - Highlight the strengths and weaknesses.

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Additionally, compare this resume to the following job description:

        Job Description:
        {job_description}

        Highlight the strengths and weaknesses of the applicant relative to these requirements.
        """

    response = model.generate_content(base_prompt)
    return response.text.strip()

# Streamlit app
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# Title
st.title("🤖 AI Resume Analyzer")
st.write("Upload your resume and compare it with job descriptions using **Google Gemini AI**.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Enter Job Description:", placeholder="Paste the job description here...")

if uploaded_file is not None:
    st.success("✅ Resume uploaded successfully!")
else:
    st.warning("⚠️ Please upload a resume in PDF format before analyzing.")

# Add spacing
st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)

if uploaded_file:
    # Save uploaded file locally for processing
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text from PDF
    resume_text = extract_text_from_pdf("uploaded_resume.pdf")

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing your resume... Please wait."):
            try:
                analysis = analyze_resume(resume_text, job_description)
                st.success("✅ Analysis complete!")
                st.write(analysis)
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <p style='text-align: center; color: #888888;'>
        Powered by <b style='color: #FF4B4B;'>Streamlit</b> 
        & <b style='color: #00BFFF;'>Google Gemini AI</b> | 
        Developed by 
        <a href="https://www.linkedin.com/in/shreyal-pancholi/" target="_blank" style='text-decoration: none; color: #FFFFFF;'>
            <b>Shreyal Pancholi</b>
        </a>
    </p>
    """,
    unsafe_allow_html=True
)






