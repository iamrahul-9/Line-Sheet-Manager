# Line Sheet Manager Documentation

This document provides a detailed guide on how to set up, use, and understand the Line Sheet Manager application.

## 1. Project Overview

The Line Sheet Manager is a web application built with Flask that allows users to create, manage, and view line sheets for fashion collections. It's designed to streamline the process of generating line sheets from Excel data and product images. The application uses Cloudinary for cloud-based image storage and management, ensuring high performance and optimized image delivery.

## 2. Tech Stack

The application is built with the following technologies:

*   **Backend:** Python with Flask web framework.
*   **Database:** SQLite for lightweight and serverless data storage.
*   **Image Storage:** Cloudinary for cloud-based image hosting, optimization, and delivery.
*   **Frontend:** HTML, CSS, and JavaScript with Tailwind CSS for styling and a responsive UI.
*   **Templating:** Jinja2 for dynamically generating HTML pages.
*   **Excel Processing:** Pandas library for reading and processing data from Excel files.
*   **Deployment:** Can be deployed on services like Heroku, Render, or any server that supports Python applications.

## 3. Setup and Installation

To run the Line Sheet Manager locally, follow these steps:

### Prerequisites

*   Python 3.x installed on your system.
*   `pip` for package management.

### Installation Steps

1.  **Clone the repository or download the source code:**

    ```bash
    git clone <repository-url>
    cd Line-Sheet-Manager-main
    ```

2.  **Create and activate a virtual environment:**

    *   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Cloudinary credentials:**

    The application uses Cloudinary for image management. You'll need to create a free Cloudinary account to get your `cloud_name`, `api_key`, and `api_secret`.

    In `app.py`, locate the Cloudinary configuration section and replace the placeholder values with your actual credentials:

    ```python
    cloudinary.config(
        cloud_name='your_cloud_name',
        api_key='your_api_key',
        api_secret='your_api_secret',
        secure=True,
        cdn_subdomain=True
    )
    ```

5.  **Run the application:**

    ```bash
    python app.py
    ```

    The application will start on `http://127.0.0.1:5000`.

## 4. How to Use the Application

### 4.1. Login

*   Navigate to `http://127.0.0.1:5000/login`.
*   Enter the username and password.
*   Successful login will redirect you to the main dashboard.

### 4.2. Creating a Line Sheet

The main dashboard provides a form to create a new line sheet. Before you begin, you need to prepare an Excel file with your product data.

#### Preparing the Excel Data Sheet

The application reads product data from an Excel file (`.xlsx`, `.xls`, or `.xlsm`). The file must contain a header row with the following column names. The order of columns does not matter.

*   **`STYLE#` (Required):** This is the unique identifier for each product. It is crucial for linking products to their images. For the application to automatically find the correct image, the image filename should match this style number (e.g., an image named `AY-510.webp` will be matched to the product with `STYLE#` "AY-510").

*   **`COLOR` (Recommended):** The color or colorway of the product (e.g., "Black", "Ivory", "Multi").

*   **`PRICE` (Required):** The wholesale price of the product. Enter a numeric value without currency symbols (e.g., `79.50`). The application will format it correctly.

*   **`DISCOUNT` (Optional):** If you want to apply a discount to a specific product, enter the percentage as a number (e.g., `20` for 20%). This will override any global discount you set in the web form.

---

#### Special Columns: `DESCRIPTION` and `SIZES`

The `DESCRIPTION` and `SIZES` columns are special because their content determines whether you are creating a **Catalog Line Sheet** or an **ATS (Available To Sell) Line Sheet**.

##### For a Catalog Line Sheet (Showcasing a New Collection):

*   **`DESCRIPTION` Column:** Use this field to specify the **fabric content**. If the text contains percentages, it will be automatically formatted into a bulleted list.
    *   *Example:* `80% Viscose, 20% Nylon`

*   **`SIZES` Column:** Use this field to define the **standard size range** available for pre-order.
    *   *Example:* `S-XXL`

##### For an ATS Line Sheet (Showing Available Inventory):

*   **`DESCRIPTION` Column:** Use this field to describe the **product type**. Certain keywords like "Reversible" will be automatically highlighted.
    *   *Example:* `Jacket`, `Top`, `Reversible Dress`

*   **`SIZES` Column:** Use this field to list the **actual size ratio** (inventory count per size) as a comma-separated list of numbers. The application expects a sequence corresponding to the standard size run (S, M, L, XL, XXL).
    *   *Example:* `1,2,2,1,0` would indicate 1 Small, 2 Medium, 2 Large, 1 X-Large, and 0 XX-Large are available. This will be displayed in a clean table format on the line sheet.

---

#### Creating the Line Sheet in the App

1.  **Required Information:**
    *   **Line Sheet Title:** Enter a descriptive title for your line sheet (e.g., "FW25 COLLECTION"). This will be the main heading.
    *   **Excel File:** Upload the Excel file you just prepared.

2.  **Optional Image Upload:**
    *   **Collection Name:** Provide a name for the collection (e.g., "FW25"). This is used for organizing images if you upload them in bulk.
    *   **Collection Images:** You can upload multiple product images at once. The application will attempt to match images to products based on the style number in the filename.

3.  **Applying Discounts:**
    *   You can apply a global discount to all products in the line sheet by checking the "Apply Discount" box and entering a percentage.
    *   Alternatively, you can specify discounts for individual products in the `DISCOUNT` column of your Excel file.

4.  **Generate Line Sheet:**
    *   Click the "Generate Line Sheet" button.
    *   If you uploaded images, they will be uploaded to Cloudinary first.
    *   The application will then process the Excel file, create product entries in the database, and generate a new line sheet.
    *   You will be redirected to the list of all line sheets.

### 4.3. Viewing and Searching Line Sheets

*   From the main dashboard, click the "View Line Sheets" button.
*   This will take you to a page listing all the created line sheets.
*   You can use the **search bar** in the header to quickly find a specific line sheet by its title.
*   Click on a line sheet title to view it.
*   The line sheet displays products in a grid. You can use the search bar on this page to find a specific style by its style number.
*   You can click on any product image to open a full-screen gallery view.

### 4.4. Editing and Deleting Line Sheets

*   On the "View Line Sheets" page, each line sheet has "Edit" and "Delete" buttons.
*   **Editing:**
    *   Clicking "Edit" takes you to a page where you can upload a new Excel file to update the product data for that line sheet.
    *   Existing discount settings are preserved during the update.
*   **Deleting:**
    *   Clicking "Delete" will permanently remove the line sheet and all its associated products from the database. A confirmation prompt will appear to prevent accidental deletion.

## 5. Line Sheet Variations: Catalog vs. ATS

The Line Sheet Manager is designed to handle two primary types of line sheets: **Catalog Line Sheets** for showcasing new collections and **ATS (Available To Sell) Line Sheets** for managing available inventory. The key difference lies in how the `DESCRIPTION` and `SIZES` columns in your Excel file are used.

### 5.1. Catalog Line Sheet

A Catalog Line Sheet is used to present a new collection to buyers. It focuses on product details, fabric composition, and available size ranges, accompanied by high-quality images.

*   **Purpose:** To introduce a new collection and take pre-orders.
*   **How to use the special columns:**
    *   **`DESCRIPTION` column:** Use this to specify the **fabric content** of the garment. The application will automatically format descriptions containing percentages (e.g., `80% Cotton, 20% Polyester`) into a clean, bulleted list.
    *   **`SIZES` column:** Use this to define the **standard size range** available for the product (e.g., `S-XXL`). This will be displayed as text.

### 5.2. ATS (Available To Sell) Line Sheet

An ATS Line Sheet is used to show buyers what inventory is currently in stock and available for immediate purchase. It focuses on product types and exact quantity ratios per size.

*   **Purpose:** To sell existing inventory.
*   **How to use the special columns:**
    *   **`DESCRIPTION` column:** Use this to describe the **type of product** (e.g., `Jacket`, `Top`, `Pant`). Special product types like `Reversible Plazzo` will be automatically highlighted.
    *   **`SIZES` column:** Use this to list the **actual size ratio** or quantities available for each size. For example, a value of `1, 2, 2, 1, 0` would be interpreted and displayed in a table as:
        *   S: 1
        *   M: 2
        *   L: 2
        *   XL: 1
        *   XXL: 0
        This provides a clear, at-a-glance view of the available stock for each size.

By using the `DESCRIPTION` and `SIZES` columns strategically, you can create the exact type of line sheet you need for different business purposes.

## 6. Database Schema

The application uses an SQLite database named `products.db` with the following tables:

*   **`products`**: Stores individual product information.
    *   `id`: INTEGER, PRIMARY KEY
    *   `style`: TEXT
    *   `colors`: TEXT
    *   `description`: TEXT
    *   `sizes`: TEXT
    *   `price`: TEXT
    *   `image`: TEXT (URL to the Cloudinary image)
    *   `line_sheet_id`: INTEGER (Foreign key to `line_sheets` table)
    *   `discount_percent`: REAL

*   **`line_sheets`**: Stores information about each line sheet.
    *   `id`: INTEGER, PRIMARY KEY
    *   `title`: TEXT
    *   `filename`: TEXT (The generated HTML filename)
    *   `created_at`: TIMESTAMP

*   **`app_settings`**: For storing application-wide settings (currently not extensively used).
    *   `id`: INTEGER, PRIMARY KEY
    *   `key`: TEXT, UNIQUE
    *   `value`: TEXT

## 7. Key Features

*   **User Authentication:** Secure login system to protect access to the management features.
*   **Dynamic Line Sheet Generation:** Creates HTML line sheets from Excel data.
*   **Cloudinary Integration:** All images are stored and served from Cloudinary's CDN for fast loading and optimization.
*   **Global Search:** Search for line sheets by title and for styles within a line sheet.
*   **Bulk Image Upload:** Upload an entire directory of product images at once.
*   **Discount Management:** Apply global or per-product discounts.
*   **Responsive Design:** The application is usable on both desktop and mobile devices.
*   **Image Gallery:** An interactive, full-screen image gallery (PhotoSwipe) for viewing product images.
*   **Product Sorting:** Sort products in a line sheet by style number, price, or quantity.
*   **Special Highlighting:** Automatically highlights special sizes and descriptions for better visibility.
*   **Dark/Light Mode:** A theme toggle for user preference.

## 5. Line Sheet Variations: Catalog vs. ATS

The Line Sheet Manager is designed to handle two primary types of line sheets: **Catalog Line Sheets** for showcasing new collections and **ATS (Available To Sell) Line Sheets** for managing available inventory. The key difference lies in how the `DESCRIPTION` and `SIZES` columns in your Excel file are used.

### 5.1. Catalog Line Sheet

A Catalog Line Sheet is used to present a new collection to buyers. It focuses on product details, fabric composition, and available size ranges, accompanied by high-quality images.

*   **Purpose:** To introduce a new collection and take pre-orders.
*   **How to use the special columns:**
    *   **`DESCRIPTION` column:** Use this to specify the **fabric content** of the garment. The application will automatically format descriptions containing percentages (e.g., `80% Cotton, 20% Polyester`) into a clean, bulleted list.
    *   **`SIZES` column:** Use this to define the **standard size range** available for the product (e.g., `S-XXL`). This will be displayed as text.

### 5.2. ATS (Available To Sell) Line Sheet

An ATS Line Sheet is used to show buyers what inventory is currently in stock and available for immediate purchase. It focuses on product types and exact quantity ratios per size.

*   **Purpose:** To sell existing inventory.
*   **How to use the special columns:**
    *   **`DESCRIPTION` column:** Use this to describe the **type of product** (e.g., `Jacket`, `Top`, `Pant`). Special product types like `Reversible Plazzo` will be automatically highlighted.
    *   **`SIZES` column:** Use this to list the **actual size ratio** or quantities available for each size. For example, a value of `1, 2, 2, 1, 0` would be interpreted and displayed in a table as:
        *   S: 1
        *   M: 2
        *   L: 2
        *   XL: 1
        *   XXL: 0
        This provides a clear, at-a-glance view of the available stock for each size.

By using the `DESCRIPTION` and `SIZES` columns strategically, you can create the exact type of line sheet you need for different business purposes.

## 6. Database Schema

The application uses an SQLite database named `products.db` with the following tables:

*   **`products`**: Stores individual product information.
    *   `id`: INTEGER, PRIMARY KEY
    *   `style`: TEXT
    *   `colors`: TEXT
    *   `description`: TEXT
    *   `sizes`: TEXT
    *   `price`: TEXT
    *   `image`: TEXT (URL to the Cloudinary image)
    *   `line_sheet_id`: INTEGER (Foreign key to `line_sheets` table)
    *   `discount_percent`: REAL

*   **`line_sheets`**: Stores information about each line sheet.
    *   `id`: INTEGER, PRIMARY KEY
    *   `title`: TEXT
    *   `filename`: TEXT (The generated HTML filename)
    *   `created_at`: TIMESTAMP

*   **`app_settings`**: For storing application-wide settings (currently not extensively used).
    *   `id`: INTEGER, PRIMARY KEY
    *   `key`: TEXT, UNIQUE
    *   `value`: TEXT

## 7. Key Features

*   **User Authentication:** Secure login system to protect access to the management features.
*   **Dynamic Line Sheet Generation:** Creates HTML line sheets from Excel data.
*   **Cloudinary Integration:** All images are stored and served from Cloudinary's CDN for fast loading and optimization.
*   **Bulk Image Upload:** Upload an entire directory of product images at once.
*   **Discount Management:** Apply global or per-product discounts.
*   **Responsive Design:** The application is usable on both desktop and mobile devices.
*   **Image Gallery:** An interactive, full-screen image gallery (PhotoSwipe) for viewing product images.
*   **Product Sorting:** Sort products in a line sheet by style number, price, or quantity.
*   **Special Highlighting:** Automatically highlights special sizes and descriptions for better visibility.
*   **Dark/Light Mode:** A theme toggle for user preference.
