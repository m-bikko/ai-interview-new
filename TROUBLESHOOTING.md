# Troubleshooting Guide

This guide helps resolve common issues you might encounter when running the AI Interview platform.

## Database Issues

### Unable to open database file

**Symptoms:**
```
sqlite3.OperationalError: unable to open database file
```

**Solutions:**
1. Ensure the instance directory exists and has proper permissions:
   ```bash
   mkdir -p instance
   chmod -R 777 instance
   ```

2. Check if another process is locking the database file. Restart your system if necessary.

3. Try using the quickstart script which uses an in-memory database:
   ```bash
   ./quickstart.sh
   ```

### Database migration errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table
```

**Solutions:**
1. Reset the database:
   ```bash
   python seed_data.py reset
   ```

## File Upload Issues

### Permission errors when uploading files

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. Ensure the uploads and static/uploads directories exist and have proper permissions:
   ```bash
   mkdir -p uploads static/uploads
   chmod -R 777 uploads static/uploads
   ```

### Files not displaying in the application

**Symptoms:**
- Audio recordings not playing
- Images not showing

**Solutions:**
1. Check that files are being saved to the correct location:
   ```bash
   ls -la static/uploads/
   ```

2. Verify file paths in the templates match where files are being stored.

## Gemini API Issues

### API Key errors

**Symptoms:**
```
google.api_core.exceptions.InvalidArgument: 400 API key not valid
```

**Solutions:**
1. Verify your API key in the `.env` file:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

2. Check if the API key has reached its quota or has been disabled.

### Model not found errors

**Symptoms:**
```
google.api_core.exceptions.NotFound: 404 Model not found
```

**Solutions:**
1. Verify the model name in the code. The application uses 'gemini-2.0-flash'.

## Installation Issues

### Virtual environment problems

**Symptoms:**
```
No module named 'flask'
```

**Solutions:**
1. Ensure you've activated the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Python version compatibility

**Symptoms:**
```
SyntaxError: invalid syntax
```

**Solutions:**
1. Verify you're using Python 3.8 or higher:
   ```bash
   python --version
   ```

2. If needed, install a compatible Python version and create a new virtual environment.

## Quick Reset

If you're experiencing persistent issues, try this reset procedure:

```bash
# 1. Remove problematic directories
rm -rf instance uploads/
rm -rf static/uploads/

# 2. Recreate necessary directories with proper permissions
mkdir -p instance uploads static/uploads
chmod -R 777 instance uploads static/uploads

# 3. Reset and reseed the database
python seed_data.py reset

# 4. Start the application
python app.py
```

## Still Having Issues?

If you continue to experience problems:

1. Try the quick start script which uses an in-memory database:
   ```bash
   ./quickstart.sh
   ```

2. Check the console output for specific error messages.

3. File an issue on the project repository with the error details and steps to reproduce.