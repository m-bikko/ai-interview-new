"""
Tests for the AI Interview platform.
"""

import os
import unittest
from flask import url_for
from src import create_app, db
from src.models import User, Profession, Skill, Question, Interview, CV
from werkzeug.security import generate_password_hash

class AIInterviewTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._populate_test_data()
            
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up after tests."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()
    
    def _populate_test_data(self):
        """Populate database with test data."""
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        
        # Create test profession
        profession = Profession(
            name='Test Profession',
            description='This is a test profession'
        )
        db.session.add(profession)
        
        # Create test skills
        skill1 = Skill(name='Skill 1')
        skill2 = Skill(name='Skill 2')
        db.session.add_all([skill1, skill2])
        
        # Associate skills with profession
        profession.skills.append(skill1)
        profession.skills.append(skill2)
        
        # Create test questions
        for grade in ['junior', 'middle', 'senior']:
            for i in range(5):
                question = Question(
                    text=f'Test question {i+1} for {grade}',
                    grade=grade,
                    profession_id=1
                )
                db.session.add(question)
        
        db.session.commit()
    
    def _login(self, email='test@example.com', password='password123'):
        """Helper method to log in a test user."""
        return self.client.post('/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    
    def _logout(self):
        """Helper method to log out."""
        return self.client.get('/logout', follow_redirects=True)
    
    # ==========================================================
    # Test Cases
    # ==========================================================
    
    def test_home_page(self):
        """Test that the home page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI-Powered Interview Practice', response.data)
    
    def test_login_page(self):
        """Test that the login page loads correctly."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_register_page(self):
        """Test that the register page loads correctly."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'full_name': 'New User',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)
        
        # Check that the user was created in the database
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'new@example.com')
    
    def test_user_login(self):
        """Test user login."""
        response = self._login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Catalog', response.data)
    
    def test_catalog_page_requires_login(self):
        """Test that the catalog page requires login."""
        response = self.client.get('/catalog/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Please log in to access this page', response.data)
    
    def test_catalog_page_after_login(self):
        """Test that the catalog page loads after login."""
        self._login()
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profession Catalog', response.data)
        self.assertIn(b'Test Profession', response.data)
    
    def test_profession_detail_page(self):
        """Test that the profession detail page loads correctly."""
        self._login()
        response = self.client.get('/catalog/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Profession', response.data)
        self.assertIn(b'Choose Experience Level', response.data)
    
    def test_interview_history_page(self):
        """Test that the interview history page loads correctly."""
        self._login()
        response = self.client.get('/interviews/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Interview History', response.data)
    
    def test_cv_page(self):
        """Test that the CV page loads correctly."""
        self._login()
        response = self.client.get('/cv/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CV Management', response.data)
        self.assertIn(b'Upload Your CV', response.data)
    
    def test_profile_page(self):
        """Test that the profile page loads correctly."""
        self._login()
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your Profile', response.data)
        self.assertIn(b'Test User', response.data)
    
    def test_start_interview_page(self):
        """Test that the interview page loads correctly."""
        self._login()
        response = self.client.get('/interviews/profession/1/junior')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Profession (Junior) Interview', response.data)
        self.assertIn(b'Question 1', response.data)
    
    def test_logout(self):
        """Test user logout."""
        self._login()
        response = self._logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out', response.data)

if __name__ == '__main__':
    unittest.main()