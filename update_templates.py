"""
Update templates to fix the block naming issue.
"""

import os
import re

# Directories to search for templates
template_dirs = [
    'templates/catalog',
    'templates/interviews',
    'templates/cv',
    'templates/profile',
]

# Files that should use the main_content block (for authenticated users)
auth_templates = [
    'templates/catalog/index.html',
    'templates/catalog/profession_detail.html',
    'templates/interviews/index.html',
    'templates/interviews/interview.html',
    'templates/interviews/review.html',
    'templates/cv/index.html',
    'templates/cv/view.html',
    'templates/profile/index.html',
]

# Keep these templates using content block (for non-authenticated users)
non_auth_templates = [
    'templates/main/index.html',
    'templates/auth/login.html',
    'templates/auth/register.html',
]

def update_template(file_path):
    """Update block names in template file."""
    # Read the template file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if it's an authenticated template
    if file_path in auth_templates:
        print(f"Updating authenticated template: {file_path}")
        # Replace {% block content %} with {% block main_content %}
        content = re.sub(r'{%\s*block\s+content\s*%}', '{% block main_content %}', content)
        # Replace {% endblock %} with {% endblock main_content %}
        # We need to be careful not to change other block endblocks
        # Get all block names
        blocks = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
        # Replace the last endblock (which should be the content block)
        endblock_pattern = r'{%\s*endblock\s*%}'
        matches = list(re.finditer(endblock_pattern, content))
        if matches and 'main_content' in blocks:
            # Replace only the last match (content block)
            last_match = matches[-1]
            content = content[:last_match.start()] + '{% endblock main_content %}' + content[last_match.end():]
    
    # Write back the updated content
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    """Main function to update all templates."""
    # Find all template files
    for template_dir in template_dirs:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    update_template(file_path)
    
    # Update specific templates
    for file_path in auth_templates + non_auth_templates:
        if os.path.exists(file_path):
            update_template(file_path)

if __name__ == "__main__":
    main()
    print("Templates updated successfully!")