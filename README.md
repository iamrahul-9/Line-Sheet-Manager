# Line Sheet Manager

A web application to manage line sheets for fashion collections with Cloudinary image storage.

## Recent Changes

### Updates (Current Date)

- **Cloudinary Upload Optimization**: Added check to skip uploading images that already exist in Cloudinary to prevent duplicate uploads
- **PDF Handling Improvement**: Fixed album price list PDF handling to preserve original filenames and correctly include .pdf extension
- **Bug Fixes**: 
  - Fixed syntax errors in Python code (list comprehension issues)
  - Fixed issue where album price lists were overwriting each other
  - Improved error handling and logging for image and PDF uploads

## Changelog

### April 8, 2024
- Migrated to Cloudinary for image hosting:
  - Added Cloudinary integration for image storage and delivery
  - Created migration script for existing images
  - Updated image handling to use Cloudinary URLs
  - Improved image loading performance through CDN
  - Added automatic image optimization
  - Maintained style number mapping in cloud storage

- Enhanced size display functionality:
  - Added support for size ratio display (e.g., S-1, M-2, L-3)
  - Implemented automatic size parsing and formatting
  - Added total quantity calculation
  - Maintained backward compatibility with standard size ranges

- UI Improvements:
  - Added Font Awesome icons for product details
  - Enhanced visual hierarchy in product cards
  - Improved responsive design for size displays

### April 7, 2024
- Optimized project structure by removing redundant file storage:
  - Removed `seed_data` directory and simplified file organization
  - Modified application to use Excel file directly from `static` directory
  - Eliminated duplicate image storage by using direct references to `static/uploads`
  - Updated configuration to use actual filenames instead of copies

- Added favicon support:
  - Created and added SVG favicon
  - Added ICO format favicon
  - Updated base template to include favicon

- Improved line sheet title:
  - Changed default line sheet title to "MINKAS FALL/WINTER 2025"
  - Updated seed data loading process to use the new title

### April 4, 2024
- Environment and deployment improvements:
  - Set up virtual environment for dependency management
  - Added requirements.txt with specific package versions
  - Configured Flask debug mode for development

### April 3, 2024
- Initial project setup:
  - Created Flask application with user authentication
  - Implemented SQLite database for product storage
  - Added support for image uploads (.webp format)
  - Created Excel file processing functionality
  - Set up basic templates and static file serving
  - Added line sheet generation feature
  - Implemented product management system

### Features

- Upload and manage product images
- Generate line sheets from Excel data
- Upload image directories in bulk
- Store album price lists as PDFs
- View and share line sheets

- User authentication system
- Excel file processing for product data
- Image upload and management (.webp format)
- Dynamic line sheet generation
- Responsive web interface
- SQLite database for data persistence
- Automatic seed data loading for initial setup

## Setup & Usage

[Include setup and usage instructions here]

### Tech Stack
- Python Flask for backend
- SQLite for database
- Pandas for Excel processing
- Werkzeug for file handling
- Jinja2 for templating
- HTML/CSS for frontend
