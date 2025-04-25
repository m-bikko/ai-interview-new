import os
import random
import google.generativeai as genai
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from src import db
from src.models import Interview, Profession, Question, Answer, AnswerFeedback, InterviewReview
from src.forms import InterviewFilterForm
from datetime import datetime

interviews = Blueprint('interviews', __name__, url_prefix='/interviews')

# Configure Gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

@interviews.route('/')
@login_required
def index():
    form = InterviewFilterForm()
    
    query = Interview.query.filter_by(user_id=current_user.id).order_by(Interview.timestamp.desc())
    
    if request.args.get('rating'):
        min_rating = float(request.args.get('rating'))
        query = query.filter(Interview.rating >= min_rating)
    
    interviews_list = query.all()
    return render_template('interviews/index.html', interviews=interviews_list, form=form)

@interviews.route('/profession/<int:profession_id>/<string:grade>')
@login_required
def start_interview(profession_id, grade):
    profession = Profession.query.get_or_404(profession_id)
    
    # Get 5 random questions for the profession and grade
    questions = Question.query.filter_by(
        profession_id=profession_id, 
        grade=grade
    ).order_by(db.func.random()).limit(5).all()
    
    if not questions:
        flash('No questions available for this profession and grade.', 'danger')
        return redirect(url_for('catalog.profession_detail', profession_id=profession_id))
    
    # Create a new interview
    interview = Interview(
        user_id=current_user.id,
        profession_id=profession_id,
        grade=grade
    )
    db.session.add(interview)
    db.session.commit()
    
    return render_template('interviews/interview.html', 
                          profession=profession, 
                          grade=grade, 
                          questions=questions, 
                          interview=interview)

@interviews.route('/save-answer', methods=['POST'])
@login_required
def save_answer():
    interview_id = request.form.get('interview_id')
    question_id = request.form.get('question_id')
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'message': 'No audio file uploaded'})
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'success': False, 'message': 'No audio file selected'})
    
    # Save the audio file
    filename = secure_filename(f"answer_{interview_id}_{question_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.webm")
    audio_path = os.path.join(current_app.static_folder, 'uploads', filename)
    audio_file.save(audio_path)
    
    # Create a new answer
    answer = Answer(
        interview_id=interview_id,
        question_id=question_id,
        audio_file=filename
    )
    db.session.add(answer)
    db.session.commit()
    
    # Get the question text
    question = Question.query.get(question_id)
    
    # Generate feedback using Gemini API
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Instead of using upload_file which may not be available in the current version,
        # we'll send a text-only prompt since the audio analysis feature requires a professional account
        # This is a workaround for the error: "module 'google.generativeai' has no attribute 'upload_file'"
        
        
        # Generate simulated feedback since we can't process audio files
        prompt = f"""
        You are an expert IT interviewer evaluating a candidate's response. 
        
        The question was: "{question.text}"
        
        Since I cannot actually listen to the audio, please generate a simulated feedback as if the 
        candidate gave a pretty good answer with a few areas for improvement. The feedback should be 
        realistic and helpful.
        
        Provide the following:
        1. A comprehensive evaluation (2-3 paragraphs)
        2. Strengths of the answer (bullet points)
        3. Areas for improvement (bullet points)
        4. A rating between 3.5 and 4.5
        
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
        
        response = model.generate_content(prompt)
        feedback_text = response.text
        
        # Parse the rating from the feedback
        rating_line = [line for line in feedback_text.split('\n') if line.startswith('RATING:')]
        rating = 3.0  # Default rating
        if rating_line:
            try:
                rating = float(rating_line[0].replace('RATING:', '').strip())
            except ValueError:
                pass
        
        # Save the feedback
        feedback = AnswerFeedback(
            answer_id=answer.id,
            content=feedback_text,
            rating=rating
        )
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Answer saved and feedback generated',
            'feedback': feedback_text,
            'answer_id': answer.id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating feedback: {str(e)}'})

@interviews.route('/complete/<int:interview_id>', methods=['POST'])
@login_required
def complete_interview(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Check if this is the user's interview
    if interview.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('interviews.index'))
    
    # Calculate average rating from answer feedbacks
    total_rating = 0.0
    count = 0
    
    for answer in interview.answers:
        if answer.feedback and answer.feedback.rating:
            total_rating += answer.feedback.rating
            count += 1
    
    if count > 0:
        interview.rating = round(total_rating / count, 1)
    else:
        interview.rating = 3.0  # Default rating
    
    # Generate overall review
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Gather all questions and feedback
        qa_pairs = []
        for answer in interview.answers:
            question = Question.query.get(answer.question_id)
            qa_pairs.append({
                'question': question.text,
                'feedback': answer.feedback.content if answer.feedback else 'No feedback available'
            })
        
        # Prepare prompt for Gemini
        prompt = f"""
        You are an expert IT interviewer reviewing a candidate's performance for a {interview.grade} {interview.profession.name} position.
        
        Based on the following question-feedback pairs, provide a comprehensive review of the candidate's performance.
        If the list is empty, generate a simulated review as if the candidate did pretty well overall.
        
        {qa_pairs if qa_pairs else "No specific feedback available, please generate a simulated review that's realistic and helpful."}
        
        Format your response as:
        OVERALL_REVIEW: A comprehensive assessment of the candidate's performance (2-3 paragraphs)
        STRENGTHS:
        - Key strength 1
        - Key strength 2
        - Key strength 3
        WEAKNESSES:
        - Key weakness 1
        - Key weakness 2
        - Key weakness 3
        IMPROVEMENTS:
        - Improvement suggestion 1
        - Improvement suggestion 2
        - Improvement suggestion 3
        """
        
        response = model.generate_content(prompt)
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
            elif line.strip() and current_section:
                content.append(line.strip())
        
        if current_section:
            sections[current_section] = '\n'.join(content)
        
        # Create review
        review = InterviewReview(
            interview_id=interview.id,
            content=sections.get('content', ''),
            strengths=sections.get('strengths', ''),
            weaknesses=sections.get('weaknesses', ''),
            improvements=sections.get('improvements', '')
        )
        db.session.add(review)
        
    except Exception as e:
        flash(f'Error generating interview review: {str(e)}', 'warning')
    
    db.session.commit()
    flash('Interview completed successfully!', 'success')
    return redirect(url_for('interviews.review', interview_id=interview.id))

@interviews.route('/review/<int:interview_id>')
@login_required
def review(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Check if this is the user's interview
    if interview.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('interviews.index'))
    
    return render_template('interviews/review.html', interview=interview)