import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image
from src import db
from src.models import User, CV
from src.forms import ProfileForm

profile = Blueprint('profile', __name__, url_prefix='/profile')

@profile.route('/')
@login_required
def index():
    form = ProfileForm()
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.full_name.data = current_user.full_name
    
    # Set original values for validation
    form.original_username = current_user.username
    form.original_email = current_user.email
    
    # Get the user's latest CV
    latest_cv = CV.query.filter_by(user_id=current_user.id).order_by(CV.timestamp.desc()).first()
    
    return render_template('profile/index.html', form=form, latest_cv=latest_cv)

@profile.route('/update', methods=['POST'])
@login_required
def update():
    form = ProfileForm()
    
    # Set original values for validation
    form.original_username = current_user.username
    form.original_email = current_user.email
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data
        
        # Handle profile photo upload
        if form.profile_photo.data:
            photo = form.profile_photo.data
            filename = secure_filename(f"profile_{current_user.id}.jpg")
            photo_path = os.path.join(current_app.static_folder, 'uploads', filename)
            
            # Save and resize image to 1:1 ratio
            try:
                img = Image.open(photo)
                # Determine the square crop dimensions
                min_dimension = min(img.width, img.height)
                left = (img.width - min_dimension) / 2
                top = (img.height - min_dimension) / 2
                right = (img.width + min_dimension) / 2
                bottom = (img.height + min_dimension) / 2
                
                # Crop to square and resize
                img = img.crop((left, top, right, bottom))
                img = img.resize((300, 300))  # Standard profile size
                img.save(photo_path)
                
                current_user.profile_photo = filename
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'danger')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    return redirect(url_for('profile.index'))

@profile.route('/download-cv/<int:cv_id>')
@login_required
def download_cv(cv_id):
    cv_record = CV.query.get_or_404(cv_id)
    
    # Check if this is the user's CV
    if cv_record.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('profile.index'))
    
    return send_from_directory(
        directory=os.path.join(current_app.static_folder, 'uploads'),
        path=cv_record.file_path,
        as_attachment=True
    )