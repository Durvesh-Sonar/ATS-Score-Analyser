from flask import Flask, request, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from utils.parser import extract_text_from_file
from ats_engine import calculate_ats_score, recommend_jobs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# Safer upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'docx'}


# ✅ SAMPLE JOB DESCRIPTION (FIXED)
SAMPLE_JOB_DESCRIPTION = """
We are looking for a Software Engineer with experience in Python, Machine Learning,
Data Structures, APIs, and problem-solving skills.
"""


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ HOME PAGE
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


# ✅ MAIN ANALYSIS ROUTE
@app.route('/analyze', methods=['POST'])
def analyze():

    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(filepath)

            extracted_text = extract_text_from_file(filepath)

            if not extracted_text.strip():
                flash('Could not extract text.', 'error')
                return redirect(url_for('index'))

            # ✅ MAIN LOGIC
            score = calculate_ats_score(extracted_text, SAMPLE_JOB_DESCRIPTION)

            # ✅ FIX: match frontend structure
            ats_score = {
                "score": score,
                "recommendations": [
                    "Add more relevant technical keywords",
                    "Improve project descriptions",
                    "Use measurable achievements",
                    "Ensure proper section formatting"
                ]
            }

            suggested_roles = recommend_jobs(extracted_text)

            # delete file
            if os.path.exists(filepath):
                os.remove(filepath)

            return render_template(
                'index.html',
                ats_score=ats_score,
                suggested_roles=suggested_roles,
                extracted_text=extracted_text[:800],
                filename=filename
            )

        except Exception as e:
            print("ERROR:", e)  # 👈 important for debugging
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))

    else:
        flash('Invalid file type (Only PDF/DOCX)', 'error')
        return redirect(url_for('index'))


@app.errorhandler(413)
def too_large(e):
    flash('File too large (max 16MB)', 'error')
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)