# System Patterns: Line Sheet Manager

## System Architecture

The Line Sheet Manager follows a traditional web application architecture with a clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Presentation   │◄────┤    Business     │◄────┤     Data        │
│     Layer       │     │     Layer       │     │     Layer       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Presentation Layer
- Flask templates (Jinja2) for HTML rendering
- TailwindCSS for styling
- JavaScript for client-side interactivity
- PhotoSwipe library for image gallery functionality

### Business Layer
- Flask routes and controllers
- Business logic for processing uploads, generating line sheets
- Authentication and authorization

### Data Layer
- SQLite database for persistent storage
- Cloudinary for image storage and delivery
- File system for temporary storage during processing

## Key Technical Decisions

### 1. Flask Web Framework
- **Decision**: Use Flask as the web framework
- **Rationale**: Lightweight, flexible, and well-suited for small to medium applications
- **Impact**: Enables rapid development with minimal boilerplate code

### 2. SQLite Database
- **Decision**: Use SQLite for data storage
- **Rationale**: Simple setup, no separate server required, suitable for the application's data volume
- **Impact**: Simplifies deployment and maintenance

### 3. Cloudinary Integration
- **Decision**: Use Cloudinary for image storage and delivery
- **Rationale**: Provides CDN capabilities, image optimization, and transformation features
- **Impact**: Improves image loading performance and reduces server storage requirements

### 4. Client-Side Rendering
- **Decision**: Use client-side JavaScript for interactive features
- **Rationale**: Provides better user experience for features like sorting and filtering
- **Impact**: More responsive UI without full page reloads

### 5. Responsive Design
- **Decision**: Implement responsive design using TailwindCSS
- **Rationale**: Ensures usability across different devices and screen sizes
- **Impact**: Broadens accessibility of the application

## Design Patterns

### MVC Pattern
The application follows the Model-View-Controller pattern:
- **Models**: Database tables (products, line_sheets, app_settings)
- **Views**: Jinja2 templates (base.html, index.html, line_sheets.html, etc.)
- **Controllers**: Flask routes in app.py

### Factory Pattern
Used for creating line sheets and processing uploads:
- Encapsulates the creation logic
- Provides a consistent interface for creating different types of objects

### Repository Pattern
Implemented through SQLite database interactions:
- Centralizes data access logic
- Abstracts database operations from business logic

### Observer Pattern
Used for handling asynchronous operations:
- File uploads trigger progress updates
- Image processing events update the UI

### Strategy Pattern
Applied to sorting functionality:
- Different sorting algorithms are encapsulated in separate functions
- The appropriate strategy is selected based on user choice

## Component Relationships

```
┌───────────────────────────────────────────────────────────────┐
│                        Flask Application                      │
│                                                               │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │             │      │             │      │             │    │
│  │   Routes    │◄────►│  Services   │◄────►│   Models    │    │
│  │             │      │             │      │             │    │
│  └─────────────┘      └─────────────┘      └──────┬──────┘    │
│         │                                         │           │
└─────────┼─────────────────────────────────────────┼───────────┘
          │                                         │
          ▼                                         ▼
┌─────────────────┐                       ┌─────────────────┐
│                 │                       │                 │
│    Templates    │                       │    Database     │
│                 │                       │                 │
└─────────────────┘                       └─────────────────┘
          │                                         │
          │                                         │
          ▼                                         ▼
┌─────────────────┐                       ┌─────────────────┐
│                 │                       │                 │
│  Client-Side JS │                       │   Cloudinary    │
│                 │                       │                 │
└─────────────────┘                       └─────────────────┘
```

### Key Components

#### 1. Authentication Component
- Handles user login/logout
- Protects routes requiring authentication
- Simple username/password authentication

#### 2. File Processing Component
- Handles Excel file uploads and parsing
- Extracts product data from Excel files
- Maps data to database models

#### 3. Image Management Component
- Processes image uploads
- Integrates with Cloudinary for storage
- Handles image optimization and delivery

#### 4. Line Sheet Generation Component
- Creates line sheets from product data and images
- Generates HTML representations of line sheets
- Handles sorting and filtering of products

#### 5. User Interface Component
- Renders templates with product data
- Provides interactive features (sorting, filtering)
- Implements responsive design for different devices

## Critical Implementation Paths

### 1. Line Sheet Creation Path
```
Excel Upload → Parse Data → Match Images → Generate Line Sheet → Save to Database → Render View
```

### 2. Image Processing Path
```
Image Upload → Validate → Process → Upload to Cloudinary → Update Database → Display in UI
```

### 3. Line Sheet Viewing Path
```
Request Line Sheet → Retrieve from Database → Load Products → Render Template → Client-side Enhancements
```

### 4. Authentication Path
```
Login Request → Validate Credentials → Create Session → Redirect to Protected Route
```
