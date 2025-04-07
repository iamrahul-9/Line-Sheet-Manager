from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = '12345678'  # Add a secret key for session management

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Ensure the upload folder exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logging.info(f"Upload folder '{app.config['UPLOAD_FOLDER']}' created or already exists.")
except Exception as e:
    logging.error(f"Error creating upload folder '{app.config['UPLOAD_FOLDER']}': {e}")

def init_db():
    with sqlite3.connect("products.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        style TEXT,
                        colors TEXT,
                        content TEXT,
                        sizes TEXT,
                        price TEXT,
                        image TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS line_sheets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        filename TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'minkas':  # Replace with your credentials
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    # Replace None image values with an empty string or a placeholder
    products = [(id, style, colors, content, sizes, price, image if image else '') for id, style, colors, content, sizes, price, image in products]
    
    return render_template('index.html', products=products)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image part in the request.", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No selected file.", 400
    
    # Get the style number for naming the image
    style = request.form.get('style', '')
    if not style:
        return "Style number is required for image upload.", 400
    
    if file:
        # Use standardized naming convention: styleNumber.webp
        filename = f"{style}.webp"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file, overwriting if it exists
        file.save(file_path)
        logging.info(f"Image saved: {file_path}")
        
        return redirect(url_for('index'))

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    file = request.files['excel']
    title = request.form['title'].upper()
    df = pd.read_excel(file)
    
    # Define a mapping from expected column names to actual column names
    column_mapping = {
        'STYLE#': 'STYLE#',
        'COLOR': 'COLOR',
        'CONTENT': 'CONTENT',
        'SIZES': 'SIZES',
        'PRICE': 'PRICE'
    }
    
    # Check if all expected columns are present in the Excel file
    for expected_col in column_mapping.values():
        if expected_col not in df.columns:
            return f"Column '{expected_col}' is missing in the Excel file.", 400
    
    # No need to create a subdirectory for each line sheet anymore
    # Images will stay in the main uploads folder
    
    with sqlite3.connect("products.db") as conn:
        conn.execute("DELETE FROM products")  # Clear existing data
        for _, row in df.iterrows():
            style = row[column_mapping['STYLE#']]
            image_filename = f"{style}.webp"  # Assuming images are in WEBP format
            
            # Check if the image exists in the uploads folder
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], image_filename)):
                # Use a relative path from 'static' to the image
                image_path = os.path.join('uploads', image_filename)
            else:
                image_path = ''  # Handle missing images
            
            conn.execute("INSERT INTO products (style, colors, content, sizes, price, image) VALUES (?, ?, ?, ?, ?, ?)",
                         (style, row[column_mapping['COLOR']], row[column_mapping['CONTENT']], 
                          row[column_mapping['SIZES']], row[column_mapping['PRICE']], image_path))
    
    # Generate and save the line sheet HTML
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    # Filter out incomplete entries
    products = [product for product in products if all(product)]
    
    rendered_html = render_template('line_sheets.html', products=products, title=title, pdf_view=True)
    
    # Create a filename from the title: convert to lowercase and replace spaces and special characters with underscores
    formatted_title = re.sub(r'[^\w\s]', '_', title.lower())  # Replace non-alphanumeric chars with underscore
    formatted_title = re.sub(r'\s+', '_', formatted_title)    # Replace spaces with underscore
    formatted_title = re.sub(r'_+', '_', formatted_title)     # Replace multiple underscores with a single one
    
    # Save the rendered HTML to a file with the formatted title as filename
    filename = f'{formatted_title}.html'
    filepath = os.path.join('static', filename)
    with open(filepath, 'w') as file:
        file.write(rendered_html)
    
    # Save the line sheet metadata to the database
    with sqlite3.connect("products.db") as conn:
        conn.execute("INSERT INTO line_sheets (title, filename) VALUES (?, ?)", (title, filename))
    
    return redirect(url_for('line_sheets', title=title))

@app.route('/line_sheets')
def line_sheets():
    # This route should also be accessible without authentication
    title = request.args.get('title', 'MINKAS LINE SHEETS')
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    # Filter out incomplete entries
    products = [product for product in products if all(product)]
    
    return render_template('line_sheets.html', products=products, title=title)

@app.route('/list_line_sheets')
def list_line_sheets():
    # This route should also be accessible without authentication
    with sqlite3.connect("products.db") as conn:
        line_sheets = conn.execute("SELECT * FROM line_sheets ORDER BY created_at DESC").fetchall()
    return render_template('list_line_sheets.html', line_sheets=line_sheets)

@app.route('/view_line_sheet/<filename>')
def view_line_sheet(filename):
    # This route should be accessible without authentication
    try:
        # Get the line sheet information from the database
        with sqlite3.connect("products.db") as conn:
            line_sheet = conn.execute(
                "SELECT * FROM line_sheets WHERE filename = ?", 
                (filename,)
            ).fetchone()
            
            if line_sheet:
                title = line_sheet[1]  # Title is stored in the second column
                
                # We could try parsing the HTML, but a simpler approach is to just query the database
                # for all products and display them - the sorting in PhotoSwipe will work
                with sqlite3.connect("products.db") as conn:
                    products = conn.execute("SELECT * FROM products").fetchall()
                
                # Filter out incomplete entries
                products = [product for product in products if all(product)]
                
                # Render the line_sheets template with the products data
                return render_template('line_sheets.html', products=products, title=title, pdf_view=False)
    
    except Exception as e:
        logging.error(f"Error rendering line sheet {filename}: {e}")
        logging.error(f"Error details: {str(e)}")
    
    # Fallback to direct redirect if any issues occur
    return redirect(url_for('static', filename=filename))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
