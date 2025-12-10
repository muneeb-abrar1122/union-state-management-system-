from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Client, User, AdminSettings
import os
from datetime import datetime
import time
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField
from flask_wtf.csrf import CSRFProtect
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
CORS(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Flask-Admin Configuration ---

class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        # No session clearing - allow free navigation within admin panel
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        
        # Dashboard Stats
        total_clients = Client.query.count()
        total_users = User.query.count()
        recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
        
        return self.render('admin/dashboard.html', 
                         total_clients=total_clients, 
                         total_users=total_users,
                         recent_clients=recent_clients)

from flask_admin.form import BaseForm

class NoCsrfForm(BaseForm):
    class Meta:
        csrf = False

class SecureModelView(ModelView):
    form_base_class = NoCsrfForm

    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

class UserModelView(SecureModelView):
    column_list = ('username', 'email', 'created_at')
    form_columns = ('username', 'email', 'password')
    form_excluded_columns = ('password_hash',)
    
    form_extra_fields = {
        'password': PasswordField('New Password')
    }
    
    def on_model_change(self, form, model, is_created):
        # Hash password if provided
        if form.password.data:
            model.set_password(form.password.data)

class ClientModelView(SecureModelView):
    column_searchable_list = ['name', 'contact', 'plotNo', 'society', 'block']
    column_filters = ['block', 'date', 'price', 'size']
    column_editable_list = ['price']
    can_export = True
    can_view_details = True
    page_size = 20
    
    column_labels = {
        'plotNo': 'Plot #',
        'name': 'Client Name'
    }

# Initialize Admin with Bootstrap 4
admin = Admin(app, name='UnionEstate Manager', index_view=DashboardView(), template_mode='bootstrap4')
# Using custom routes for User management instead of Flask-Admin ModelView
admin.add_view(ClientModelView(Client, db.session, name='Clients', endpoint='clients'))

# Routes
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
@csrf.exempt
def admin_login():
    if session.get('admin_logged_in'):
        return redirect('/admin')
        
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Check against AdminSettings (independent admin password)
        admin_settings = AdminSettings.query.first()
        if admin_settings and admin_settings.check_password(password):
            session['admin_logged_in'] = True
            session['admin_login_time'] = time.time()  # Store login timestamp
            return redirect('/admin')
            
        flash('Invalid admin password')
    
    return render_template('admin/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@csrf.exempt
def admin_settings():
    # No session clearing - allow free navigation within admin panel
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Get AdminSettings (independent admin password)
        admin_settings = AdminSettings.query.first()
        if not admin_settings:
            flash('Admin settings not found')
            return redirect(url_for('admin_settings'))
            
        if not admin_settings.check_password(current_password):
            flash('Current password is incorrect')
            return redirect(url_for('admin_settings'))
            
        if new_password != confirm_password:
            flash('New passwords do not match')
            return redirect(url_for('admin_settings'))
            
        if len(new_password) < 6:
            flash('Password must be at least 6 characters')
            return redirect(url_for('admin_settings'))
            
        admin_settings.set_password(new_password)
        db.session.commit()
        flash('Admin password updated successfully')
        
    return render_template('admin/settings.html', 
                         total_users=User.query.count(), 
                         total_clients=Client.query.count())

@app.route('/register', methods=['GET', 'POST'])
@csrf.exempt
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# Admin User CRUD Routes
@app.route('/admin/users/list')
def admin_users_list():
    # No session clearing - allow free navigation within admin panel
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
@csrf.exempt
def admin_create_user():
    # No session clearing - allow free navigation within admin panel
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('admin/user_form.html', user=None, action='create')
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('admin/user_form.html', user=None, action='create')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully')
        return redirect('/admin/users/list')
    
    return render_template('admin/user_form.html', user=None, action='create')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@csrf.exempt
def admin_edit_user(user_id):
    # No session clearing - allow free navigation within admin panel
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists')
            return render_template('admin/user_form.html', user=user, action='edit')
        
        # Check if email is taken by another user
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user_id:
            flash('Email already exists')
            return render_template('admin/user_form.html', user=user, action='edit')
        
        user.username = username
        user.email = email
        if password:  # Only update password if provided
            user.set_password(password)
        
        db.session.commit()
        flash('User updated successfully')
        return redirect('/admin/users/list')
    
    return render_template('admin/user_form.html', user=user, action='edit')

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@csrf.exempt
def admin_delete_user(user_id):
    # No session clearing - allow free navigation within admin panel
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted successfully'})


# API Endpoints
@app.route('/api/clients', methods=['GET'])
@login_required
def get_clients():
    clients = Client.query.order_by(Client.created_at.desc()).all()
    return jsonify([client.to_dict() for client in clients])

@app.route('/api/clients', methods=['POST'])
@csrf.exempt
@login_required
def create_client():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
            
        if not data.get('id'):
            data['id'] = str(int(datetime.utcnow().timestamp() * 1000))
        
        client = Client(
            id=data.get('id'),
            name=data.get('name', ''),
            contact=data.get('contact', ''),
            society=data.get('society', ''),
            plotNo=data.get('plotNo', ''),
            block=data.get('block', 'A'),
            price=data.get('price', ''),
            size=data.get('size', ''),
            date=data.get('date', ''),
            description=data.get('description', '')
        )
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify(client.to_dict()), 201
    except Exception as e:
        print(f"Error creating client: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/clients/<client_id>', methods=['PUT'])
@csrf.exempt
@login_required
def update_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    data = request.json
    client.name = data.get('name', client.name)
    client.contact = data.get('contact', client.contact)
    client.society = data.get('society', client.society)
    client.plotNo = data.get('plotNo', client.plotNo)
    client.block = data.get('block', client.block)
    client.price = data.get('price', client.price)
    client.size = data.get('size', client.size)
    client.date = data.get('date', client.date)
    client.description = data.get('description', client.description)
    
    db.session.commit()
    
    return jsonify(client.to_dict())

@app.route('/api/clients/<client_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    db.session.delete(client)
    db.session.commit()
    
    return jsonify({'message': 'Client deleted successfully'})

@app.route('/api/clients/import', methods=['POST'])
@csrf.exempt
@login_required
def import_clients():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Expected array of clients'}), 400
    
    Client.query.delete()
    
    for item in data:
        if not item.get('id'):
            item['id'] = str(int(datetime.utcnow().timestamp() * 1000))
        
        client = Client(
            id=item.get('id'),
            name=item.get('name', ''),
            contact=item.get('contact', ''),
            society=item.get('society', ''),
            plotNo=item.get('plotNo', ''),
            block=item.get('block', 'A'),
            price=item.get('price', ''),
            size=item.get('size', ''),
            date=item.get('date', ''),
            description=item.get('description', '')
        )
        db.session.add(client)
    
    db.session.commit()
    
    return jsonify({'imported': len(data)})

# Initialize database and create default admin
def create_admin():
    with app.app_context():
        db.create_all()
        
        # Create default main app user
        user = User.query.filter_by(username='union').first()
        if not user:
            user = User(
                username='union',
                email='union@unionestate.com'
            )
            user.set_password('union1234')
            db.session.add(user)
            db.session.commit()
            print('Default user created: union / union1234')
        else:
            print('User union already exists')
        
        # Create independent admin panel password
        admin_settings = AdminSettings.query.first()
        if not admin_settings:
            admin_settings = AdminSettings()
            admin_settings.set_password('admin123')
            db.session.add(admin_settings)
            db.session.commit()
            print('Admin panel password created: admin123')
        else:
            print('Admin settings already exist')

if __name__ == '__main__':
    create_admin()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
