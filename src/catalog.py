from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_required
from src import db
from src.models import Profession, Skill
from src.forms import CatalogFilterForm

catalog = Blueprint('catalog', __name__, url_prefix='/catalog')

@catalog.route('/')
@login_required
def index():
    form = CatalogFilterForm()
    
    # Dynamically populate profession choices
    professions = [(str(p.id), p.name) for p in Profession.query.all()]
    form.profession.choices = [('', 'All Professions')] + professions
    
    # Dynamically populate skill choices
    skills = [(str(s.id), s.name) for s in Skill.query.all()]
    form.skill.choices = [('', 'All Skills')] + skills
    
    # Filter professions based on form data
    query = Profession.query
    
    if request.args.get('profession'):
        profession_id = request.args.get('profession')
        query = query.filter(Profession.id == profession_id)
    
    if request.args.get('skill'):
        skill_id = request.args.get('skill')
        query = query.join(Profession.skills).filter(Skill.id == skill_id)
    
    if request.args.get('grade'):
        grade = request.args.get('grade')
        # This doesn't filter professions, but we'll store it in session for Interview creation
        session['selected_grade'] = grade
    
    if request.args.get('search'):
        search_term = request.args.get('search')
        query = query.filter(Profession.name.ilike(f'%{search_term}%') | 
                           Profession.description.ilike(f'%{search_term}%'))
    
    # Ensure we import session at the top of the file
    from flask import session
    
    professions = query.all()
    return render_template('catalog/index.html', professions=professions, form=form)

@catalog.route('/<int:profession_id>')
@login_required
def profession_detail(profession_id):
    profession = Profession.query.get_or_404(profession_id)
    # Get the selected grade from session if available
    selected_grade = session.get('selected_grade', 'junior')
    return render_template('catalog/profession_detail.html', 
                          profession=profession,
                          selected_grade=selected_grade)