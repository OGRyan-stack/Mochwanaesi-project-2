from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
from datetime import datetime
from vercel_blob import put, delete as blob_delete
from database import *

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Admin credentials (in production, use a database)
ADMIN_USERS = {
    'Admin123@mochwanaesi.co.za': generate_password_hash('Admin123A')
}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to upload file to Vercel Blob
def upload_to_blob(file, prefix='upload'):
    """Upload file to Vercel Blob storage"""
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    blob_filename = f"{prefix}_{timestamp}_{filename}"
    
    # Upload to Vercel Blob
    blob_result = put(
        pathname=blob_filename,
        body=file.read(),
        options={
            'access': 'public',
            'addRandomSuffix': False
        }
    )
    
    return blob_result['url']

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
    stats = get_stats()
    return render_template('admin/dashboard.html', stats=stats)

# ===================================
# Admin - Announcements Management
# ===================================

@app.route('/admin/announcements')
@login_required
def admin_announcements():
    announcements = get_all_announcements()
    return render_template('admin/announcements.html', announcements=announcements)

@app.route('/admin/announcements/add', methods=['GET', 'POST'])
@login_required
def admin_add_announcement():
    if request.method == 'POST':
        # Handle file upload
        image_url = '/static/images/announcements/default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                try:
                    image_url = upload_to_blob(file, 'announcement')
                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'error')
        
        # Create announcement in database
        create_announcement(
            title=request.form.get('title'),
            excerpt=request.form.get('excerpt'),
            category=request.form.get('category'),
            image_url=image_url,
            featured=request.form.get('featured') == 'on'
        )
        
        flash('Announcement added successfully!', 'success')
        return redirect(url_for('admin_announcements'))
    
    return render_template('admin/announcement_form.html', announcement=None)

@app.route('/admin/announcements/edit/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_announcement(announcement_id):
    announcement = get_announcement_by_id(announcement_id)
    
    if not announcement:
        flash('Announcement not found.', 'error')
        return redirect(url_for('admin_announcements'))
    
    if request.method == 'POST':
        image_url = announcement['image_url']
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                try:
                    image_url = upload_to_blob(file, 'announcement')
                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'error')
        
        # Update announcement in database
        update_announcement(
            announcement_id=announcement_id,
            title=request.form.get('title'),
            excerpt=request.form.get('excerpt'),
            category=request.form.get('category'),
            image_url=image_url,
            featured=request.form.get('featured') == 'on'
        )
        
        flash('Announcement updated successfully!', 'success')
        return redirect(url_for('admin_announcements'))
    
    return render_template('admin/announcement_form.html', announcement=announcement)

@app.route('/admin/announcements/delete/<int:announcement_id>', methods=['POST'])
@login_required
def admin_delete_announcement(announcement_id):
    delete_announcement(announcement_id)
    flash('Announcement deleted successfully!', 'success')
    return redirect(url_for('admin_announcements'))

# ===================================
# Admin - Staff Management
# ===================================

@app.route('/admin/staff')
@login_required
def admin_staff():
    staff = get_all_staff()
    return render_template('admin/staff.html', staff=staff)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@login_required
def admin_add_staff():
    if request.method == 'POST':
        # Handle file upload
        image_url = '/static/images/staff/default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                try:
                    image_url = upload_to_blob(file, 'staff')
                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'error')
        
        # Get department if program staff
        department = None
        if request.form.get('role') == 'program_staff':
            department = request.form.get('department')
        
        # Create staff member in database
        create_staff(
            name=request.form.get('name'),
            title=request.form.get('title'),
            bio=request.form.get('bio'),
            role=request.form.get('role'),
            email=request.form.get('email'),
            linkedin_url=request.form.get('linkedin_url'),
            image_url=image_url,
            department=department
        )
        
        flash('Staff member added successfully!', 'success')
        return redirect(url_for('admin_staff'))
    
    return render_template('admin/staff_form.html', staff_member=None)

@app.route('/admin/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_staff(staff_id):
    staff_member = get_staff_by_id(staff_id)
    
    if not staff_member:
        flash('Staff member not found.', 'error')
        return redirect(url_for('admin_staff'))
    
    if request.method == 'POST':
        image_url = staff_member['image_url']
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                try:
                    image_url = upload_to_blob(file, 'staff')
                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'error')
        
        # Get department if program staff
        department = None
        if request.form.get('role') == 'program_staff':
            department = request.form.get('department')
        
        # Update staff member in database
        update_staff(
            staff_id=staff_id,
            name=request.form.get('name'),
            title=request.form.get('title'),
            bio=request.form.get('bio'),
            role=request.form.get('role'),
            email=request.form.get('email'),
            linkedin_url=request.form.get('linkedin_url'),
            image_url=image_url,
            department=department
        )
        
        flash('Staff member updated successfully!', 'success')
        return redirect(url_for('admin_staff'))
    
    return render_template('admin/staff_form.html', staff_member=staff_member)

@app.route('/admin/staff/delete/<int:staff_id>', methods=['POST'])
@login_required
def admin_delete_staff(staff_id):
    delete_staff(staff_id)
    flash('Staff member deleted successfully!', 'success')
    return redirect(url_for('admin_staff'))

# ===================================
# Admin - Program Images Management
# ===================================

@app.route('/admin/programs')
@login_required
def admin_programs():
    programs = get_all_programs()
    return render_template('admin/programs.html', programs=programs)

@app.route('/admin/programs/edit/<program_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_program_image(program_id):
    program = get_program_by_id(program_id)
    
    if not program:
        flash('Program not found.', 'error')
        return redirect(url_for('admin_programs'))
    
    if request.method == 'POST':
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                try:
                    image_url = upload_to_blob(file, 'program')
                    update_program_image(program_id, image_url)
                    flash(f'{program["name"]} image updated successfully!', 'success')
                    return redirect(url_for('admin_programs'))
                except Exception as e:
                    flash(f'Error uploading image: {str(e)}', 'error')
            else:
                flash('No valid file selected.', 'error')
    
    return render_template('admin/program_form.html', program=program)

# ===================================
# Admin - Images Management
# ===================================

@app.route('/admin/images')
@login_required
def admin_images():
    images = get_all_images()
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
        try:
            blob_url = upload_to_blob(file, 'upload')
            
            # Save to database
            create_image_record(
                filename=secure_filename(file.filename),
                blob_url=blob_url,
                category='general',
                size=0  # We can't easily get size from file object
            )
            
            flash('Image uploaded successfully!', 'success')
        except Exception as e:
            flash(f'Error uploading image: {str(e)}', 'error')
    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif, webp', 'error')
    
    return redirect(url_for('admin_images'))

@app.route('/admin/images/delete/<int:image_id>', methods=['POST'])
@login_required
def admin_delete_image(image_id):
    # Note: We're not deleting from Vercel Blob to avoid complexity
    # In production, you'd want to delete from blob storage too
    delete_image_record(image_id)
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_images'))

# ===================================
# Public Routes
# ===================================

@app.route('/')
def index():
    programs = get_all_programs()
    return render_template('index.html', current_page='home', programs=programs)

@app.route('/about')
def about():
    staff = get_all_staff()
    leadership_team = [member for member in staff if member['role'] == 'leadership']
    return render_template('about.html', current_page='about', leadership_team=leadership_team)

@app.route('/programs')
def programs():
    programs = get_all_programs()
    return render_template('programs.html', current_page='programs', programs=programs)

@app.route('/staff')
def staff():
    staff = get_all_staff()
    leadership_team = [member for member in staff if member['role'] == 'leadership']
    program_staff = [member for member in staff if member['role'] == 'program_staff']
    
    return render_template('staff.html', 
                         current_page='staff',
                         leadership_team=leadership_team,
                         program_staff=program_staff)

@app.route('/announcements')
def announcements():
    all_announcements = get_all_announcements()
    featured_announcements = [ann for ann in all_announcements if ann.get('featured', False)][:2]
    
    return render_template('announcements.html', 
                         current_page='announcements',
                         featured_announcements=featured_announcements,
                         all_announcements=all_announcements)

@app.route('/contact')
def contact():
    return render_template('contact.html', current_page='contact')

# Initialize database on first run
@app.before_request
def before_first_request():
    """Initialize database tables if they don't exist"""
    if not hasattr(app, 'db_initialized'):
        try:
            init_db()
            app.db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")

if __name__ == '__main__':
    app.run()
