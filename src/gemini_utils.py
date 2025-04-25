import os
import google.generativeai as genai
from google.genai import types

# Configure Gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def analyze_audio(audio_file_path, question):
    """
    Analyzes an audio interview response using Gemini API
    
    Args:
        audio_file_path: Path to the audio file
        question: The interview question text
        
    Returns:
        dict: Analysis results with evaluation, strengths, improvements, and rating
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Upload audio file to Gemini
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
        
        myfile = genai.upload_file(data=audio_bytes, mime_type='audio/webm')
        
        # Generate feedback
        prompt = f"""
        You are an expert IT interviewer evaluating a candidate's response. 
        
        The question was: "{question}"
        
        Listen to the candidate's answer and provide the following:
        1. A comprehensive evaluation (2-3 paragraphs)
        2. Strengths of the answer (bullet points)
        3. Areas for improvement (bullet points)
        4. A rating from 1.0 to 5.0 where:
           - 1.0: Poor, incorrect or irrelevant answer
           - 2.0: Basic understanding but significant gaps
           - 3.0: Adequate answer with some missing elements
           - 4.0: Good answer with minor improvements needed
           - 5.0: Excellent, comprehensive answer
        
        Format your response as:
        EVALUATION: Your evaluation here
        STRENGTHS: 
        - Strength 1
        - Strength 2
        IMPROVEMENTS:
        - Improvement 1
        - Improvement 2
        RATING: X.X
        """
        
        response = model.generate_content([prompt, myfile])
        feedback_text = response.text
        
        # Parse the sections
        sections = {}
        current_section = None
        content = []
        
        for line in feedback_text.split('\n'):
            if line.startswith('EVALUATION:'):
                current_section = 'evaluation'
                content = [line.replace('EVALUATION:', '').strip()]
            elif line.startswith('STRENGTHS:'):
                sections['evaluation'] = '\n'.join(content) if current_section == 'evaluation' else ''
                current_section = 'strengths'
                content = []
            elif line.startswith('IMPROVEMENTS:'):
                sections['strengths'] = '\n'.join(content) if current_section == 'strengths' else ''
                current_section = 'improvements'
                content = []
            elif line.startswith('RATING:'):
                sections['improvements'] = '\n'.join(content) if current_section == 'improvements' else ''
                try:
                    sections['rating'] = float(line.replace('RATING:', '').strip())
                except ValueError:
                    sections['rating'] = 3.0  # Default rating
                current_section = None
            elif line.strip() and current_section:
                content.append(line.strip())
        
        return {
            'evaluation': sections.get('evaluation', ''),
            'strengths': sections.get('strengths', ''),
            'improvements': sections.get('improvements', ''),
            'rating': sections.get('rating', 3.0),
            'raw_feedback': feedback_text
        }
        
    except Exception as e:
        print(f"Error analyzing audio: {str(e)}")
        return {
            'evaluation': 'Error analyzing response',
            'strengths': '',
            'improvements': '',
            'rating': 3.0,
            'raw_feedback': f'Error: {str(e)}'
        }

def analyze_cv(cv_file_path):
    """
    Analyzes a CV/resume using Gemini API
    
    Args:
        cv_file_path: Path to the CV PDF file
        
    Returns:
        dict: Analysis results with content, strengths, weaknesses, improvements, etc.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Upload PDF file to Gemini
        with open(cv_file_path, 'rb') as f:
            pdf_bytes = f.read()
        
        myfile = genai.upload_file(data=pdf_bytes, mime_type='application/pdf')
        
        # Generate review
        prompt = """
        You are an expert CV/resume reviewer for IT professionals. 
        
        Review the attached CV and provide the following:
        1. Overall assessment (2-3 paragraphs)
        2. Strengths of the CV (bullet points)
        3. Weaknesses of the CV (bullet points)
        4. Suggested improvements (bullet points)
        5. Lacking sections (bullet points)
        6. Notable benefits/qualifications (bullet points)
        
        Format your response exactly as:
        OVERALL_REVIEW: Your assessment here
        STRENGTHS:
        - Strength 1
        - Strength 2
        WEAKNESSES:
        - Weakness 1
        - Weakness 2
        IMPROVEMENTS:
        - Improvement 1
        - Improvement 2
        LACKING_SECTIONS:
        - Section 1
        - Section 2
        BENEFITS:
        - Benefit 1
        - Benefit 2
        """
        
        response = model.generate_content([prompt, myfile])
        review_text = response.text
        
        # Parse sections
        sections = {}
        current_section = None
        content = []
        
        for line in review_text.split('\n'):
            if line.startswith('OVERALL_REVIEW:'):
                current_section = 'content'
                content = [line.replace('OVERALL_REVIEW:', '').strip()]
            elif line.startswith('STRENGTHS:'):
                sections['content'] = '\n'.join(content) if current_section == 'content' else ''
                current_section = 'strengths'
                content = []
            elif line.startswith('WEAKNESSES:'):
                sections['strengths'] = '\n'.join(content) if current_section == 'strengths' else ''
                current_section = 'weaknesses'
                content = []
            elif line.startswith('IMPROVEMENTS:'):
                sections['weaknesses'] = '\n'.join(content) if current_section == 'weaknesses' else ''
                current_section = 'improvements'
                content = []
            elif line.startswith('LACKING_SECTIONS:'):
                sections['improvements'] = '\n'.join(content) if current_section == 'improvements' else ''
                current_section = 'lacking_sections'
                content = []
            elif line.startswith('BENEFITS:'):
                sections['lacking_sections'] = '\n'.join(content) if current_section == 'lacking_sections' else ''
                current_section = 'benefits'
                content = []
            elif line.strip() and current_section:
                content.append(line.strip())
        
        if current_section:
            sections[current_section] = '\n'.join(content)
        
        return {
            'content': sections.get('content', ''),
            'strengths': sections.get('strengths', ''),
            'weaknesses': sections.get('weaknesses', ''),
            'improvements': sections.get('improvements', ''),
            'lacking_sections': sections.get('lacking_sections', ''),
            'benefits': sections.get('benefits', ''),
            'raw_review': review_text
        }
        
    except Exception as e:
        print(f"Error analyzing CV: {str(e)}")
        return {
            'content': f'Error analyzing CV: {str(e)}',
            'strengths': '',
            'weaknesses': '',
            'improvements': '',
            'lacking_sections': '',
            'benefits': '',
            'raw_review': f'Error: {str(e)}'
        }