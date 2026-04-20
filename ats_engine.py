import re
from sentence_transformers import SentenceTransformer, util

# Load AI model (runs only once)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Job roles
JOB_ROLES = [
    "Software Engineer",
    "Data Analyst",
    "Machine Learning Engineer",
    "Embedded Systems Engineer",
    "Electronics Engineer"
]

# Skills list
SKILLS_DB = [
    "python", "c++", "java", "machine learning",
    "deep learning", "opencv", "sql",
    "arduino", "esp32", "iot", "embedded systems"
]

# -----------------------
# CLEAN TEXT
# -----------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    return text


# -----------------------
# SKILL EXTRACTION
# -----------------------
def extract_skills(text):
    return [skill for skill in SKILLS_DB if skill in text]


# -----------------------
# SECTION SCORE
# -----------------------
def section_score(text):
    sections = ["skills", "experience", "education", "projects"]
    count = 0
    for sec in sections:
        if sec in text:
            count += 1
    return count / len(sections)


# -----------------------
# FORMAT SCORE
# -----------------------
def format_score(text):
    bullets = text.count("-") + text.count("•")
    return min(bullets / 20, 1)


# -----------------------
# SEMANTIC SCORE (MAIN AI)
# -----------------------
def semantic_score(resume, job):
    # Split into smaller chunks (sentences)
    resume_chunks = resume.split('.')
    job_chunks = job.split('.')

    resume_chunks = [r.strip() for r in resume_chunks if len(r.strip()) > 20]
    job_chunks = [j.strip() for j in job_chunks if len(j.strip()) > 20]

    if not resume_chunks or not job_chunks:
        return 0

    # Encode all chunks
    resume_emb = model.encode(resume_chunks, convert_to_tensor=True)
    job_emb = model.encode(job_chunks, convert_to_tensor=True)

    # Compute similarity matrix
    similarity_matrix = util.cos_sim(job_emb, resume_emb)

    # For each job sentence → take best matching resume sentence
    max_scores = similarity_matrix.max(dim=1).values

    # Average score
    score = max_scores.mean().item()

    # Normalize to 0–1 range
    score = max(0, min(1, score))

    return score


# -----------------------
# FINAL ATS SCORE
# -----------------------
def calculate_ats_score(resume_text, job_desc):
    resume_text = clean_text(resume_text)
    job_desc = clean_text(job_desc)

    # Convert to sets (unique words)
    resume_words = set(resume_text.split())
    job_words = set(job_desc.split())

    # Remove very common words (basic stopwords)
    stopwords = {"the", "and", "is", "in", "to", "of", "a", "for", "on"}
    job_words = job_words - stopwords

    # Keyword match score
    matched_keywords = resume_words.intersection(job_words)
    keyword_score = len(matched_keywords) / len(job_words) if job_words else 0

    # Semantic similarity (make sure it's between 0–1)
    sem_score = semantic_score(resume_text, job_desc)
    sem_score = max(0, min(1, sem_score))  # clamp

    # Section + format scores (assumed 0–1)
    sec_score = max(0, min(1, section_score(resume_text)))
    fmt_score = max(0, min(1, format_score(resume_text)))

    # Weighted final score
    final = (
        0.35 * keyword_score +
        0.40 * sem_score +
        0.15 * sec_score +
        0.10 * fmt_score
    )

    return round(final * 100, 2)


# -----------------------
# JOB SUGGESTION
# -----------------------
def recommend_jobs(resume_text):
    resume_text = clean_text(resume_text)
    resume_emb = model.encode(resume_text, convert_to_tensor=True)

    scores = []
    for job in JOB_ROLES:
        job_emb = model.encode(job, convert_to_tensor=True)
        sim = util.cos_sim(resume_emb, job_emb).item()
        scores.append((job, sim))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [job for job, _ in scores[:3]]