from flask import Flask, render_template, request, redirect, url_for, flash
import os
from utils.text_extraction import extract_text_from_pdf

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Required for flash messages

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    extracted_texts = {}
    if request.method == 'POST':
        try:
            files = request.files.getlist('pdfs')
            if not files or files[0].filename == '':
                flash('No files selected. Please select a PDF file to upload.', 'error')
                return redirect(request.url)
            
            for file in files:
                if not file.filename.lower().endswith('.pdf'):
                    flash(f"File '{file.filename}' is not a PDF. Please upload PDF files only.", 'error')
                    continue

                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                
                try:
                    # Extract text from the uploaded PDF
                    extracted_text = extract_text_from_pdf(file_path, use_ocr=True, ocr_lang='eng+fra+deu')
                    extracted_texts[file.filename] = extracted_text
                except Exception as e:
                    flash(f"Failed to extract text from '{file.filename}': {str(e)}", 'error')
                    continue
            
            if not extracted_texts:
                flash('No text could be extracted from the uploaded files.', 'error')

        except Exception as e:
            flash(f"An unexpected error occurred: {str(e)}", 'error')
            return redirect(request.url)
    
    return render_template('upload.html', extracted_texts=extracted_texts)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
