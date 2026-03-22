<div align="center">

# 📄 PDF · Image · DOCX — Extract, Mask & Translate

**Extract text from any document. Redact sensitive data. Translate to 3 languages.**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

[Features](#-features) · [Quickstart](#-quickstart) · [How It Works](#-how-it-works) · [Project Structure](#-project-structure) · [Author](#-author)

</div>

---

## ✨ Features

| Feature | Detail |
|---|---|
| 📁 **File types** | PDF, JPG, PNG, WEBP, BMP, TIFF, DOCX |
| 🔍 **PDF extraction** | Native text + EasyOCR fallback for scanned pages |
| 🖼 **Image OCR** | EasyOCR with contrast & sharpness preprocessing |
| 📝 **DOCX** | Paragraphs + tables + embedded image OCR |
| 🔒 **Data masking** | `[EMAIL] ****@domain.com` · `[PHONE] +91 ****` · `[NAME] ****` · `[CARD] **** 1234` · `[URL] domain/****` |
| 🌐 **Translation** | English · Hindi · French (Google Translate) |
| 🧠 **NER** | Named entity recognition via spaCy (optional) |
| ⬇️ **Export** | Copy or download extracted text per file |

---

## 🚀 Quickstart

**No Tesseract. No Docker. Just pip install.**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Install spaCy model for Named Entity Recognition
python -m spacy download en_core_web_sm

# 3. Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

> ⚡ **First run note:** EasyOCR downloads its model files (~100 MB) automatically on first use. This is a one-time download — subsequent runs use cached models instantly.

---

## 🖼 Demo

### Upload & Extract
> Upload any PDF, image, or DOCX file. The app extracts all text — even from scanned documents using EasyOCR.

```
Input:  resume.pdf  /  invoice.jpg  /  report.docx
Output: Full extracted text, ready to copy or download
```

### Data Masking
> Sensitive data is automatically detected and partially masked with a type label:

```
Before:  Ravi Sah  ·  +91 9234614488  ·  rsahravi57@gmail.com  ·  github.com/sahravi63
After:   [NAME] ****  ·  [PHONE] +91 ****  ·  [EMAIL] ****@gmail.com  ·  [URL] github.com/****
```

### Translation Tabs
> Switch between English, Hindi, and French output tabs on every result card.

```
🇬🇧 English  →  Original extracted text (masked)
🇮🇳 Hindi    →  हिंदी में अनुवादित पाठ
🇫🇷 French   →  Texte traduit en français
```

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────┐
│              Upload (PDF / Image / DOCX)         │
└─────────────────────┬───────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │    Text Extraction     │
          │  pypdf · EasyOCR      │
          │  python-docx          │
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │     Data Masking      │
          │  Regex + spaCy NER    │
          │  EMAIL PHONE NAME     │
          │  CARD URL             │
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │     Translation       │
          │  Google Translate     │
          │  EN · HI · FR         │
          └───────────┬───────────┘
                      │
          ┌───────────▼───────────┐
          │   Results + Export    │
          │  View · Copy · Download│
          └───────────────────────┘
```

---

## 🔤 OCR Engine: EasyOCR

This project uses **EasyOCR** — no system-level install required:

| | Tesseract | EasyOCR |
|---|---|---|
| Install | System package required | `pip install easyocr` only |
| Accuracy | Good | Better (deep learning based) |
| Languages | Separate pack installs | Auto-downloaded |
| Windows support | Complex setup | ✅ Works out of the box |

### Language codes

| Language | Code |
|---|---|
| English | `en` |
| Hindi | `hi` |
| French | `fr` |
| English + Hindi | `en+hi` |
| All three | `en+hi+fr` |

---

## 📁 Project Structure

```
pdf-dataExtraction-main/
├── app.py                      ← Flask app, routes, orchestration
├── requirements.txt
├── static/
│   └── styles.css              ← Dark themed UI
├── templates/
│   ├── upload.html             ← Main upload + results page
│   └── error.html              ← 404 / 500 error page
└── utils/
    ├── ocr.py                  ← EasyOCR engine (replaces Tesseract)
    ├── text_extraction.py      ← PDF → text (pypdf + OCR fallback)
    ├── image_extraction.py     ← Image → text (EasyOCR)
    ├── docx_extraction.py      ← DOCX → text (python-docx + OCR)
    ├── image_processing.py     ← Preprocessing helpers
    ├── masking.py              ← Labelled partial masking
    ├── ner.py                  ← spaCy Named Entity Recognition
    └── translation.py          ← Google Translate (EN / HI / FR)
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| PDF parsing | pypdf, pdf2image |
| OCR | EasyOCR |
| DOCX parsing | python-docx |
| NER | spaCy (`en_core_web_sm`) |
| Translation | deep-translator (Google Translate) |
| Language detection | langdetect |
| Frontend | HTML, CSS, Vanilla JS |

---

## 👤 Author

**Ravi Sah**
B.Tech Computer Science & Engineering — SRM Institute of Science and Technology

[![GitHub](https://img.shields.io/badge/GitHub-sahravi63-black?style=flat-square&logo=github)](https://github.com/sahravi63)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-ravi--sah-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/sahravi63)

---

## 🚀 Live Project  

👉 https://pdf-data-extraction-1av5.vercel.app/  

---


## 📄 License


This project is open source and available under the [MIT License](LICENSE).