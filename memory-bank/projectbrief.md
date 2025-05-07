# Project Brief: Line Sheet Manager

## Overview
Line Sheet Manager is a web application designed to help fashion businesses create, manage, and share line sheets for their collections. The application allows users to upload product images, import product data from Excel files, and generate professional line sheets that can be shared with buyers and retailers.

## Core Requirements

### User Authentication
- Simple login system with username/password authentication
- Protected routes requiring authentication for admin functions

### Product Management
- Upload and manage product images (webp format)
- Import product data from Excel files
- Support for product details: style number, colors, description, sizes, price
- Apply discounts to products (individual or global percentage discounts)

### Line Sheet Generation
- Create line sheets from product data and images
- Organize products by collection
- Display product details in a visually appealing format
- Support for size ratio display (e.g., S-1, M-2, L-3, XL-2, XXL-1)
- Highlight special sizes and display total quantities

### Image Management
- Upload individual product images
- Bulk upload of collection images
- Integration with Cloudinary for image storage and optimization
- Skip duplicate image uploads to prevent redundancy

### Sharing and Viewing
- View generated line sheets in browser
- Share line sheets via URLs
- Responsive design for viewing on different devices
- Interactive gallery view for product images

## Technical Requirements

### Backend
- Python Flask web framework
- SQLite database for data storage
- Pandas for Excel file processing
- Cloudinary integration for image hosting

### Frontend
- HTML/CSS for structure and styling
- JavaScript for interactive features
- Responsive design with mobile support
- Dark/light mode toggle
- TailwindCSS for styling
- PhotoSwipe for image gallery functionality

### Data Structure
- Products table with fields for style, colors, description, sizes, price, image, line_sheet_id, discount_percent
- Line sheets table with fields for title, filename, created_at
- App settings table for application configuration

## Project Goals
1. Streamline the process of creating and sharing line sheets for fashion collections
2. Provide a user-friendly interface for managing product data and images
3. Optimize image storage and delivery for better performance
4. Support responsive viewing on different devices
5. Enable easy updates and modifications to line sheets
