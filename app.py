from flask import Flask, render_template, request, redirect, url_for, flash
import os, uuid, logging, tempfile
from werkzeug.utils import secure_filename

# Utils
from utils.text_extraction  import extract_text_from_pdf
from utils.image_extraction import extract_text_from_image, is_image_file, SUPPORTED_EXTENSIONS
from utils.docx_extraction  import extract_text_from_docx
from utils.masking          import mask_text, get_mask_summary
from utils.ner              import group_entities_by_type
from utils.translation      import translate_all, TARGET_LANGUAGES

# ------------------- CONFIG -------------------

app = Flask(__name__)

# Secret key (use environment variable in production)
app.secret_key = os.environ.get('SECRET_KEY', 'change-me-in-production')

# Logging
logging.basicConfig(level=logging.INFO)

# Max file size (20 MB)
MAX_FILE_SIZE_MB = 20
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024

# Accepted file types
ACCEPTED_EXTENSIONS = {'.pdf', '.docx'} | SUPPORTED_EXTENSIONS


# ------------------- HELPERS -------------------

def _accepted(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in ACCEPTED_EXTENSIONS


def _file_type(filename: str) -> str:
    ext = os.path.splitext(filename.lower())[1]
    if ext == '.pdf':   return 'pdf'
    if ext == '.docx':  return 'docx'
    if ext in SUPPORTED_EXTENSIONS: return 'image'
    return 'unknown'


def _save_temp(file) -> str:
    """
    Save uploaded file to temporary directory (Vercel-safe)
    """
    temp_dir = tempfile.gettempdir()
    filename = secure_filename(file.filename)
    path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{filename}")
    file.save(path)
    return path


def _delete(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


def _extract_raw(path: str, file_type: str, use_ocr: bool, ocr_lang: str) -> str:
    """Route file to the correct extractor"""
    if file_type == 'pdf':
        return extract_text_from_pdf(path, use_ocr=use_ocr, ocr_lang=ocr_lang)

    if file_type == 'image':
        return extract_text_from_image(path, ocr_lang=ocr_lang)

    if file_type == 'docx':
        return extract_text_from_docx(path, ocr_lang=ocr_lang, ocr_images=use_ocr)

    raise ValueError(f"Unsupported file type: {file_type}")


# ------------------- ROUTES -------------------

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    results = []

    if request.method == 'POST':
        files        = request.files.getlist('files')
        use_ocr      = request.form.get('use_ocr')     == 'on'
        extract_ner  = request.form.get('extract_ner') == 'on'
        apply_mask   = request.form.get('apply_mask')  == 'on'
        do_translate = request.form.get('do_translate')== 'on'
        ocr_lang     = request.form.get('ocr_lang', 'eng').strip() or 'eng'

        if not files or files[0].filename == '':
            flash('No files selected.', 'error')
            return redirect(request.url)

        for file in files:
            fname = file.filename

            # File type check
            if not _accepted(fname):
                flash(f"'{fname}' skipped — unsupported format.", 'warning')
                continue

            # File size check
            if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
                flash(f"'{fname}' is too large.", "error")
                continue

            ftype = _file_type(fname)
            path  = _save_temp(file)

            entry = dict(
                filename=fname,
                file_type=ftype,
                raw_text='',
                masked_text='',
                masking_applied=apply_mask,
                mask_summary='',
                mask_report={},
                entities={},
                translations={},
                translation_applied=do_translate,
                error=None,
            )

            try:
                logging.info(f"Processing file: {fname}")

                raw = _extract_raw(path, ftype, use_ocr, ocr_lang)
                entry['raw_text'] = raw or ''

                # ---------------- Masking ----------------
                if apply_mask and raw:
                    masked, report = mask_text(raw)
                    entry['masked_text']  = masked
                    entry['mask_summary'] = get_mask_summary(report)
                    entry['mask_report']  = report.by_type

                # ---------------- NER ----------------
                if extract_ner and raw:
                    try:
                        entry['entities'] = group_entities_by_type(raw)
                    except RuntimeError as e:
                        flash(f"NER skipped for '{fname}': {e}", 'warning')

                # ---------------- Translation ----------------
                source_for_translation = (
                    entry['masked_text']
                    if (apply_mask and entry['masked_text'])
                    else raw
                )

                if do_translate and source_for_translation:
                    entry['translations'] = translate_all(source_for_translation)

            except Exception as e:
                entry['error'] = str(e)
                logging.error(f"Error processing {fname}: {e}")
                flash(f"Failed to process '{fname}': {e}", 'error')

            finally:
                _delete(path)

            results.append(entry)

        if not results:
            flash('No valid files were processed.', 'error')

    accepted_str = ', '.join(sorted(ACCEPTED_EXTENSIONS))

    return render_template(
        'upload.html',
        results=results,
        languages=list(TARGET_LANGUAGES.keys()),
        accepted_extensions=accepted_str
    )


# ------------------- ERROR HANDLERS -------------------

@app.errorhandler(413)
def too_large(e):
    flash(f'File too large. Max {MAX_FILE_SIZE_MB} MB.', 'error')
    return redirect(url_for('upload_file'))


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500


# ------------------- ENTRY POINT -------------------

# IMPORTANT: No app.run() for Vercel
# Vercel automatically detects `app`
if __name__ == "__main__":
    app.run(debug=True)