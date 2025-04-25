from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100))
    profile_photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    interviews = db.relationship('Interview', backref='user', lazy=True)
    cvs = db.relationship('CV', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Profession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    questions = db.relationship('Question', backref='profession', lazy=True)
    interviews = db.relationship('Interview', backref='profession', lazy=True)
    
    def __repr__(self):
        return f'<Profession {self.name}>'

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Many-to-many relationship with professions
    professions = db.relationship('Profession', secondary='profession_skills',
                                 backref=db.backref('skills', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Skill {self.name}>'

# Association table for profession-skills many-to-many relationship
profession_skills = db.Table('profession_skills',
    db.Column('profession_id', db.Integer, db.ForeignKey('profession.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    grade = db.Column(db.String(20), nullable=False)  # junior, middle, senior
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False)
    
    # Relationship
    answers = db.relationship('Answer', backref='question', lazy=True)
    
    def __repr__(self):
        return f'<Question {self.id}: {self.text[:30]}...>'

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False)
    grade = db.Column(db.String(20), nullable=False)  # junior, middle, senior
    rating = db.Column(db.Float)  # 1.0-5.0
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    answers = db.relationship('Answer', backref='interview', lazy=True)
    review = db.relationship('InterviewReview', backref='interview', uselist=False)
    
    def __repr__(self):
        return f'<Interview {self.id} - {self.user.username} - {self.profession.name}>'

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    audio_file = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    feedback = db.relationship('AnswerFeedback', backref='answer', uselist=False)
    
    def __repr__(self):
        return f'<Answer {self.id} - Interview {self.interview_id}>'

class AnswerFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    content = db.Column(db.Text)
    rating = db.Column(db.Float)  # 1.0-5.0
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AnswerFeedback {self.id} - Answer {self.answer_id}>'

class InterviewReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interview.id'), nullable=False)
    content = db.Column(db.Text)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    improvements = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<InterviewReview {self.id} - Interview {self.interview_id}>'

class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    review = db.relationship('CVReview', backref='cv', uselist=False)
    
    def __repr__(self):
        return f'<CV {self.id} - {self.user.username}>'

class CVReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(db.Integer, db.ForeignKey('cv.id'), nullable=False)
    content = db.Column(db.Text)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    improvements = db.Column(db.Text)
    lacking_sections = db.Column(db.Text)
    benefits = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CVReview {self.id} - CV {self.cv_id}>'