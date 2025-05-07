# Technical Context: Line Sheet Manager

## Technologies Used

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Primary programming language |
| Flask | 2.0+ | Web framework |
| PostgreSQL | 15.x | Database |
| Pandas | 1.3+ | Excel file processing |
| Werkzeug | 2.0+ | File handling and utilities |
| Jinja2 | 3.0+ | HTML templating |
| Cloudinary | 1.29+ | Image storage and CDN |
| Gunicorn | 20.1+ | WSGI HTTP Server for production |
| python-dotenv | 0.19+ | Environment variable management |

### Frontend

| Technology | Purpose |
|------------|---------|
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript (ES6+) | Client-side interactivity |
| TailwindCSS | CSS framework |
| PhotoSwipe | Image gallery functionality |
| Font Awesome | Icons |

## Development Setup

### Local Development Environment

1. **Python Environment**:
   - Python 3.9 or higher
   - Virtual environment (venv or conda)
   - Dependencies installed via pip from requirements.txt

2. **Database**:
   - SQLite database (products.db)
   - Created automatically on application startup
   - No separate database server required

3. **Configuration**:
   - Environment variables for sensitive information
   - Debug mode enabled for development

4. **Running the Application**:
   ```bash
   # Set up virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python app.py
   ```

### Development Workflow

1. **Code Organization**:
   - Single app.py file for routes and application logic
   - Templates in /templates directory
   - Static assets in /static directory
   - Uploaded files in /static/uploads directory

2. **Database Schema Management**:
   - Schema defined and updated in init_db() function
   - Automatic migration of schema changes on application startup

3. **Testing**:
   - Manual testing through the web interface
   - No automated tests currently implemented

## Technical Constraints

### Performance Constraints

1. **Image Processing**:
   - Image uploads limited by server memory and processing capacity
   - Large batch uploads may cause timeouts or memory issues
   - Cloudinary free tier has usage limits

2. **Database**:
   - SQLite has concurrency limitations (single writer at a time)
   - Not suitable for high-volume concurrent writes
   - Performance may degrade with very large datasets

3. **Server Resources**:
   - Limited by hosting environment (CPU, memory, disk space)
   - File uploads constrained by server disk space

### Security Constraints

1. **Authentication**:
   - Simple username/password authentication
   - No multi-factor authentication
   - No password recovery mechanism

2. **Data Protection**:
   - No encryption for data at rest
   - Session management via Flask's built-in session mechanism
   - CSRF protection not explicitly implemented

3. **API Security**:
   - No rate limiting implemented
   - No API authentication for public endpoints

### Scalability Constraints

1. **Database Scalability**:
   - SQLite is file-based and has limited scalability
   - Not suitable for distributed deployment

2. **Application Architecture**:
   - Monolithic design limits horizontal scaling
   - No separation of services for independent scaling

3. **Deployment**:
   - Single server deployment model
   - No load balancing or clustering

## Dependencies

### Direct Dependencies

```
Flask==2.0.1
Werkzeug==2.0.1
pandas==1.3.3
openpyxl==3.0.9
Jinja2==3.0.1
cloudinary==1.29.0
gunicorn==20.1.0
python-dotenv==0.19.1
```

### Indirect Dependencies

- **Flask Dependencies**:
  - click
  - itsdangerous
  - MarkupSafe

- **Pandas Dependencies**:
  - numpy
  - python-dateutil
  - pytz
  - six

- **Openpyxl Dependencies**:
  - et-xmlfile

### Frontend Dependencies (CDN)

- TailwindCSS (via CDN)
- PhotoSwipe (via CDN)
- Font Awesome (via CDN)
- Google Fonts (Poppins)

## Tool Usage Patterns

### Database Interaction

```python
# Connection pattern
with sqlite3.connect("products.db") as conn:
    # Execute queries
    conn.execute("SQL QUERY HERE", (param1, param2))
    
    # Fetch results
    results = conn.execute("SELECT QUERY").fetchall()
```

### File Upload Handling

```python
# File upload pattern
if 'file' in request.files:
    file = request.files['file']
    if file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
```

### Cloudinary Integration

```python
# Cloudinary upload pattern
result = cloudinary.uploader.upload(
    file,
    public_id=public_id,
    resource_type="image",
    format="webp",
    overwrite=True,
    invalidate=True
)

# Cloudinary URL generation
image_url = get_cloudinary_url(
    public_id,
    transformation={
        'quality': 'auto',
        'fetch_format': 'auto'
    }
)
```

### Excel Processing

```python
# Excel processing pattern
df = pd.read_excel(excel_file)
for _, row in df.iterrows():
    # Extract data from row
    style = str(row.get('STYLE#', ''))
    color = str(row.get('COLOR', ''))
    # Process data...
```

### Template Rendering

```python
# Template rendering pattern
return render_template(
    'template_name.html',
    products=products,
    title=title,
    additional_data=additional_data
)
```

## Deployment Considerations

### Hosting Environment

- Deployed on Render.com or similar PaaS
- Single web service instance
- Environment variables for configuration
- Automatic deployment from Git repository

### Production Configuration

- Debug mode disabled
- Gunicorn as WSGI server
- Static files served through CDN when possible
- Database backup strategy needed

### Performance Optimization

- Cloudinary for image optimization and delivery
- Client-side caching for static assets
- Minimized JavaScript and CSS
- Lazy loading for images
