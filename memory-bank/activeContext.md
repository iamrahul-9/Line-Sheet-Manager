# Active Context: Line Sheet Manager

## Current Work Focus

The Line Sheet Manager project is currently focused on enhancing the user experience and adding new features to improve the functionality of the application. The main areas of focus are:

1. **Product Sorting Feature**: Recently implemented sorting capabilities for line sheet products, allowing users to sort by style number, price, and quantity.

2. **Discount Management**: Added support for applying percentage discounts to products, both globally and individually.

3. **UI/UX Improvements**: Ongoing enhancements to the user interface to improve usability and visual appeal.

4. **Image Management Optimization**: Optimizing the image upload and storage process using Cloudinary integration.

## Recent Changes

### Product Sorting Feature (April 28, 2025)
- Added dropdown with sorting options (style number, price, quantity)
- Implemented client-side sorting functionality using JavaScript
- Created responsive sorting UI that adapts to mobile screens
- Added visual feedback during sorting operations

### Discount Feature (April 22, 2025)
- Implemented discount toggle UI in product creation form
- Added support for global discount application to all products in a line sheet
- Enhanced line sheet display to show crossed-out original prices with discounted prices
- Updated database schema to include discount_percent field

### UI Improvements (April 22, 2025)
- Enhanced Home button with bold text and improved styling
- Fixed file upload display to show filenames in a single line with ellipsis
- Standardized button corner radius across the application
- Fixed spacing between price and currency symbols

### Cloudinary Integration (April 15, 2025)
- Added check to skip uploading images that already exist in Cloudinary
- Improved error handling and logging for image uploads
- Optimized image delivery through Cloudinary CDN

## Next Steps

1. **Enhanced Image Management**
   - Implement image cropping and resizing tools
   - Add support for image reordering within line sheets
   - Improve image upload progress indicators

2. **Export Functionality**
   - Add PDF export option for line sheets
   - Implement email sharing of line sheets
   - Create printable version of line sheets

3. **User Management**
   - Implement user roles and permissions
   - Add multi-user support with separate accounts
   - Enhance authentication security

4. **Performance Optimization**
   - Optimize database queries for larger datasets
   - Implement pagination for line sheet viewing
   - Add caching for frequently accessed data

## Active Decisions and Considerations

### Architecture Decisions

1. **Single App File vs. Module Structure**
   - Currently using a single app.py file for simplicity
   - Considering refactoring into a modular structure as the application grows
   - Decision pending based on future feature requirements

2. **Database Choice**
   - Currently using SQLite for simplicity and ease of deployment
   - May need to consider migration to PostgreSQL if user base grows
   - Monitoring performance to determine if/when migration is necessary

3. **Frontend Framework**
   - Currently using vanilla JavaScript with TailwindCSS
   - Evaluating whether to introduce a frontend framework like Vue.js or React
   - Decision will depend on complexity of future UI requirements

### Technical Debt

1. **Code Organization**
   - The app.py file is becoming large and could benefit from refactoring
   - Need to separate concerns into modules (routes, models, services)
   - Consider implementing a proper ORM for database interactions

2. **Testing**
   - No automated tests currently implemented
   - Need to add unit tests for critical functionality
   - Consider implementing integration tests for key user flows

3. **Error Handling**
   - Current error handling is basic and could be improved
   - Need to implement more robust error reporting and recovery
   - Consider adding a logging service for better monitoring

## Important Patterns and Preferences

### Code Style

- **Python**: Following PEP 8 style guidelines
- **JavaScript**: Using ES6+ features with consistent formatting
- **HTML/CSS**: Using TailwindCSS utility classes with consistent structure

### Design Patterns

- **Component-Based UI**: Building reusable UI components
- **Service Pattern**: Encapsulating business logic in service functions
- **Repository Pattern**: Centralizing database access

### User Experience Preferences

- **Responsive Design**: All features must work well on mobile and desktop
- **Progressive Enhancement**: Core functionality should work without JavaScript
- **Visual Feedback**: Provide clear feedback for user actions
- **Dark/Light Mode**: Support both dark and light mode preferences

## Learnings and Project Insights

### What's Working Well

1. **Cloudinary Integration**: The move to Cloudinary has significantly improved image loading performance and reduced server storage requirements.

2. **Excel Import**: The Excel import functionality is working efficiently and provides a good user experience for bulk data entry.

3. **Responsive Design**: The application works well across different devices and screen sizes.

### Challenges and Solutions

1. **Challenge**: Large image uploads causing timeouts
   **Solution**: Implemented client-side chunking and progress indicators

2. **Challenge**: Complex sorting requirements for products
   **Solution**: Implemented client-side sorting with multiple criteria

3. **Challenge**: Maintaining consistent styling across the application
   **Solution**: Adopted TailwindCSS and created reusable component classes

### User Feedback

1. **Positive Feedback**:
   - Users appreciate the clean, modern interface
   - The image gallery functionality is highly valued
   - The discount feature has been well-received

2. **Areas for Improvement**:
   - Some users have requested bulk editing capabilities
   - Export to PDF functionality is frequently requested
   - Some users would like more customization options for line sheet appearance
