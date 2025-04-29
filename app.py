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
                        line_sheet_id INTEGER,
                        discount_percent REAL)''')  # Add discount_percent column
        conn.execute('''CREATE TABLE IF NOT EXISTS line_sheets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        filename TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS app_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE,
                        value TEXT)''')
        
        # Check if columns exist in the products table
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add line_sheet_id column if it doesn't exist
        if 'line_sheet_id' not in columns:
            conn.execute("ALTER TABLE products ADD COLUMN line_sheet_id INTEGER")
            
        # Add discount_percent column if it doesn't exist
        if 'discount_percent' not in columns:
            conn.execute("ALTER TABLE products ADD COLUMN discount_percent REAL DEFAULT 0")

with app.app_context():
    # Code that requires the application context
    try:
        init_db()
        logging.info("Database initialization completed successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        # Continue running the app even if database initialization fails
        # The routes will handle database errors gracefully

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

def count_uploaded_images():
    """Count the number of products with uploaded images"""
    try:
        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            # Count products with non-empty image field
            cursor.execute("SELECT COUNT(*) FROM products WHERE image IS NOT NULL AND image != ''")
            total_count = cursor.fetchone()[0]
            return total_count
    except Exception as e:
        logging.error(f"Error counting uploaded images: {e}")
        return 0

def count_collection_images(collection_name):
    """Count images uploaded for a specific collection"""
    try:
        with sqlite3.connect("products.db") as conn:
            cursor = conn.cursor()
            # Count images where the URL contains the collection name
            cursor.execute("SELECT COUNT(*) FROM products WHERE image LIKE ?", (f'%/{collection_name}/%',))
            collection_count = cursor.fetchone()[0]
            return collection_count
    except Exception as e:
        logging.error(f"Error counting collection images: {e}")
        return 0

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    # Make sure we include all columns including discount_percent
    # products = [(id, style, colors, description, sizes, price, image if image else '') 
    #            for id, style, colors, description, sizes, price, image, line_sheet_id, discount_percent in products]
    
    # Get image upload count
    uploaded_count = count_uploaded_images()
    
    return render_template('index.html', products=products, uploaded_count=uploaded_count)

# Add this helper function to check if an image already exists in Cloudinary
def image_exists_in_cloudinary(public_id):
    """Check if image with given public_id already exists in Cloudinary"""
    try:
        # Try to get image information from Cloudinary
        cloudinary.api.resource(public_id)
        # If no exception is raised, the image exists
        return True
    except Exception as e:
        if "not found" in str(e).lower():
            # Resource doesn't exist
            return False
        else:
            # Some other error occurred
            logging.error(f"Error checking if image exists in Cloudinary: {e}")
            # Assume it doesn't exist if we couldn't check
            return False

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "No image part in the request.", 400
    file = request.files['image']
    if file.filename == '':
        return "No selected file.", 400
    # Get the style number
    style = request.form.get('style', '')
    collection_name = request.form.get('collection_name', '').strip()
    if not style:
        return "Style number is required for image upload.", 400
    if file:
        try:
            # Get original filename for reference
            original_filename = secure_filename(file.filename)
            logging.info(f"Processing file: {original_filename}, style: {style}")
            # First, always try to remove PICTURES prefix regardless of case or separator
            clean_style = re.sub(r'(?i)pictures[_-]?', '', style)
            
            # Extract just the style code if it matches the pattern (like CM-720)
            style_match = re.search(r'([A-Z]{1,3}[-_]?\d{1,4})', clean_style)
            if style_match:
                clean_style = style_match.group(1)
                logging.info(f"Style code extracted: {clean_style}")
            else:
                logging.info(f"No style code pattern found, using cleaned style: {clean_style}")
            
            # Double-check there's no PICTURES prefix left
            if re.search(r'(?i)pictures', clean_style):
                logging.warning(f"PICTURES still in style after cleanup: {clean_style}")
                clean_style = re.sub(r'(?i)pictures[_-]?', '', clean_style)
            # Get original filename for reference
            # Upload to Cloudinary without collection name folder
            public_id = clean_style
            logging.info(f"Final public_id for upload: {public_id}")
            
            # Check if image already exists in Cloudinary
            if image_exists_in_cloudinary(public_id):
                logging.info(f"Style {public_id} already uploaded to Cloudinary - skipping upload")
                
                # Get the URL for the existing image
                image_url = get_cloudinary_url(
                    public_id,
                    transformation={
                        'quality': 'auto',
                        'fetch_format': 'auto'
                    }
                )
                
                if not image_url:
                    raise Exception("Failed to generate Cloudinary URL for existing image")
                
                # Update the database with the existing Cloudinary URL
                with sqlite3.connect("products.db") as conn:
                    conn.execute(
                        "UPDATE products SET image = ? WHERE style = ?",
                        (image_url, style)
                    )
                
                logging.info(f"Image already in Cloudinary, database updated with URL")
                return redirect(url_for('index'))
            
            # If image doesn't exist, proceed with upload
            result = cloudinary.uploader.upload(
                file,
                public_id=public_id,
                resource_type="image",
                format="webp",
                overwrite=True,
                invalidate=True
            )
            
            # Get the secure URL with proper transformations
            image_url = get_cloudinary_url(
                public_id,
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
            
            # Get updated count after upload
            uploaded_count = count_uploaded_images()
            flash(f"Image uploaded successfully! Total images: {uploaded_count}")
                
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
    
    # Handle global discount if applied
    apply_global_discount = request.form.get('apply_global_discount') == 'true'
    global_discount_percent = 0
    if apply_global_discount:
        try:
            global_discount_percent = float(request.form.get('global_discount_percent', 0))
            logging.info(f"Applying global discount of {global_discount_percent}%")
        except (ValueError, TypeError):
            global_discount_percent = 0
            logging.warning("Invalid discount percentage provided")
    
    if not title or not collection_name:
        return jsonify({'success': False, 'error': 'Title and Collection Name are required'}), 400
    
    uploaded_count = 0
    errors = []
    collection_products = []
    
    # Get initial count before upload
    initial_count = count_uploaded_images()
    
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
    
        for file in files:
            if file.filename == '':
                continue
                
            try:
                # Get original filename for reference
                original_filename = secure_filename(file.filename)
                logging.info(f"Processing file: {original_filename}")
                
                # Clean up the filename - remove spaces and special characters
                clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', original_filename.rsplit('.', 1)[0])
                
                # Extract just the style code if it matches the pattern (like CM-720)
                style_match = re.search(r'([A-Z]{1,3}[-_]?\d{1,4})', clean_name)
                if style_match:
                    # Use just the style code if found
                    clean_name = style_match.group(1)
                    logging.info(f"Style code extracted: {clean_name}")
                else:
                    # Remove any collection name prefix
                    collection_prefix = collection_name.replace(' ', '_').lower() + '_'
                    if clean_name.lower().startswith(collection_prefix):
                        clean_name = clean_name[len(collection_prefix):]
                    logging.info(f"No style code pattern found, using cleaned name: {clean_name}")
                
                # Double-check there's no PICTURES prefix left
                if re.search(r'(?i)pictures', clean_name):
                    logging.warning(f"PICTURES still in name after cleanup: {clean_name}")
                    clean_name = re.sub(r'(?i)pictures[_-]?', '', clean_name)
                
                # Make sure name is unique by adding timestamp if needed
                if not clean_name or clean_name.lower() == collection_name.lower():
                    timestamp = int(datetime.now().timestamp())
                    clean_name = f"{timestamp}"  # Fallback to timestamp if no valid name found
                    logging.warning(f"Using generated name: {clean_name}")
                
                public_id = clean_name
                logging.info(f"Final public_id for upload: {public_id}")
                
                # Check if image already exists in Cloudinary
                if image_exists_in_cloudinary(public_id):
                    logging.info(f"Style {public_id} already uploaded to Cloudinary - skipping upload")
                    
                    # Get the URL for the existing image
                    image_url = get_cloudinary_url(
                        public_id,
                        transformation={
                            'quality': 'auto',
                            'fetch_format': 'auto'
                        }
                    )
                    
                    if not image_url:
                        logging.error(f"Failed to generate Cloudinary URL for existing image {public_id}")
                        continue  # Skip this file
                        
                    # Create a product entry for this collection
                    product = {
                        'style': clean_name,
                        'image': image_url,
                        'colors': '',
                        'description': '',
                        'sizes': '',
                        'price': '',
                        'line_sheet_id': line_sheet_id,
                        'discount_percent': global_discount_percent if apply_global_discount else 0
                    }
                    collection_products.append(product)
                    
                    # Update the database - USING THE EXISTING CONNECTION
                    # Don't create a new connection here to avoid database locks
                    conn.execute(
                        "INSERT OR REPLACE INTO products (style, image, colors, description, sizes, price, line_sheet_id, discount_percent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (clean_name, image_url, '', '', '', '', line_sheet_id, global_discount_percent if apply_global_discount else 0)
                    )
                    
                    uploaded_count += 1
                    continue  # Skip to next file
                
                # If image doesn't exist, proceed with upload
                result = cloudinary.uploader.upload(
                    file,
                    public_id=public_id,
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
                    'style': clean_name,
                    'image': image_url,
                    'colors': '',
                    'description': '',
                    'sizes': '',
                    'price': '',
                    'line_sheet_id': line_sheet_id  # Associate with the specific line sheet
                }
                collection_products.append(product)
                
                # Update the database - USING THE EXISTING CONNECTION
                # Don't create a new connection here either
                conn.execute(
                    "INSERT OR REPLACE INTO products (style, image, colors, description, sizes, price, line_sheet_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (clean_name, image_url, '', '', '', '', line_sheet_id)
                )
                
                uploaded_count += 1
                
            except Exception as e:
                errors.append(f"Error uploading {original_filename}: {str(e)}")
                logging.error(f"Error uploading {original_filename}: {e}")
        
        if uploaded_count == 0 and errors:
            return jsonify({'success': False, 'error': '; '.join(errors)}), 500
        
        # Get final count after all uploads
        final_count = count_uploaded_images()
        collection_count = count_collection_images(collection_name)
        
        return jsonify({
            'success': True,
            'uploaded_count': uploaded_count,
            'total_count': final_count,
            'collection_count': collection_count,
            'line_sheet_url': url_for('view_line_sheet', filename=line_sheet_filename),
            'errors': errors if errors else None
        })

@app.route('/upload-excel', methods=['POST'])
def upload_excel():
    if 'excel' not in request.files:
        return jsonify({'success': False, 'error': 'Missing required files'}), 400
    
    excel_file = request.files['excel']
    if excel_file.filename == '':
        return jsonify({'success': False, 'error': 'No selected files'}), 400
    
    # Check file types - added .xlsm support
    if not excel_file.filename.lower().endswith(('.xlsx', '.xls', '.xlsm')):
        return jsonify({'success': False, 'error': 'Invalid file formats'}), 400
    
    title = request.form.get('title', '').strip().upper()  # Convert title to uppercase
    collection_name = request.form.get('collection_name', '').strip()
    
    # Handle global discount if applied
    apply_global_discount = request.form.get('apply_global_discount') == 'true'
    global_discount_percent = 0
    if apply_global_discount:
        try:
            global_discount_percent = float(request.form.get('global_discount_percent', 0))
            logging.info(f"Applying global discount of {global_discount_percent}%")
        except (ValueError, TypeError):
            global_discount_percent = 0
            logging.warning("Invalid discount percentage provided")
    
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
                
                # Use row discount or global discount if applied
                row_discount = float(row.get('DISCOUNT', 0)) if not pd.isna(row.get('DISCOUNT', 0)) else 0
                discount_percent = row_discount
                
                # Apply global discount if specified and no row-specific discount
                if apply_global_discount and global_discount_percent > 0:
                    discount_percent = global_discount_percent
                    logging.info(f"Applied {discount_percent}% discount to product {style}")
                
                # Skip empty rows
                if not style:
                    continue
                
                # Check if image exists in Cloudinary for this style
                try:
                    image_url = get_cloudinary_url(f"{style}")  # No folder structure
                except Exception as e:
                    logging.error(f"Error getting Cloudinary URL for {style}: {e}")
                    image_url = ''
                
                # Insert into database with line_sheet_id and discount_percent
                conn.execute(
                    "INSERT INTO products (style, colors, description, sizes, price, image, line_sheet_id, discount_percent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (style, color, description, sizes, price, image_url, line_sheet_id, discount_percent)
                )
            
            return redirect(url_for('view_line_sheet', filename=line_sheet_filename))
        except Exception as e:
            logging.error(f"Error processing Excel file: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/line_sheets')
def line_sheets():
    title = request.args.get('title', '').strip()

    # Redirect specifically for this collection
    if title.upper() == 'MINKAS FALL/WINTER 2025':
        return redirect('https://minkas-fw25.onrender.com/view_line_sheet/minkas_fall_winter_2025.html', code=301)
    
    # Extract collection name from title for image mapping
    collection_name = title.strip().split()[0] if title and ' ' in title else None
    
    with sqlite3.connect("products.db") as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    # Convert SQLite row objects to plain lists for JSON serialization
    safe_products = []
    for product in products:
        # Only check if style number exists, allow other fields to be empty
        if product[1]:  # Style is at index 1
            # Convert product tuple to list
            product_list = list(product)
            
            # Get style number and check image URL
            style_number = product_list[1]
            image_url = product_list[6]
            
            # If image URL is empty or doesn't include a valid Cloudinary path, try to construct it
            if not image_url or 'cloudinary' not in image_url:
                # Try to get Cloudinary URL using just the style number without collection prefix
                try:
                    clean_style = re.sub(r'(?i)pictures[_-]?', '', style_number)
                    public_id = clean_style  # Use style number directly
                    new_url = get_cloudinary_url(
                        public_id,
                        transformation={
                            'quality': 'auto',
                            'fetch_format': 'auto'
                        }
                    )
                    if new_url:
                        product_list[6] = new_url
                        logging.info(f"Updated image URL for {style_number} to {new_url}")
                        # Update database with new URL
                        conn.execute(
                            "UPDATE products SET image = ? WHERE id = ?",
                            (new_url, product_list[0])
                        )
                except Exception as e:
                    logging.error(f"Error generating Cloudinary URL for {style_number}: {e}")
            safe_products.append(product_list)
    
    return render_template(
        'line_sheets.html', 
        products=safe_products, 
        title=title,
        album_price_list_url="#"  # Add dummy value for template compatibility
    )

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
                
                # Extract collection name from title for image mapping
                collection_name = title.strip().split()[0] if title and ' ' in title else None
                
                # Convert SQLite row objects to plain lists for JSON serialization
                safe_products = []
                for product in products:
                    # Only check if style number exists, allow other fields to be empty
                    if product[1]:  # Style is at index 1
                        # Convert product tuple to list
                        product_list = list(product)
                        
                        # Get style number and check image URL
                        style_number = product_list[1]
                        image_url = product_list[6]
                        
                        # If image URL is empty or doesn't include a valid Cloudinary path, try to construct it
                        if not image_url or 'cloudinary' not in image_url:
                            # Try to get Cloudinary URL using just the style number
                            try:
                                clean_style = re.sub(r'(?i)pictures[_-]?', '', style_number)
                                public_id = clean_style  # Use style number directly
                                new_url = get_cloudinary_url(
                                    public_id,
                                    transformation={
                                        'quality': 'auto',
                                        'fetch_format': 'auto'
                                    }
                                )
                                if new_url:
                                    product_list[6] = new_url
                                    logging.info(f"Updated image URL for {style_number} to {new_url}")
                                    # Update database with new URL
                                    conn.execute(
                                        "UPDATE products SET image = ? WHERE id = ?",
                                        (new_url, product_list[0])
                                    )
                            except Exception as e:
                                logging.error(f"Error generating Cloudinary URL for {style_number}: {e}")
                        
                        # Calculate discounted price if discount_percent exists
                        discount_percent = product_list[8] if len(product_list) > 8 else 0
                        price = product_list[5]
                        
                        # Add discounted price to the product data if discount is applied
                        if price and discount_percent and float(discount_percent) > 0:
                            try:
                                # Extract numeric price (handle currency symbols)
                                price_str = price.strip()
                                numeric_price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_str)))
                                
                                # Calculate discounted price
                                discounted_price = numeric_price * (1 - float(discount_percent)/100)
                                
                                # Format with same currency symbol if present
                                currency_symbol = ''.join(c for c in price_str if not (c.isdigit() or c == '.'))
                                formatted_discount = f"{currency_symbol}{discounted_price:.2f}"
                                
                                # Add to product list
                                product_list.append(formatted_discount)
                            except (ValueError, TypeError):
                                product_list.append("")
                        else:
                            product_list.append("")
                                
                        safe_products.append(product_list)
                
                # Render the line_sheets template with the sanitized products data
                return render_template(
                    'line_sheets.html', 
                    products=safe_products, 
                    title=title,
                    album_price_list_url="#"  # Add dummy value for template compatibility
                )
            else:
                # If no line sheet found in database, return 404
                logging.error(f"Line sheet not found in database: {filename}")
                return "Line sheet not found", 404
    except Exception as e:
        logging.error(f"Error rendering line sheet {filename}: {e}")
        return f"Error rendering line sheet: {str(e)}", 500

@app.route('/list_line_sheets')
def list_line_sheets():
    # This route should also be accessible without authentication
    with sqlite3.connect("products.db") as conn:
        line_sheets = conn.execute("SELECT * FROM line_sheets ORDER BY created_at DESC").fetchall()
    
    # Add a dummy album_price_list_url to maintain template compatibility
    return render_template('list_line_sheets.html', line_sheets=line_sheets, album_price_list_url="#")

@app.route('/update-discount', methods=['POST'])
def update_discount():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
    try:
        product_id = request.form.get('product_id')
        discount_percent = request.form.get('discount_percent', 0)
        
        # Convert discount to float or set to 0 if invalid
        try:
            discount_percent = float(discount_percent)
        except (ValueError, TypeError):
            discount_percent = 0
            
        with sqlite3.connect("products.db") as conn:
            conn.execute(
                "UPDATE products SET discount_percent = ? WHERE id = ?",
                (discount_percent, product_id)
            )
            
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error updating discount: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
