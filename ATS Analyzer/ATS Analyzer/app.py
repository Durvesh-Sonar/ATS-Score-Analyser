from flask import Flask, request, render_template, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from utils.parser import extract_text_from_file
from utils.scorer import calculate_ats_score, suggest_job_roles

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Sample job description for ATS scoring
SAMPLE_JOB_DESCRIPTION = """
We are looking for a Software Developer with experience in Python, JavaScript, React, Flask, 
Django, SQL databases, Git, AWS, Docker, machine learning, data analysis, project management, 
communication skills, problem solving, teamwork, leadership, and agile methodologies.
Requirements include Bachelor's degree in Computer Science, 3+ years of experience in software 
development, knowledge of web technologies, database design, API development, testing, 
debugging, and version control systems. Strong analytical and critical thinking skills required.
Experience with microservices, REST APIs, and cloud platforms preferred.
"""

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Make sure the uploads folder exists"""
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Created upload folder at: {upload_folder}")
    else:
        print(f"Upload folder already exists at: {upload_folder}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                ensure_upload_folder()
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"Attempting to save file at: {filepath}")
                file.save(filepath)
                print(f"File saved successfully at: {filepath}")
                
                # Extract text from the uploaded file
                extracted_text = extract_text_from_file(filepath)
                
                if not extracted_text.strip():
                    flash('Could not extract text from the file. Please ensure it contains readable text.', 'error')
                    return redirect(request.url)
                
                # Calculate ATS score
                ats_score = calculate_ats_score(extracted_text, SAMPLE_JOB_DESCRIPTION)
                
                # Suggest job roles
                suggested_roles = suggest_job_roles(extracted_text)
                
                # Show success message
                flash('Resume analyzed successfully!', 'success')
                
                return render_template('index.html', 
                                       ats_score=ats_score, 
                                       suggested_roles=suggested_roles,
                                       extracted_text=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                                       filename=filename,
                                       filepath=filepath)  # also pass file path to frontend if needed
            
            except Exception as e:
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload PDF or DOCX files only.', 'error')
            return redirect(request.url)
    
    return render_template('index.html')

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    ensure_upload_folder()
    print("Starting ATS Resume Checker...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
