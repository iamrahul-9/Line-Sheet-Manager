import pandas as pd
import os

# Create a dataframe with dummy data
data = {
    'STYLE#': ['AY-101', 'AY-102', 'CM-201'],
    'COLOR': ['Black', 'White', 'Blue'],
    'PRICE': [50.00, 75.50, 99.99],
    'DISCOUNT': [10, '', 20],
    'DESCRIPTION': ['80% Cotton, 20% Polyester', 'Reversible Jacket', '100% Silk'],
    'SIZES': ['S-XXL', '1,2,2,1,0', 'S,M,L']
}
df = pd.DataFrame(data)

# Define the path for the template file
file_path = os.path.join(os.path.dirname(__file__), 'static', 'linesheet_template.xlsx')

# Ensure the static directory exists
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Save the dataframe to an Excel file
df.to_excel(file_path, index=False)

print(f"Template file created at {file_path}")
