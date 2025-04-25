# AI Interview Platform

AI Interview is a platform that allows IT professionals to practice interviews and receive AI-powered feedback on their responses. It also provides CV review functionality.

## Features

### User Authentication
- Registration and login
- User profile management with photo upload

### Interview Simulation
- Multiple IT professions and experience levels (Junior/Middle/Senior)
- Audio recording for interview answers
- AI-powered feedback using Google's Gemini 2.0 Flash API
- Interview history with ratings and detailed review

### CV Analysis
- Upload CV in PDF format
- AI-powered review and feedback
- Suggestions for improvement and strengths analysis

## Technology Stack
- **Backend**: Python with Flask
- **Database**: SQLAlchemy with SQLite (configurable for other databases)
- **Frontend**: Bootstrap, JavaScript, HTML, CSS
- **AI**: Google Gemini 2.0 Flash API

## Supported Professions

The platform supports the following IT professions:
- Backend Developer
- Frontend Developer
- Full Stack Developer
- Data Scientist
- Product Manager
- DevOps Engineer
- UX/UI Designer
- Mobile Developer

Each profession has questions tailored to Junior, Middle, and Senior experience levels.

## Quick Start

The easiest way to run the application is using the provided run script:

```bash
# Make the script executable if needed
chmod +x run.sh

# Run the application
./run.sh
```

This will:
1. Create a virtual environment if it doesn't exist
2. Install all dependencies
3. Set up the database and seed it with initial data
4. Start the application

Once started, access the application at http://localhost:5000

### Test Mode

For quick testing with an in-memory database, use:

```bash
# Make the script executable if needed
chmod +x quickstart.sh

# Run in test mode
./quickstart.sh
```

## Manual Setup

If you prefer to set up manually:

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create required directories with proper permissions:
   ```bash
   mkdir -p instance uploads static/uploads
   chmod -R 777 instance uploads static/uploads
   ```

4. Create a `.env` file with your Gemini API key:
   ```
   SECRET_KEY=your-secret-key-here
   DATABASE_URI=sqlite:///instance/ai_interview.db
   GEMINI_API_KEY=your-api-key-here
   ```

5. Initialize the database:
   ```bash
   python seed_data.py
   ```

6. Run the application:
   ```bash
   python app.py
   ```

7. Access the application at http://localhost:5000

## Testing

To run the tests:

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## Troubleshooting

If you encounter issues running the application, please refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide for common problems and solutions.

Common fixes:

1. Database permission issues:
   ```bash
   mkdir -p instance
   chmod -R 777 instance
   ```

2. File upload issues:
   ```bash
   mkdir -p uploads static/uploads
   chmod -R 777 uploads static/uploads
   ```

3. Reset database:
   ```bash
   python seed_data.py reset
   ```

## Project Structure

- `/src` - Backend Python code
- `/static` - Static assets (CSS, JS, images)
- `/templates` - HTML templates
- `/data` - Questions dataset and other data
- `/uploads` - Uploaded files (CVs, audio recordings, profile photos)
- `/instance` - Database files

## Using the Application

1. Register an account or log in
2. Navigate to the Catalog to browse available professions
3. Select a profession and experience level to start an interview
4. Answer questions by recording your voice
5. Receive AI-powered feedback on your responses
6. Upload your CV for AI analysis and improvement suggestions
7. Track your progress in the History section

## License

[MIT License](LICENSE)