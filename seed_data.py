"""
Seed database with professions, skills, and questions.
"""

import os
import sys
from flask import Flask
from src import db, create_app
from src.models import Profession, Skill, Question
from data.questions import QUESTIONS

def seed_database():
    """Seed the database with initial data."""
    print("Seeding database...")
    
    try:
        # Define professions with descriptions
        professions = {
            "backend_developer": {
                "name": "Backend Developer",
                "description": "Backend developers create server-side applications, APIs, and services that power websites and applications. They work with databases, server logic, and application architecture.",
                "skills": ["Python", "Java", "Node.js", "SQL", "NoSQL", "API Design", "Microservices", "Docker", "Cloud Services", "Security"]
            },
            "frontend_developer": {
                "name": "Frontend Developer",
                "description": "Frontend developers create the user interface and user experience of websites and applications. They work with HTML, CSS, JavaScript, and frontend frameworks.",
                "skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Vue", "Angular", "Responsive Design", "Web Accessibility", "UI Frameworks"]
            },
            "full_stack_developer": {
                "name": "Full Stack Developer",
                "description": "Full stack developers work on both the frontend and backend of applications. They have a broad range of skills and can develop complete web applications.",
                "skills": ["JavaScript", "Python", "Node.js", "React", "Angular", "SQL", "NoSQL", "API Design", "DevOps", "Cloud Services"]
            },
            "data_scientist": {
                "name": "Data Scientist",
                "description": "Data scientists analyze and interpret complex data to help organizations make better decisions. They use statistics, machine learning, and programming to extract insights from data.",
                "skills": ["Python", "R", "Machine Learning", "Statistics", "Data Visualization", "SQL", "Big Data", "Deep Learning", "Data Mining", "NLP"]
            },
            "product_manager": {
                "name": "Product Manager",
                "description": "Product managers are responsible for the strategy, roadmap, and features of a product. They work with cross-functional teams to deliver products that meet user needs and business goals.",
                "skills": ["Product Strategy", "User Research", "Market Analysis", "Roadmapping", "Agile/Scrum", "Stakeholder Management", "Data Analysis", "UX/UI", "Prioritization", "Communication"]
            },
            "devops_engineer": {
                "name": "DevOps Engineer",
                "description": "DevOps engineers work at the intersection of software development and IT operations. They automate processes, manage infrastructure, and improve deployment workflows.",
                "skills": ["Linux", "CI/CD", "Docker", "Kubernetes", "Infrastructure as Code", "Cloud Services", "Monitoring", "Scripting", "Security", "Automation"]
            },
            "ux_ui_designer": {
                "name": "UX/UI Designer",
                "description": "UX/UI designers create user-centered and visually appealing interfaces for applications and websites. They focus on the look and feel of products and the overall user experience.",
                "skills": ["User Research", "Wireframing", "Prototyping", "Visual Design", "Interaction Design", "Figma", "Adobe XD", "User Testing", "Accessibility", "Design Systems"]
            },
            "mobile_developer": {
                "name": "Mobile Developer",
                "description": "Mobile developers create applications for mobile platforms like iOS and Android. They work with mobile-specific technologies, design patterns, and user interfaces.",
                "skills": ["Swift", "Kotlin", "Flutter", "React Native", "Mobile UI Design", "App Performance", "API Integration", "Push Notifications", "Mobile Security", "App Store Deployment"]
            }
        }
        
        # Create skills
        all_skills = set()
        for profession_data in professions.values():
            all_skills.update(profession_data["skills"])
        
        skill_objects = {}
        for skill_name in all_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.session.add(skill)
            skill_objects[skill_name] = skill
        
        # Commit skills first to get IDs
        db.session.commit()
        
        # Create professions and associate skills
        profession_objects = {}
        for profession_key, profession_data in professions.items():
            profession = Profession.query.filter_by(name=profession_data["name"]).first()
            if not profession:
                profession = Profession(
                    name=profession_data["name"],
                    description=profession_data["description"]
                )
                db.session.add(profession)
            
            # Associate skills with profession
            for skill_name in profession_data["skills"]:
                skill = skill_objects[skill_name]
                if skill not in profession.skills:
                    profession.skills.append(skill)
            
            profession_objects[profession_key] = profession
        
        # Commit professions to get IDs
        db.session.commit()
        
        # Create questions
        question_count = 0
        for profession_key, grade_questions in QUESTIONS.items():
            profession = profession_objects[profession_key]
            
            for grade, questions_list in grade_questions.items():
                for question_text in questions_list:
                    existing_question = Question.query.filter_by(
                        text=question_text,
                        grade=grade,
                        profession_id=profession.id
                    ).first()
                    
                    if not existing_question:
                        question = Question(
                            text=question_text,
                            grade=grade,
                            profession_id=profession.id
                        )
                        db.session.add(question)
                        question_count += 1
        
        db.session.commit()
        print(f"Database seeded successfully! Added {len(all_skills)} skills, {len(professions)} professions, and {question_count} questions.")
        return True
    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        return False

if __name__ == "__main__":
    # Create Flask app with in-memory SQLite database
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Seed database
        success = seed_database()
        
        if success:
            print("Database seeded successfully! You can now run the application.")
        else:
            print("Failed to seed database. Please check the error messages above.")
            sys.exit(1)