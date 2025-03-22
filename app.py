import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pytesseract
import pdfplumber  # Using pdfplumber for PDF text extraction
import pandas as pd
import re

app = Flask(__name__)

# Set up folder to save uploaded PDFs
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the 'uploads' folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to check if the uploaded file is a PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from a PDF using pdfplumber
def extract_text_from_pdf(pdf_path):
    # Open the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        # Extract text from the first page
        page = pdf.pages[0]
        extracted_text = page.extract_text()
    
    return extracted_text

# Function to check fraud based on receipt ID
def check_fraud(extracted_text, csv_path):
    # Use regular expression to find receipt ID
    match = re.search(r'REC-\d{3}', extracted_text)  # Adjusted for receipt ID format RC-xxxxx
    
    if match:
        receipt_id = match.group(0)  # Extract the matched receipt ID (e.g., 'REC-20005')
        print(f"Extracted Receipt ID: {receipt_id}")
    else:
        return "Not a fraud"
    
    # Load the receipts.csv file
    receipts_df = pd.read_csv(csv_path)

    # Check if the extracted receipt ID matches any in the CSV file
    if receipt_id in receipts_df['receipt_id'].values:
        return "Fraud"
    else:
        return "Not fraud"

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the uploaded PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Path to the receipts.csv file (adjust the path as needed)
        csv_path = '/Users/kabirmathur/Desktop/ocr_receipt_fraud/dataset/receipt_features.csv'
        
        # Extract text from the uploaded PDF
        extracted_text = extract_text_from_pdf(file_path)
        
        # Check fraud based on extracted text
        result = check_fraud(extracted_text, csv_path)
        
        return f"Fraud Check Result: {result}"
    
    return "Invalid file type. Please upload a PDF."

if __name__ == '__main__':
    app.run(debug=True)
