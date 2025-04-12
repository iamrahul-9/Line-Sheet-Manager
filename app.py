from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import sqlite3
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
import re
import shutil
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = '12345678'  # Add a secret key for session management

# Add configuration for URL generation
app.config['APPLICATION_ROOT'] = '/'
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Cloudinary configuration
cloudinary.config(
    cloud_name='dtydw90se',
    api_key='366769575269776',
    api_secret='dEUDnefjIJ78-EcLBlMNWmLMEVs',
    secure=True,  # Force HTTPS
    cdn_subdomain=True  # Enable CDN subdomain
)


# Add seed data configuration
SEED_DATA_DIR = 'static'  # Changed to use static directory
DEFAULT_EXCEL = 'FW25 Linesheets Data Final.xlsx'  # Using the actual Excel file name

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Ensure the upload folder exists
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logging.info(f"Upload folder '{app.config['UPLOAD_FOLDER']}' created or already exists.")
except Exception as e:
    logging.error(f"Error creating upload folder '{app.config['UPLOAD_FOLDER']}': {e}")

def get_cloudinary_url(public_id, transformation=None):
    """Get a secure Cloudinary URL with proper transformations"""
    try:
        options = {
            'secure': True,
            'resource_type': 'image',
            'format': 'webp'
        }
        if transformation:
            options['transformation'] = transformation
            
        url, _ = cloudinary.utils.cloudinary_url(
            public_id,
            **options
        )
        return url
    except Exception as e:
        logging.error(f"Error generating Cloudinary URL: {e}")
        return None

def load_seed_data():
    """Load initial data from static directory"""
    try:
        # Read and process the default Excel file
        excel_path = os.path.join(SEED_DATA_DIR, DEFAULT_EXCEL)
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
            
            # Define column mapping
            column_mapping = {
                'STYLE#': 'STYLE#',
                'COLOR': 'COLOR',
                'DESCRIPTION': 'DESCRIPTION',
                'SIZES': 'SIZES',
                'PRICE': 'PRICE'
            }
            
            # Insert data into database
            with sqlite3.connect("products.db") as conn:
                # Create a default line sheet for seed data
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO line_sheets (title, filename) VALUES (?, ?)",
                    ('DEFAULT SEED DATA', 'default_seed_data.html')
                )
                
                # Get the line sheet ID (either existing or newly created)
                cursor.execute("SELECT id FROM line_sheets WHERE filename = ?", ('default_seed_data.html',))
                line_sheet_id = cursor.fetchone()[0]
                
                for _, row in df.iterrows():
                    style = row[column_mapping['STYLE#']]
                    
                    # Check if image exists in Cloudinary
                    try:
                        image_url = get_cloudinary_url(f"{style}")  # Updated to use new format without folder
                    except:
                        image_url = ''
                    
                    conn.execute(
                        "INSERT INTO products (style, colors, description, sizes, price, image, line_sheet_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (style, row[column_mapping['COLOR']], row[column_mapping['DESCRIPTION']], 
                         row[column_mapping['SIZES']], row[column_mapping['PRICE']], image_url, line_sheet_id)
                    )
                
                # Get all products for the line sheet
                products = conn.execute("SELECT * FROM products").fetchall()
                
                # Filter out incomplete entries
                products = [product for product in products if all(product[:-1])]  # Exclude line_sheet_id from check
                
                return products
                
    except Exception as e:
        logging.error(f"Error loading seed data: {e}")
        return []

def init_db():
    with sqlite3.connect("products.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        style TEXT,
                        colors TEXT,
                        description TEXT,
                        sizes TEXT,
                        price TEXT,
                        image TEXT,
                        line_sheet_id INTEGER)''')  # Add line_sheet_id to associate products with specific line sheets
        conn.execute('''CREATE TABLE IF NOT EXISTS line_sheets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        filename TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS app_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE,
                        value TEXT)''')
        
        # Check if the line_sheet_id column exists in the products table
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add line_sheet_id column if it doesn't exist
        if 'line_sheet_id' not in columns:
            conn.execute("ALTER TABLE products ADD COLUMN line_sheet_id INTEGER")
        
        # Check if products table is empty
        if not conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]:
            load_seed_data()
            
        # Set default album price list if not exists
        if not conn.execute("SELECT value FROM app_settings WHERE key='album_price_list_url'").fetchone():
            # Default to the static file path directly instead of using url_for
            default_pdf_path = "/static/FW25 ALBUM PRICE LIST.pdf"
            conn.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)", 
                       ('album_price_list_url', default_pdf_path))

with app.app_context():
    # Code that requires the application context
    try:
        init_db()
        logging.info("Database initialization completed successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        # Continue running the app even if database initialization fails
        # The routes will handle database errors gracefully

def get_album_price_list_url():
    """Get the current Album Price List URL from the database"""
    try:
        with sqlite3.connect("products.db") as conn:
            result = conn.execute("SELECT value FROM app_settings WHERE key='album_price_list_url'").fetchone()
            if result:
                # If the URL starts with /static, convert it to a proper URL
                if result[0].startswith('/static'):
                    return url_for('static', filename=result[0].replace('/static/', ''))
                return result[0]
    except Exception as e:
        logging.error(f"Error getting album price list URL: {e}")
    
    # Fallback to static file if not found
    return url_for('static', filename='FW25 ALBUM PRICE LIST.pdf')

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
    products = [(id, style, colors, description, sizes, price, image if image else '') 
                for id, style, colors, description, sizes, price, image, line_sheet_id in products]
    
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
        try:
            # Upload to Cloudinary with style number as public_id, without folder structure
            result = cloudinary.uploader.upload(
                file,
                public_id=f"{style}",  # No folder structure in the public_id
                resource_type="image",
                format="webp",
                overwrite=True,
                invalidate=True
            )
            
            # Get the secure URL with proper transformations
            image_url = get_cloudinary_url(
                f"{style}",  # No folder structure
                transformation={
                    'quality': 'auto',
                    'fetch_format': 'auto'
                }
            )
            
            if not image_url:
                raise Exception("Failed to generate Cloudinary URL")
            
            # Update the database with the Cloudinary URL
            with sqlite3.connect("products.db") as conn:
                conn.execute(
                    "UPDATE products SET image = ? WHERE style = ?",
                    (image_url, style)
                )
            
            logging.info(f"Image uploaded to Cloudinary: {image_url}")
            return redirect(url_for('index'))
            
        except Exception as e:
            logging.error(f"Error uploading to Cloudinary: {e}")
            return f"Error uploading image: {str(e)}", 500

@app.route('/upload-directory', methods=['POST'])
def upload_directory():
    if 'images' not in request.files:
        return jsonify({'success': False, 'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('images')
    title = request.form.get('title', '').strip().upper()  # Convert title to uppercase
    collection_name = request.form.get('collection_name', '').strip()
    
    if not title or not collection_name:
        return jsonify({'success': False, 'error': 'Title and Collection Name are required'}), 400
    
    uploaded_count = 0
    errors = []
    collection_products = []
    
    # Generate a safe filename
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', title.lower())
    line_sheet_filename = f"{safe_filename}.html"
    
    # Create the line sheet first to get its ID
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO line_sheets (title, filename) VALUES (?, ?)",
            (title, line_sheet_filename)
        )
        line_sheet_id = cursor.lastrowid
    
    for file in files:
        if file.filename == '':
            continue
            
        try:
            # Get original filename and remove any prefix that matches collection name
            filename = secure_filename(file.filename)
            name_without_ext = os.path.splitext(filename)[0]
            
            # Remove any prefix that matches collection name (case insensitive)
            collection_prefix = collection_name.replace(' ', '_').lower() + '_'
            if name_without_ext.lower().startswith(collection_prefix):
                name_without_ext = name_without_ext[len(collection_prefix):]
            
            # Use only the style number as the public_id, without any folder structure
            # This will save it with just the original filename without prefix
            public_id = f"{name_without_ext}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                public_id=public_id,  # No folder structure in the public_id
                resource_type="image",
                format="webp",
                overwrite=True,
                invalidate=True
            )
            
            # Get the secure URL
            image_url = get_cloudinary_url(
                public_id,
                transformation={
                    'quality': 'auto',
                    'fetch_format': 'auto'
                }
            )
            
            if not image_url:
                raise Exception("Failed to generate Cloudinary URL")
            
            # Create a product entry for this collection
            product = {
                'style': name_without_ext,
                'image': image_url,
                'colors': '',
                'description': '',
                'sizes': '',
                'price': '',
                'line_sheet_id': line_sheet_id  # Associate with the specific line sheet
            }
            collection_products.append(product)
            
            # Update the database
            with sqlite3.connect("products.db") as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO products (style, image, colors, description, sizes, price, line_sheet_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name_without_ext, image_url, '', '', '', '', line_sheet_id)
                )
            
            uploaded_count += 1
            
        except Exception as e:
            errors.append(f"Error uploading {filename}: {str(e)}")
            logging.error(f"Error uploading {filename}: {e}")
    
    if uploaded_count == 0 and errors:
        return jsonify({'success': False, 'error': '; '.join(errors)}), 500
    
    return jsonify({
        'success': True,
        'uploaded_count': uploaded_count,
        'line_sheet_url': url_for('view_line_sheet', filename=line_sheet_filename),
        'errors': errors if errors else None
    })

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'excel' not in request.files or 'album_price_list' not in request.files:
        return jsonify({'success': False, 'error': 'Missing required files'}), 400
    
    excel_file = request.files['excel']
    album_price_list = request.files['album_price_list']
    
    if excel_file.filename == '' or album_price_list.filename == '':
        return jsonify({'success': False, 'error': 'No selected files'}), 400
    
    # Check file types
    if not excel_file.filename.lower().endswith(('.xlsx', '.xls')) or not album_price_list.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'Invalid file formats'}), 400
    
    title = request.form.get('title', '').strip().upper()  # Convert title to uppercase
    
    if not title:
        # Generate a title if none was provided
        title = f"LINE SHEET {datetime.now().strftime('%Y-%m-%d')}"
    
    # Generate a safe filename
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', title.lower())
    line_sheet_filename = f"{safe_filename}.html"
    
    # Create database connection
    with sqlite3.connect("products.db") as conn:
        cursor = conn.cursor()
        
        # Create the line sheet first to get its ID
        cursor.execute(
            "INSERT INTO line_sheets (title, filename) VALUES (?, ?)",
            (title, line_sheet_filename)
        )
        line_sheet_id = cursor.lastrowid
        
        # Save the PDF
        try:
            album_result = cloudinary.uploader.upload(
                album_price_list,
                public_id=f"album_price_list",  # No folder structure in the public_id
                resource_type="raw",  # For non-image files like PDFs
                overwrite=True,
                invalidate=True
            )
            
            album_price_list_url = album_result['secure_url']
            
            # Update the album price list URL in the database
            conn.execute(
                "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
                ('album_price_list_url', album_price_list_url)
            )
        except Exception as e:
            logging.error(f"Error uploading Album Price List to Cloudinary: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
        
        # Process Excel file
        try:
            # Read Excel file
            df = pd.read_excel(excel_file)
            
            # Process each row
            for _, row in df.iterrows():
                # Extract data (handle possible missing columns)
                style = str(row.get('STYLE#', '')) if not pd.isna(row.get('STYLE#', '')) else ''
                color = str(row.get('COLOR', '')) if not pd.isna(row.get('COLOR', '')) else ''
                description = str(row.get('DESCRIPTION', '')) if not pd.isna(row.get('DESCRIPTION', '')) else ''
                sizes = str(row.get('SIZES', '')) if not pd.isna(row.get('SIZES', '')) else ''
                price = str(row.get('PRICE', '')) if not pd.isna(row.get('PRICE', '')) else ''
                
                # Skip empty rows
                if not style:
                    continue
                
                # Check if image exists in Cloudinary for this style
                try:
                    image_url = get_cloudinary_url(f"{style}")  # No folder structure
                except:
                    image_url = ''
                
                # Insert into database with line_sheet_id
                conn.execute(
                    "INSERT INTO products (style, colors, description, sizes, price, image, line_sheet_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (style, color, description, sizes, price, image_url, line_sheet_id)
                )
            
            return redirect(url_for('view_line_sheet', filename=line_sheet_filename))
        
        except Exception as e:
            logging.error(f"Error processing Excel file: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/line_sheets')
def line_sheets():
    # This route should also be accessible without authentication
    title = request.args.get('title', 'MINKAS LINE SHEETS')
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    # Convert SQLite row objects to plain lists for JSON serialization
    safe_products = []
    for product in products:
        # Updated to properly check all required fields except line_sheet_id
        if all(product[:-1]):  # Check all fields except the last one (line_sheet_id)
            # Convert product tuple to list
            product_list = list(product)
            safe_products.append(product_list)
    
    # Get the album price list URL
    album_price_list_url = get_album_price_list_url()
    
    return render_template(
        'line_sheets.html', 
        products=safe_products, 
        title=title, 
        album_price_list_url=album_price_list_url
    )

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
                line_sheet_id = line_sheet[0]  # ID is stored in the first column
                
                # Query the database for products associated with this line sheet only
                products = conn.execute(
                    "SELECT * FROM products WHERE line_sheet_id = ?",
                    (line_sheet_id,)
                ).fetchall()
                
                # Convert SQLite row objects to plain lists for JSON serialization
                safe_products = []
                for product in products:
                    if all(product[:-1]):  # Check all fields except line_sheet_id
                        # Convert product tuple to list
                        product_list = list(product)
                        safe_products.append(product_list)
                
                # Get the album price list URL
                album_price_list_url = get_album_price_list_url()
                
                # Render the line_sheets template with the sanitized products data
                return render_template(
                    'line_sheets.html', 
                    products=safe_products, 
                    title=title, 
                    album_price_list_url=album_price_list_url
                )
            else:
                # If no line sheet found in database, return 404
                logging.error(f"Line sheet not found in database: {filename}")
                return "Line sheet not found", 404
    
    except Exception as e:
        logging.error(f"Error rendering line sheet {filename}: {e}")
        return f"Error rendering line sheet: {str(e)}", 500

@app.route('/upload-album-price-list', methods=['POST'])
def upload_album_price_list():
    if 'album_price_list' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['album_price_list']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    # Check if it's a PDF
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'Uploaded file must be a PDF'}), 400
    
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            public_id=f"album_price_list",  # No folder structure in the public_id
            resource_type="raw",  # For non-image files like PDFs
            overwrite=True,
            invalidate=True
        )
        
        # Get the secure URL
        pdf_url = result['secure_url']
        
        # Update the database with the new URL
        with sqlite3.connect("products.db") as conn:
            conn.execute(
                "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
                ('album_price_list_url', pdf_url)
            )
        
        logging.info(f"Album Price List PDF uploaded to Cloudinary: {pdf_url}")
        
        return jsonify({
            'success': True,
            'url': pdf_url
        })
        
    except Exception as e:
        logging.error(f"Error uploading Album Price List to Cloudinary: {e}")
        return jsonify({
            'success': False,
            'error': f"Error uploading Album Price List: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)
