import os
import re
from flask import Blueprint, current_app, render_template, render_template_string, send_from_directory, url_for
from app import app
import markdown


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home_page():

    '''
    View root page function that returns the index page and its data
    '''
    return render_template('main/home.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

def get_readme_content():
    base_dir = os.path.dirname(current_app.root_path)
    readme_path = os.path.join(base_dir, 'doc', 'README.md')
    try:
        with open(readme_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "README.md not found in /doc directory."

def fix_image_paths(html_content):
    def repl(match):
        img_src = match.group(1)
        new_src = url_for('main.serve_doc_file', filename=img_src)
        return f'<img src="{new_src}"'
    
    pattern = r'<img src="([^"]+)"'
    return re.sub(pattern, repl, html_content)

@main.route('/documentation')
def display_readme():
    readme_content = get_readme_content()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(readme_content)
    
    # Fix image paths
    html_content = fix_image_paths(html_content)
    
    # Debug: Print the HTML content
    print("HTML Content:", html_content)
    
    return render_template('main/documentation.html', content=html_content)

@main.route('/doc/<path:filename>')
def serve_doc_file(filename):
    base_dir = os.path.dirname(current_app.root_path)
    doc_dir = os.path.join(base_dir, 'doc')
    
    # Debug: Print the requested filename and full path
    full_path = os.path.join(doc_dir, filename)
    print(f"Requested file: {filename}")
    print(f"Full path: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")
    
    return send_from_directory(doc_dir, filename)