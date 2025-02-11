from flask import Flask, render_template, request, jsonify
import fitz  # PyMuPDF
import re
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])  # Extract text
    doc.close()
    return text

def clean_text(text):
    """Cleans extracted text by removing extra spaces."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text.lower()  # Convert to lowercase for case-insensitive search

def extract_main_data(sentence, query):
    """Extracts only the main information from a sentence."""
    sentence = re.sub(r'\b\d+(\.\d+)?\b', '', sentence)  # Remove numbers
    sentence = re.sub(r'cgpa|projects|nov|dec', '', sentence, flags=re.IGNORECASE)  # Remove unwanted words
    sentence = sentence.strip()

    if query in sentence:
        return f"✅ Data Found: {query}\n📌 Extracted Text: {sentence.strip()}"

    return "❌ Not Found"

def find_relevant_text(query, document):
    """Finds relevant text and extracts the most important information."""
    query = query.lower().strip()
    sentences = re.split(r'(?<=[.!?])\s+', document)  # Split text into sentences

    for sentence in sentences:
        if query in sentence:
            return extract_main_data(sentence, query)

    return "❌ Not Found"

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    """Handles PDF upload and processes text."""
    if "pdf_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["pdf_file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(extracted_text)

    return jsonify({"message": "PDF uploaded successfully!", "text": cleaned_text})

@app.route("/search", methods=["POST"])
def search_text():
    """Searches for user query in extracted text."""
    data = request.json
    query = data.get("query", "").strip()
    document = data.get("text", "").strip()

    if not query or not document:
        return jsonify({"error": "Invalid input"}), 400

    result = find_relevant_text(query, document)
    return jsonify({"response": result})

if __name__ == "__main__":
    app.run(debug=True)
