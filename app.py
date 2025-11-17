from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Admin credentials (in production, use a database)
ADMIN_USERS = {
    'Admin123@mochwanaesi.co.za': generate_password_hash('Admin123A')
}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to load JSON data
def load_json_data(filename):
    filepath = os.path.join('data', filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Helper function to save JSON data
def save_json_data(filename, data):
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in to access the admin panel.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ===================================
# Admin Routes
# ===================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ADMIN_USERS and check_password_hash(ADMIN_USERS[username], password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Successfully logged out.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@login_required
def admin_dashboard():
    # Get counts for dashboard
    announcements = load_json_data('announcements.json')
    staff = load_json_data('staff.json')
    
    stats = {
        'announcements': len(announcements),
        'staff': len(staff),
        'leadership': len([s for s in staff if s['role'] == 'leadership']),
        'program_staff': len([s for s in staff if s['role'] == 'program_staff'])
    }
    
    return render_template('admin/dashboard.html', stats=stats)

# ===================================
# Admin - Announcements Management
# ===================================

@app.route('/admin/announcements')
@login_required
def admin_announcements():
    announcements = load_json_data('announcements.json')
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/announcements/add', methods=['GET', 'POST'])
@login_required
def admin_add_announcement():
    if request.method == 'POST':
        announcements = load_json_data('announcements.json')
        
        # Generate unique numeric ID
        existing_ids = [a['id'] for a in announcements if isinstance(a['id'], int)]
        new_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Handle file upload
        image_url = '/static/images/announcements/default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"announcement_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f'/static/images/uploads/{filename}'
        
        new_announcement = {
            'id': new_id,
            'title': request.form.get('title'),
            'excerpt': request.form.get('excerpt'),
            'category': request.form.get('category'),
            'date': datetime.now().isoformat(),
            'image_url': image_url,
            'featured': request.form.get('featured') == 'on'
        }
        
        announcements.insert(0, new_announcement)
        save_json_data('announcements.json', announcements)
        
        flash('Announcement added successfully!', 'success')
        return redirect(url_for('admin_announcements'))
    
    return render_template('admin/announcement_form.html', announcement=None)

@app.route('/admin/announcements/edit/<announcement_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_announcement(announcement_id):
    announcements = load_json_data('announcements.json')
    # Convert to int if it's a numeric string
    try:
        announcement_id = int(announcement_id)
    except ValueError:
        pass
    announcement = next((a for a in announcements if a['id'] == announcement_id), None)
    
    if not announcement:
        flash('Announcement not found.', 'error')
        return redirect(url_for('admin_announcements'))
    
    if request.method == 'POST':
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"announcement_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                announcement['image_url'] = f'/static/images/uploads/{filename}'
        
        announcement['title'] = request.form.get('title')
        announcement['excerpt'] = request.form.get('excerpt')
        announcement['category'] = request.form.get('category')
        announcement['featured'] = request.form.get('featured') == 'on'
        
        save_json_data('announcements.json', announcements)
        
        flash('Announcement updated successfully!', 'success')
        return redirect(url_for('admin_announcements'))
    
    return render_template('admin/announcement_form.html', announcement=announcement)

@app.route('/admin/announcements/delete/<announcement_id>', methods=['POST'])
@login_required
def admin_delete_announcement(announcement_id):
    announcements = load_json_data('announcements.json')
    # Convert to int if it's a numeric string
    try:
        announcement_id = int(announcement_id)
    except ValueError:
        pass
    announcements = [a for a in announcements if a['id'] != announcement_id]
    save_json_data('announcements.json', announcements)
    
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('admin_announcements'))

# ===================================
# Admin - Staff Management
# ===================================

@app.route('/admin/staff')
@login_required
def admin_staff():
    staff = load_json_data('staff.json')
    return render_template('admin/staff.html', staff=staff)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@login_required
def admin_add_staff():
    if request.method == 'POST':
        staff = load_json_data('staff.json')
        
        # Generate unique numeric ID
        existing_ids = [s['id'] for s in staff if isinstance(s['id'], int)]
        new_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Handle file upload
        image_url = '/static/images/staff/default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"staff_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f'/static/images/uploads/{filename}'
        
        new_staff = {
            'id': new_id,
            'name': request.form.get('name'),
            'title': request.form.get('title'),
            'bio': request.form.get('bio'),
            'role': request.form.get('role'),
            'email': request.form.get('email'),
            'linkedin_url': request.form.get('linkedin_url'),
            'image_url': image_url
        }
        
        # Add department for program staff
        if new_staff['role'] == 'program_staff':
            new_staff['department'] = request.form.get('department')
        
        staff.append(new_staff)
        save_json_data('staff.json', staff)
        
        flash('Staff member added successfully!', 'success')
        return redirect(url_for('admin_staff'))
    
    return render_template('admin/staff_form.html', staff_member=None)

@app.route('/admin/staff/edit/<staff_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_staff(staff_id):
    staff = load_json_data('staff.json')
    # Convert to int if it's a numeric string
    try:
        staff_id = int(staff_id)
    except ValueError:
        pass
    staff_member = next((s for s in staff if s['id'] == staff_id), None)
    
    if not staff_member:
        flash('Staff member not found.', 'error')
        return redirect(url_for('admin_staff'))
    
    if request.method == 'POST':
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"staff_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                staff_member['image_url'] = f'/static/images/uploads/{filename}'
        
        staff_member['name'] = request.form.get('name')
        staff_member['title'] = request.form.get('title')
        staff_member['bio'] = request.form.get('bio')
        staff_member['role'] = request.form.get('role')
        staff_member['email'] = request.form.get('email')
        staff_member['linkedin_url'] = request.form.get('linkedin_url')
        
        if staff_member['role'] == 'program_staff':
            staff_member['department'] = request.form.get('department')
        
        save_json_data('staff.json', staff)
        
        flash('Staff member updated successfully!', 'success')
        return redirect(url_for('admin_staff'))
    
    return render_template('admin/staff_form.html', staff_member=staff_member)

@app.route('/admin/staff/delete/<staff_id>', methods=['POST'])
@login_required
def admin_delete_staff(staff_id):
    staff = load_json_data('staff.json')
    # Convert to int if it's a numeric string
    try:
        staff_id = int(staff_id)
    except ValueError:
        pass
    staff = [s for s in staff if s['id'] != staff_id]
    save_json_data('staff.json', staff)
    
    flash('Staff member deleted successfully!', 'success')
    return redirect(url_for('admin_staff'))

# ===================================
# Admin - Images Management
# ===================================

@app.route('/admin/images')
@login_required
def admin_images():
    # Get all uploaded images
    upload_folder = app.config['UPLOAD_FOLDER']
    images = []
    
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            if allowed_file(filename):
                filepath = os.path.join(upload_folder, filename)
                file_stats = os.stat(filepath)
                images.append({
                    'filename': filename,
                    'url': f'/static/images/uploads/{filename}',
                    'size': file_stats.st_size,
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                })
    
    # Sort by modified date (newest first)
    images.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('admin/images.html', images=images)

@app.route('/admin/images/upload', methods=['POST'])
@login_required
def admin_upload_image():
    if 'image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_images'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_images'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upload_{timestamp}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        flash('Image uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif, webp', 'error')
    
    return redirect(url_for('admin_images'))

@app.route('/admin/images/delete/<filename>', methods=['POST'])
@login_required
def admin_delete_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Image deleted successfully!', 'success')
    else:
        flash('Image not found.', 'error')
    
    return redirect(url_for('admin_images'))

# ===================================
# Admin - Page-Specific Images
# ===================================

# Helper function to get images for a specific page
def get_page_images(page_folder):
    page_path = os.path.join('static', 'images', page_folder)
    images = []
    
    if os.path.exists(page_path):
        for filename in os.listdir(page_path):
            if allowed_file(filename):
                filepath = os.path.join(page_path, filename)
                file_stats = os.stat(filepath)
                images.append({
                    'filename': filename,
                    'url': f'/static/images/{page_folder}/{filename}',
                    'size': file_stats.st_size,
                    'modified': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                })
    
    images.sort(key=lambda x: x['modified'], reverse=True)
    return images

@app.route('/admin/images/home')
@login_required
def admin_home_images():
    images = get_page_images('hero')
    return render_template('admin/page_images.html', 
                         images=images, 
                         page_name='Home Page',
                         page_folder='hero',
                         upload_endpoint='admin_upload_home_image',
                         edit_endpoint='admin_edit_home_image',
                         delete_endpoint='admin_delete_home_image')

@app.route('/admin/images/home/upload', methods=['POST'])
@login_required
def admin_upload_home_image():
    if 'image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_home_images'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_home_images'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"home_{timestamp}_{filename}"
        
        # Ensure hero folder exists
        hero_path = os.path.join('static', 'images', 'hero')
        os.makedirs(hero_path, exist_ok=True)
        
        file.save(os.path.join(hero_path, filename))
        flash('Image uploaded successfully!', 'success')
    else:
        flash('Invalid file type.', 'error')
    
    return redirect(url_for('admin_home_images'))

@app.route('/admin/images/home/edit', methods=['POST'])
@login_required
def admin_edit_home_image():
    old_filename = request.form.get('old_filename')
    
    if 'new_image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_home_images'))
    
    file = request.files['new_image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_home_images'))
    
    if file and allowed_file(file.filename):
        hero_path = os.path.join('static', 'images', 'hero')
        old_filepath = os.path.join(hero_path, secure_filename(old_filename))
        
        # Delete old file if it exists
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
        
        # Save new file with same name or generate new name
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"home_{timestamp}_{filename}"
        
        os.makedirs(hero_path, exist_ok=True)
        file.save(os.path.join(hero_path, filename))
        
        flash('Image replaced successfully!', 'success')
    else:
        flash('Invalid file type.', 'error')
    
    return redirect(url_for('admin_home_images'))

@app.route('/admin/images/home/delete/<filename>', methods=['POST'])
@login_required
def admin_delete_home_image(filename):
    filepath = os.path.join('static', 'images', 'hero', secure_filename(filename))
    
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Image deleted successfully!', 'success')
    else:
        flash('Image not found.', 'error')
    
    return redirect(url_for('admin_home_images'))

@app.route('/admin/images/about')
@login_required
def admin_about_images():
    images = get_page_images('about')
    return render_template('admin/page_images.html', 
                         images=images, 
                         page_name='About Us Page',
                         page_folder='about',
                         upload_endpoint='admin_upload_about_image',
                         edit_endpoint='admin_edit_about_image',
                         delete_endpoint='admin_delete_about_image')

@app.route('/admin/images/about/upload', methods=['POST'])
@login_required
def admin_upload_about_image():
    if 'image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_about_images'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_about_images'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"about_{timestamp}_{filename}"
        
        # Ensure about folder exists
        about_path = os.path.join('static', 'images', 'about')
        os.makedirs(about_path, exist_ok=True)
        
        file.save(os.path.join(about_path, filename))
        flash('Image uploaded successfully!', 'success')
    else:
        flash('Invalid file type.', 'error')
    
    return redirect(url_for('admin_about_images'))

@app.route('/admin/images/about/edit', methods=['POST'])
@login_required
def admin_edit_about_image():
    old_filename = request.form.get('old_filename')
    
    if 'new_image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_about_images'))
    
    file = request.files['new_image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_about_images'))
    
    if file and allowed_file(file.filename):
        about_path = os.path.join('static', 'images', 'about')
        old_filepath = os.path.join(about_path, secure_filename(old_filename))
        
        # Delete old file if it exists
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
        
        # Save new file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"about_{timestamp}_{filename}"
        
        os.makedirs(about_path, exist_ok=True)
        file.save(os.path.join(about_path, filename))
        
        flash('Image replaced successfully!', 'success')
    else:
        flash('Invalid file type.', 'error')
    
    return redirect(url_for('admin_about_images'))

@app.route('/admin/images/about/delete/<filename>', methods=['POST'])
@login_required
def admin_delete_about_image(filename):
    filepath = os.path.join('static', 'images', 'about', secure_filename(filename))
    
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Image deleted successfully!', 'success')
    else:
        flash('Image not found.', 'error')
    
    return redirect(url_for('admin_about_images'))

@app.route('/admin/images/programs')
@login_required
def admin_programs_images():
    images = get_page_images('programs')
    return render_template('admin/page_images.html', 
                         images=images, 
                         page_name='Our Programs Page',
                         page_folder='programs',
                         upload_endpoint='admin_upload_programs_image',
                         edit_endpoint='admin_edit_programs_image',
                         delete_endpoint='admin_delete_programs_image')

@app.route('/admin/images/programs/upload', methods=['POST'])
@login_required
def admin_upload_programs_image():
    if 'image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_programs_images'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_programs_images'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"program_{timestamp}_{filename}"
        
        # Ensure programs folder exists
        programs_path = os.path.join('static', 'images', 'programs')
        os.makedirs(programs_path, exist_ok=True)
        
        file.save(os.path.join(programs_path, filename))
        flash('Image uploaded successfully!', 'success')
    else:
        flash('Invalid file type.', 'error')
    
    return redirect(url_for('admin_programs_images'))

@app.route('/admin/images/programs/edit', methods=['POST'])
@login_required
def admin_edit_programs_image():
    old_filename = request.form.get('old_filename')
    
    if 'new_image' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_programs_images'))
    
    file = request.files['new_image']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('admin_programs_images'))
    
    if file and allowed_file(file.filename):
        programs_path = os.path.join('static', 'images', 'programs')
        old_filepath = os.path.join(programs_path, secure_filename(old_filename))
        
        # Delete old file if it exists
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
        
        # Save new file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"program_{timestamp}_{filename}"
        
        os.makedirs(programs_path, exist_ok=True)
        file.save(os.path.join(programs_path, filename))
        
        flash('Image replaced successfully!', 'success')
    else:
        flash('Invalid file type.', 'error')
    
    return redirect(url_for('admin_programs_images'))

@app.route('/admin/images/programs/delete/<filename>', methods=['POST'])
@login_required
def admin_delete_programs_image(filename):
    filepath = os.path.join('static', 'images', 'programs', secure_filename(filename))
    
    if os.path.exists(filepath):
        os.remove(filepath)
        flash('Image deleted successfully!', 'success')
    else:
        flash('Image not found.', 'error')
    
    return redirect(url_for('admin_programs_images'))

# ===================================
# Admin - Program Images Management
# ===================================

@app.route('/admin/programs')
@login_required
def admin_programs():
    programs_data = load_json_data('programs.json')
    return render_template('admin/programs.html', programs=programs_data)

@app.route('/admin/programs/edit/<program_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_program_image(program_id):
    programs_data = load_json_data('programs.json')
    program = next((p for p in programs_data if p['id'] == program_id), None)
    
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('admin_programs'))
    
    if request.method == 'POST':
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Get file extension from uploaded file
                original_filename = secure_filename(file.filename)
                file_extension = original_filename.rsplit('.', 1)[1].lower()
                
                # Create clean filename using program name with underscores
                # e.g., "Mentorship Program" -> "Mentorship_Program.png"
                clean_name = program['name'].replace(' ', '_')
                filename = f"{clean_name}.{file_extension}"
                
                # Ensure programs folder exists
                programs_path = os.path.join('static', 'images', 'programs')
                os.makedirs(programs_path, exist_ok=True)
                
                # Delete old image file if it exists and is different
                if program.get('image_url'):
                    old_image_path = program['image_url'].replace('/static/', 'static/')
                    if os.path.exists(old_image_path) and not old_image_path.endswith(filename):
                        try:
                            os.remove(old_image_path)
                        except:
                            pass  # Ignore if file can't be deleted
                
                # Save new file
                file.save(os.path.join(programs_path, filename))
                program['image_url'] = f'/static/images/programs/{filename}'
                
                save_json_data('programs.json', programs_data)
                flash(f'{program["name"]} image updated successfully!', 'success')
                return redirect(url_for('admin_programs'))
        else:
            flash('No file selected.', 'error')
    
    return render_template('admin/program_form.html', program=program)

# ===================================
# Public Routes
# ===================================

@app.route('/')
def index():
    # Get slideshow images from hero folder
    hero_images = get_page_images('hero')
    # Get programs data for home page program cards
    programs_data = load_json_data('programs.json')
    return render_template('index.html', current_page='home', hero_images=hero_images, programs=programs_data)

@app.route('/about')
def about():
    staff_data = load_json_data('staff.json')
    
    # Get leadership team for the about page
    leadership_team = [member for member in staff_data if member['role'] == 'leadership']
    
    return render_template('about.html', current_page='about', leadership_team=leadership_team)

@app.route('/programs')
def programs():
    programs_data = load_json_data('programs.json')
    # Programs now use image_url directly from JSON data
    # No need for keyword matching since admin updates the JSON
    return render_template('programs.html', current_page='programs', programs=programs_data)

@app.route('/staff')
def staff():
    staff_data = load_json_data('staff.json')
    
    # Separate leadership and program staff
    leadership_team = [member for member in staff_data if member['role'] == 'leadership']
    program_staff = [member for member in staff_data if member['role'] == 'program_staff']
    
    return render_template('staff.html', 
                         current_page='staff',
                         leadership_team=leadership_team,
                         program_staff=program_staff)

@app.route('/announcements')
def announcements():
    announcements_data = load_json_data('announcements.json')
    
    # Separate featured and regular announcements
    featured_announcements = [ann for ann in announcements_data if ann.get('featured', False)][:2]
    all_announcements = announcements_data
    
    return render_template('announcements.html', 
                         current_page='announcements',
                         featured_announcements=featured_announcements,
                         all_announcements=all_announcements)

@app.route('/contact')
def contact():
    return render_template('contact.html', current_page='contact')

if __name__ == '__main__':
    app.run()
