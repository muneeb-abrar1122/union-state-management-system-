# Union Estate Management System

A complete real estate management application built with Flask. This system helps you manage clients, properties, and users with a secure admin panel.

## What This App Does

- **Manage Clients**: Add, edit, view, and delete client information
- **Track Properties**: Keep records of plots, societies, and property details
- **User Management**: Admin can create and manage multiple users
- **Secure Login**: Password-protected access for both main app and admin panel
- **Mobile Friendly**: Works perfectly on phones and tablets

## How to Install and Run

### Step 1: Download the Project

```bash
git clone https://github.com/muneeb-abrar1122/union-state-management-system-.git
cd union-state-management-system-
```

### Step 2: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

```bash
python app.py
```

### Step 4: Open in Browser

Go to: `http://localhost:5000`

## Login Information

**Main Application:**
- Username: `union`
- Password: `union1234`

**Admin Panel:**
- Go to: `http://localhost:5000/admin`
- Password: `admin123`

## Features Explained

### For Regular Users
1. **Login** to access the system
2. **View all clients** in a clean table
3. **Add new clients** with property details
4. **Edit client information** anytime
5. **Delete clients** when needed
6. **Search and filter** to find specific clients

### For Administrators
1. **Access admin panel** with separate password
2. **Manage users** - create, edit, delete user accounts
3. **View all clients** from admin dashboard
4. **Change admin password** from settings
5. **See statistics** - total users and clients

## What's Inside

```
union-state-management-system/
├── app.py                  # Main application code
├── models.py               # Database structure
├── requirements.txt        # Required Python packages
├── templates/              # HTML pages
│   ├── admin/             # Admin panel pages
│   ├── index.html         # Main dashboard
│   └── login.html         # Login page
└── static/                # CSS and images
    └── css/
        └── style.css      # Styling
```

## Technologies Used

- **Flask** - Python web framework
- **SQLite** - Database for storing data
- **Flask-Login** - User authentication
- **Flask-Admin** - Admin panel
- **bcrypt** - Password security
- **Bootstrap 4** - Beautiful UI design

## How to Deploy Online

### Option 1: Render (Recommended - Free)

1. Push code to GitHub (you're already doing this!)
2. Go to [Render.com](https://render.com)
3. Sign up with GitHub
4. Click "New +" → "Web Service"
5. Connect your repository
6. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
7. Click "Create Web Service"
8. Wait 5-10 minutes
9. Your app is live!

### Option 2: PythonAnywhere (Also Free)

1. Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Upload your code
3. Set up a web app
4. Configure WSGI file
5. Your app is live!

## Important Notes

- **Database**: All data is saved in `database.db` file
- **Security**: Passwords are encrypted with bcrypt
- **Sessions**: Users stay logged in until they logout
- **Admin Access**: Only people with admin password can access admin panel

## Need Help?

If you have questions:
1. Check if all packages are installed: `pip install -r requirements.txt`
2. Make sure Python 3.7+ is installed
3. Check if port 5000 is available
4. Look at error messages in terminal

## License

This project is free to use for educational purposes.

---

