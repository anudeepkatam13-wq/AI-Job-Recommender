import streamlit as st
import sys
import os

# ✅ Fix for Streamlit Cloud (add src to path FIRST)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# ✅ Import AFTER fixing path
from helper import extract_text_from_pdf, ask_openai
from job_api import fetch_linkedin_jobs, fetch_naukri_jobs


# ------------------ UI CONFIG ------------------
st.set_page_config(page_title="Job Recommender", layout="wide")

st.title("📄 AI Job Recommender")
st.markdown(
    "Upload your resume and get job recommendations based on your skills and experience from LinkedIn and Naukri."
)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])


# ------------------ MAIN FLOW ------------------
if uploaded_file:

    # Extract Resume
    with st.spinner("Extracting text from your resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_text = resume_text[:8000]  # prevent token overflow

    # ------------------ SUMMARY ------------------
    try:
        with st.spinner("Summarizing your resume..."):
            summary = ask_openai(
                f"Summarize this resume highlighting the skills, education, and experience:\n\n{resume_text}",
                max_tokens=500
            )
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        st.stop()

    # ------------------ SKILL GAPS ------------------
    try:
        with st.spinner("Finding skill gaps..."):
            gaps = ask_openai(
                f"Analyze this resume and highlight missing skills, certifications, and experiences needed for better job opportunities:\n\n{resume_text}",
                max_tokens=400
            )
    except Exception as e:
        st.error(f"Error analyzing gaps: {e}")
        st.stop()

    # ------------------ ROADMAP ------------------
    try:
        with st.spinner("Creating future roadmap..."):
            roadmap = ask_openai(
                f"Based on this resume, suggest a future roadmap to improve career prospects (skills to learn, certifications, industry exposure):\n\n{resume_text}",
                max_tokens=400
            )
    except Exception as e:
        st.error(f"Error generating roadmap: {e}")
        st.stop()

    # ------------------ DISPLAY ------------------
    st.markdown("---")
    st.header("📑 Resume Summary")
    st.info(summary)

    st.markdown("---")
    st.header("🛠️ Skill Gaps & Missing Areas")
    st.warning(gaps)

    st.markdown("---")
    st.header("🚀 Future Roadmap & Preparation Strategy")
    st.success(roadmap)

    st.success("✅ Analysis Completed Successfully!")

    # ------------------ JOB SEARCH ------------------
    if st.button("🔎 Get Job Recommendations"):

        try:
            with st.spinner("Extracting job keywords..."):
                keywords = ask_openai(
                    f"Based on this resume summary, suggest the best job titles and keywords for searching jobs. Give a comma-separated list only.\n\nSummary: {summary}",
                    max_tokens=100
                )

                search_keywords_clean = keywords.replace("\n", "").strip()
                search_keywords_clean = ", ".join(
                    [k.strip() for k in search_keywords_clean.split(",")]
                )

        except Exception as e:
            st.error(f"Error extracting keywords: {e}")
            st.stop()

        st.success(f"Extracted Job Keywords: {search_keywords_clean}")

        # ------------------ FETCH JOBS ------------------
        with st.spinner("Fetching jobs (this may take a few seconds)..."):
            try:
                linkedin_jobs = fetch_linkedin_jobs(search_keywords_clean, rows=60)
                naukri_jobs = fetch_naukri_jobs(search_keywords_clean, rows=60)
            except Exception as e:
                st.error(f"Error fetching jobs: {e}")
                st.stop()

        # ------------------ LINKEDIN ------------------
        st.markdown("---")
        st.header("💼 Top LinkedIn Jobs")

        if linkedin_jobs:
            for job in linkedin_jobs:
                st.markdown(
                    f"**{job.get('title', 'N/A')}** at *{job.get('companyName', 'N/A')}*"
                )
                st.markdown(f"- 📍 {job.get('location', 'N/A')}")
                st.markdown(f"- 🔗 [View Job]({job.get('link', '#')})")
                st.markdown("---")
        else:
            st.warning("No LinkedIn jobs found.")

        # ------------------ NAUKRI ------------------
        st.markdown("---")
        st.header("💼 Top Naukri Jobs (India)")

        if naukri_jobs:
            for job in naukri_jobs:
                st.markdown(
                    f"**{job.get('title', 'N/A')}** at *{job.get('companyName', 'N/A')}*"
                )
                st.markdown(f"- 📍 {job.get('location', 'N/A')}")
                st.markdown(f"- 🔗 [View Job]({job.get('url', '#')})")
                st.markdown("---")
        else:
            st.warning("No Naukri jobs found.")
