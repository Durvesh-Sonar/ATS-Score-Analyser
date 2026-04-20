import re
from collections import Counter

# Common ATS keywords by category
ATS_KEYWORDS = {
    'technical_skills': [
        'python', 'javascript', 'java', 'c++', 'html', 'css', 'sql', 'react', 
        'angular', 'vue', 'flask', 'django', 'node', 'express', 'mongodb', 
        'mysql', 'postgresql', 'git', 'docker', 'kubernetes', 'aws', 'azure',
        'machine learning', 'data analysis', 'artificial intelligence', 'ai',
        'algorithms', 'data structures', 'api', 'rest', 'microservices'
    ],
    'soft_skills': [
        'communication', 'leadership', 'teamwork', 'problem solving', 
        'critical thinking', 'time management', 'adaptability', 'creativity',
        'collaboration', 'project management', 'analytical', 'detail oriented'
    ],
    'experience': [
        'experience', 'years', 'developed', 'implemented', 'managed', 'led',
        'created', 'designed', 'optimized', 'improved', 'achieved', 'delivered',
        'bachelor', 'master', 'degree', 'certification', 'agile', 'scrum'
    ],
    'job_roles': [
        'software developer', 'data scientist', 'web developer', 'frontend developer',
        'backend developer', 'full stack developer', 'devops engineer', 
        'software engineer', 'data analyst', 'product manager', 'ui designer',
        'ux designer', 'quality assurance', 'database administrator'
    ]
}

def extract_keywords_from_text(text):
    """Extract keywords from text"""
    text_lower = text.lower()
    found_keywords = []
    
    for category, keywords in ATS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_keywords.append((keyword, category))
    
    return found_keywords

def calculate_ats_score(resume_text, job_description):
    """Calculate ATS score based on keyword matching"""
    resume_keywords = set([kw[0] for kw in extract_keywords_from_text(resume_text)])
    job_keywords = set([kw[0] for kw in extract_keywords_from_text(job_description)])
    
    if not job_keywords:
        return {
            'score': 0,
            'total_keywords': 0,
            'matched_keywords': [],
            'missing_keywords': [],
            'recommendations': ['No keywords found in job description']
        }
    
    matched_keywords = resume_keywords.intersection(job_keywords)
    missing_keywords = job_keywords - resume_keywords
    
    score = (len(matched_keywords) / len(job_keywords)) * 100
    
    # Generate recommendations
    recommendations = generate_recommendations(score, missing_keywords)
    
    return {
        'score': round(score, 1),
        'total_keywords': len(job_keywords),
        'matched_keywords': list(matched_keywords),
        'missing_keywords': list(missing_keywords),
        'recommendations': recommendations
    }

def generate_recommendations(score, missing_keywords):
    """Generate recommendations based on ATS score"""
    recommendations = []
    
    if score < 30:
        recommendations.append("Your resume needs significant improvement for ATS compatibility")
        recommendations.append("Consider adding more relevant keywords from the job description")
    elif score < 50:
        recommendations.append("Your resume has moderate ATS compatibility")
        recommendations.append("Add more technical skills and experience keywords")
    elif score < 70:
        recommendations.append("Good ATS compatibility! Consider minor improvements")
    else:
        recommendations.append("Excellent ATS compatibility!")
    
    # Specific recommendations based on missing keywords
    if missing_keywords:
        tech_missing = [kw for kw in missing_keywords if kw in ATS_KEYWORDS['technical_skills']]
        soft_missing = [kw for kw in missing_keywords if kw in ATS_KEYWORDS['soft_skills']]
        
        if tech_missing and len(tech_missing) > 3:
            recommendations.append(f"Consider adding technical skills: {', '.join(tech_missing[:3])}")
        
        if soft_missing and len(soft_missing) > 2:
            recommendations.append(f"Consider highlighting soft skills: {', '.join(soft_missing[:2])}")
    
    return recommendations

def suggest_job_roles(resume_text):
    """Suggest suitable job roles based on resume content"""
    resume_keywords = [kw[0] for kw in extract_keywords_from_text(resume_text)]
    keyword_counts = Counter(resume_keywords)
    
    role_scores = {}
    
    # Define role-specific keyword weights
    role_keywords = {
        'Software Developer': ['python', 'java', 'javascript', 'programming', 'software', 'development', 'coding'],
        'Data Scientist': ['python', 'machine learning', 'data analysis', 'statistics', 'ai', 'algorithms'],
        'Web Developer': ['html', 'css', 'javascript', 'react', 'angular', 'web', 'frontend', 'backend'],
        'DevOps Engineer': ['docker', 'kubernetes', 'aws', 'azure', 'ci/cd', 'infrastructure', 'automation'],
        'Data Analyst': ['sql', 'data analysis', 'excel', 'visualization', 'statistics', 'reporting'],
        'Product Manager': ['product management', 'agile', 'scrum', 'leadership', 'strategy', 'communication'],
        'UI/UX Designer': ['design', 'ui', 'ux', 'user experience', 'figma', 'adobe', 'prototyping']
    }
    
    for role, keywords in role_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in resume_keywords:
                score += keyword_counts.get(keyword, 0)
        role_scores[role] = score
    
    # Sort roles by score and return top 3
    sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
    
    suggestions = []
    for role, score in sorted_roles[:3]:
        if score > 0:
            suggestions.append({
                'role': role,
                'match_score': min(100, (score / 5) * 100),  # Normalize to percentage
                'confidence': 'High' if score >= 3 else 'Medium' if score >= 1 else 'Low'
            })
    
    return suggestions if suggestions else [{'role': 'General Software Role', 'match_score': 0, 'confidence': 'Low'}]