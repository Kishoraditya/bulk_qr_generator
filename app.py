import os
import uuid
import zipfile
import tempfile
import pandas as pd
import segno
from flask import Flask, render_template, request, send_file, jsonify, url_for, redirect, session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import math
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from dotenv import load_dotenv
from PIL import Image
import io
import base64
import time
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-for-session')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv', 'jpg', 'jpeg', 'png'}
app.config['SESSION_LIFETIME'] = timedelta(hours=1)

# Rate limiting to prevent abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import utility functions
from utils.qr_generator import generate_qr_codes, create_qr_pdf, create_styled_qr
from utils.file_utils import read_file_data, allowed_file, cleanup_old_files

# Setup scheduler for cleanup tasks
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_files, args=[app.config['UPLOAD_FOLDER'], 3600], trigger="interval", seconds=3600)
scheduler.start()

@app.route('/')
def index():
    # Generate a unique session ID if not already present
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        logger.info(f"New user session created: {session['user_id']}")
    
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handle QR code generation requests"""
    try:
        generation_type = request.form.get('generation_type')
        
        if generation_type == 'excel':
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'})
                
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'})
                
            # Handle Excel/CSV generation
            result = handle_excel_generation(request.form, file)
            return jsonify(result)
            
        elif generation_type == 'url':
            # Handle URL QR code generation
            result = handle_url_generation(request.form)
            return jsonify(result)
            
        elif generation_type == 'vcard':
            # Handle vCard QR code generation
            result = handle_vcard_generation(request.form)
            return jsonify(result)
            
        elif generation_type == 'image':
            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({'error': 'No image uploaded'})
                
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No image selected'})
                
            # Handle image QR code generation
            result = handle_image_generation(request.form, file)
            return jsonify(result)
            
        else:
            return jsonify({'error': 'Invalid generation type'})
            
    except Exception as e:
        logger.error(f"Error in generate route: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'})


def handle_excel_generation(request_form, file):
    """
    Handle generation of QR codes from Excel/CSV files
    
    Args:
        request_form: Form data containing generation parameters
        file: Uploaded file object
    
    Returns:
        Dictionary with generation results or error
    """
    try:
        # Get form parameters
        column_index = int(request_form.get('column', 0))
        max_rows = request_form.get('max_rows', '')
        max_rows = int(max_rows) if max_rows and max_rows.strip() else None
        qr_size = int(request_form.get('qr_size', 50))
        page_margin = int(request_form.get('page_margin', 5))
        qr_margin = int(request_form.get('qr_margin', 0))
        include_text = request_form.get('include_text') == 'true'
        include_page_numbers = request_form.get('include_page_numbers') == 'true'
        error_level = request_form.get('error_level', 'l')
        download_type = request_form.get('download_type', 'pdf')
        
        # Validate inputs
        if qr_size < 50:
            qr_size = 50  # Minimum size for reliable scanning
        
        # Create unique session directory
        session_id = session.get('user_id', str(uuid.uuid4()))
        session['user_id'] = session_id
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(session_dir, secure_filename(file.filename))
        file.save(file_path)
        
        # Read data from file
        data = read_file_data(file_path, column_index, max_rows)
        
        if not data:
            return {'error': 'No valid data found in the specified column'}
        
        # Generate QR codes
        qr_files = generate_qr_codes(data, session_dir, qr_size, error_level)
        
        # Create output files based on download type
        pdf_stats = None
        
        if download_type in ['pdf', 'both']:
            pdf_path = os.path.join(session_dir, 'qr_codes.pdf')
            pdf_stats = create_qr_pdf(
                qr_files, pdf_path, qr_size, page_margin, qr_margin,
                include_text, include_page_numbers
            )
        
        if download_type in ['zip', 'both']:
            # Create zip file with individual QR codes
            zip_path = os.path.join(session_dir, 'qr_codes.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for i, (qr_file, code) in enumerate(qr_files):
                    # Use the code value as filename (sanitized)
                    safe_name = "".join([c if c.isalnum() else "_" for c in code])
                    safe_name = safe_name[:50]  # Limit filename length
                    zipf.write(qr_file, f"{safe_name}.png")
        
        # Prepare response
        response = {
            'success': True,
            'message': f'Successfully generated {len(qr_files)} QR codes',
            'stats': pdf_stats if pdf_stats else {'total_qr_codes': len(qr_files)}
        }
        
        # Add download URLs based on download type
        download_links = []
        
        if download_type in ['pdf', 'both']:
            pdf_url = url_for('download_file', session_id=session_id, file_type='pdf')
            response['pdf_url'] = pdf_url
            download_links.append({
                'url': pdf_url,
                'label': 'Download PDF'
            })
        
        if download_type in ['zip', 'both']:
            zip_url = url_for('download_file', session_id=session_id, file_type='zip')
            response['zip_url'] = zip_url
            download_links.append({
                'url': zip_url,
                'label': 'Download ZIP'
            })
        
        # Add download links for the frontend
        response['download_links'] = download_links
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating QR codes: {str(e)}")
        return {'error': f'Error generating QR codes: {str(e)}'}

def handle_url_generation(form_data):
    url = form_data.get('url', '').strip()
    if not url:
        return {'error': 'URL is required'}
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    qr_size = int(form_data.get('qr_size', 300))
    error_level = form_data.get('error_level', 'm')
    qr_style = form_data.get('qr_style', 'standard')
    
    # Create unique session directory
    session_id = session.get('user_id', str(uuid.uuid4()))
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Generate QR code
    qr_file = os.path.join(session_dir, 'url_qr.png')
    
    # Create styled QR code
    create_styled_qr(url, qr_file, qr_size, error_level, qr_style)
    
    # Create a preview image for display
    with open(qr_file, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        'success': True,
        'message': 'URL QR code generated successfully',
        'download_url': url_for('download_file', session_id=session_id, file_type='url_qr'),
        'preview': f'data:image/png;base64,{img_data}'
    }

def handle_image_generation(file, form_data):
    qr_data = form_data.get('qr_data', '').strip()
    if not qr_data:
        return {'error': 'QR code data is required'}
    
    qr_size = int(form_data.get('qr_size', 300))
    error_level = form_data.get('error_level', 'h')  # Use high error correction for image QR
    
    # Create unique session directory
    session_id = session.get('user_id', str(uuid.uuid4()))
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save uploaded image
    img_path = os.path.join(session_dir, secure_filename(file.filename))
    file.save(img_path)
    
    # Generate QR code with embedded image
    qr_file = os.path.join(session_dir, 'image_qr.png')
    
    # Create QR code with image overlay
    qr = segno.make(qr_data, error=error_level)
    
    # Open and resize the image
    img = Image.open(img_path)
    img = img.resize((qr_size // 3, qr_size // 3))
    
    # Create a new image with the QR code
    scale = max(1, int(qr_size / 25))
    qr_img = qr.to_pil(scale=scale, border=4)
    
    # Calculate position to place the image in the center
    position = ((qr_img.width - img.width) // 2, (qr_img.height - img.height) // 2)
    
    # Paste the image onto the QR code
    qr_img.paste(img, position)
    qr_img.save(qr_file)
    
    # Create a preview image for display
    with open(qr_file, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        'success': True,
        'message': 'Image QR code generated successfully',
        'download_url': url_for('download_file', session_id=session_id, file_type='image_qr'),
        'preview': f'data:image/png;base64,{img_data}'
    }

def handle_vcard_generation(form_data):
    # Get vCard data
    name = form_data.get('name', '').strip()
    email = form_data.get('email', '').strip()
    phone = form_data.get('phone', '').strip()
    company = form_data.get('company', '').strip()
    title = form_data.get('title', '').strip()
    website = form_data.get('website', '').strip()
    address = form_data.get('address', '').strip()
    
    if not (name or email or phone):
        return {'error': 'At least name, email, or phone is required'}
    
    # Create vCard format
    vcard = [
        "BEGIN:VCARD",
        "VERSION:3.0"
    ]
    
    if name:
        vcard.append(f"FN:{name}")
        # Split name into parts if possible
        name_parts = name.split()
        if len(name_parts) > 1:
            vcard.append(f"N:{name_parts[-1]};{' '.join(name_parts[:-1])}")
        else:
            vcard.append(f"N:{name}")
    
    if email:
        vcard.append(f"EMAIL:{email}")
    
    if phone:
        vcard.append(f"TEL:{phone}")
    
    if company:
        vcard.append(f"ORG:{company}")
    
    if title:
        vcard.append(f"TITLE:{title}")
    
    if website:
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        vcard.append(f"URL:{website}")
    
    if address:
        vcard.append(f"ADR:;;{address}")
    
    vcard.append("END:VCARD")
    vcard_data = "\n".join(vcard)
    
    # Generate QR code
    qr_size = int(form_data.get('qr_size', 300))
    error_level = form_data.get('error_level', 'm')
    
    # Create unique session directory
    session_id = session.get('user_id', str(uuid.uuid4()))
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Generate QR code
    qr_file = os.path.join(session_dir, 'vcard_qr.png')
    
    # Create QR code
    qr = segno.make(vcard_data, error=error_level)
    scale = max(1, int(qr_size / 25))
    qr.save(qr_file, scale=scale, border=4)
    
    # Create a preview image for display
    with open(qr_file, 'rb') as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    
    return {
        'success': True,
        'message': 'vCard QR code generated successfully',
        'download_url': url_for('download_file', session_id=session_id, file_type='vcard_qr'),
        'preview': f'data:image/png;base64,{img_data}'
    }

@app.route('/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    
    if not os.path.exists(session_dir):
        logger.warning(f"Download attempt for non-existent session: {session_id}")
        return "Files not found or expired", 404
    
    # Log download
    logger.info(f"File download: {file_type} by session {session_id}")
    
    if file_type == 'pdf':
        file_path = os.path.join(session_dir, 'qr_codes.pdf')
        return send_file(file_path, as_attachment=True, download_name='qr_codes.pdf')
    elif file_type == 'zip':
        file_path = os.path.join(session_dir, 'qr_codes.zip')
        return send_file(file_path, as_attachment=True, download_name='qr_codes.zip')
    elif file_type == 'url_qr':
        file_path = os.path.join(session_dir, 'url_qr.png')
        return send_file(file_path, as_attachment=True, download_name='url_qr.png')
    elif file_type == 'image_qr':
        file_path = os.path.join(session_dir, 'image_qr.png')
        return send_file(file_path, as_attachment=True, download_name='image_qr.png')
    elif file_type == 'vcard_qr':
        file_path = os.path.join(session_dir, 'vcard_qr.png')
        return send_file(file_path, as_attachment=True, download_name='vcard_qr.png')
    else:
        return "Invalid file type", 400

@app.route('/api/stats')
def api_stats():
    """API endpoint for usage statistics (for admin dashboard)"""
    if request.headers.get('X-Admin-Key') != os.environ.get('ADMIN_API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # This would be implemented with a proper database in production
    return jsonify({
        'total_generations': 0,
        'active_users': 0,
        'popular_formats': {}
    })

@app.route('/sitemap.xml')
def sitemap():
    """Generate a sitemap for SEO"""
    pages = [
        {'loc': url_for('index', _external=True), 'priority': '1.0'},
        {'loc': url_for('index', _external=True) + '#excel', 'priority': '0.8'},
        {'loc': url_for('index', _external=True) + '#url', 'priority': '0.8'},
        {'loc': url_for('index', _external=True) + '#vcard', 'priority': '0.8'},
        {'loc': url_for('index', _external=True) + '#image', 'priority': '0.8'},
    ]
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = app.response_class(sitemap_xml, mimetype='application/xml')
    return response

@app.route('/robots.txt')
def robots():
    return """
User-agent: *
Allow: /
Sitemap: {}
""".format(url_for('sitemap', _external=True))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500

# Cleanup when the app is shutting down
@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        scheduler.shutdown()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
