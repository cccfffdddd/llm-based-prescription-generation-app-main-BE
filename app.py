from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import requests
from google.cloud import logging as google_logging

# Instantiates a client
logging_client = google_logging.Client()

# Creates a Cloud Logging handler that logs at INFO level and higher
cloud_logger = logging_client.logger('image-upload-logger')

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        cloud_logger.log_text('No file part in the request', severity='ERROR')
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        cloud_logger.log_text('No file selected for upload', severity='ERROR')
        return jsonify({'error': 'No selected file'})
    
    filename = secure_filename(file.filename)  # Ensures the filename is safe to use
    img = Image.open(file.stream)
    extracted_text = pytesseract.image_to_string(img)
    
    cloud_logger.log_text(f'Extracted text: {extracted_text}', severity='INFO')

    response = requests.post('http://example.com/api', json={'text': extracted_text})
    if response.status_code == 200:
        imageUrl = response.json().get('imageUrl')
        cloud_logger.log_text(f'Image URL received: {imageUrl}', severity='INFO')
        return jsonify({'imageUrl': imageUrl})
    else:
        error_message = 'Failed to process the image'
        cloud_logger.log_text(error_message, severity='ERROR')
        return jsonify({'error': error_message})

if __name__ == '__main__':
    app.run(debug=True)
