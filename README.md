# Employee-Daily-Work-Management-System

A browser-based office file management system that allows employees to securely upload, manage, download, and share files while providing administrators with user management, file management, and activity monitoring.

---

## 📌 Overview

The **Office Web Portal** provides a centralized platform for employees and administrators to manage office files.

### 👤 Employee

* Secure login
* Personal file management
* Common/shared file access
* Drag-and-drop file upload
* Multiple file upload
* Upload progress tracking
* File download
* File deletion
* Logout

### 👨‍💼 Admin

* Admin dashboard
* Employee management
* Create and update employees
* Reset employee passwords
* Activate/deactivate accounts
* View all uploaded files
* Delete files
* View activity logs
* Monitor storage and user activity

---

# 🖥️ Frontend

The frontend is a React Single Page Application that provides the user interface for employees and administrators.

### Technologies

* React.js
* Vite
* React Router DOM
* Axios
* React Dropzone
* Lucide React

### Features

* Login
* Dashboard
* File Upload
* Personal Files
* Common Files
* File Download
* File Delete
* Upload Progress
* Admin Dashboard
* User Management
* File Management
* Activity Logs
* Protected Routes

### Frontend Pages

```text
/login
/
/upload
/files/personal
/files/common
/admin
/admin/users
/admin/files
/admin/logs
```

---

# ⚙️ Backend

The backend provides REST APIs and handles authentication, authorization, file management, database operations, and activity logging.

### Technologies

* Python
* Flask
* Flask REST API
* SQLite3
* Gunicorn
* Werkzeug
* Flask-CORS

### Features

* User Authentication
* Role-Based Authorization
* Session Management
* File Upload
* File Download
* File Deletion
* Personal & Common File Management
* User Management
* Password Reset
* File Validation
* Activity & Audit Logging
* Admin APIs

---

# 📂 Project Structure

```text
Office-Web-Portal/
│
├── frontend/
│   │
│   ├── public/
│   │
│   ├── src/
│   │   ├── assets/
│   │   │
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── FileList.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── PersonalFiles.jsx
│   │   │   ├── CommonFiles.jsx
│   │   │   │
│   │   │   └── admin/
│   │   │       ├── AdminDashboard.jsx
│   │   │       ├── Users.jsx
│   │   │       ├── Files.jsx
│   │   │       └── Logs.jsx
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── backend/
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── files.py
│   │   └── admin.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── file.py
│   │   └── activity_log.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── file_service.py
│   │   └── user_service.py
│   │
│   ├── middleware/
│   │   ├── auth.py
│   │   └── admin.py
│   │
│   ├── utils/
│   │   ├── security.py
│   │   ├── file_validation.py
│   │   └── logger.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── schema.sql
│   │
│   ├── app.py
│   ├── config.py
│   └── requirements.txt
│
├── nginx/
│   └── officeportal.conf
│
├── systemd/
│   └── officeportal.service
│
├── README.md
└── .gitignore
```

---

# 🏗️ Architecture

```text
              Employee / Admin
                     │
                     ▼
              React Frontend
                     │
                     ▼
                   Nginx
                     │
                     ▼
              Flask REST API
                     │
            ┌────────┴────────┐
            ▼                 ▼
         SQLite          File Storage
        portal.db        /srv/office
```

---

# 🔌 REST API

## Authentication

| Method | Endpoint           | Description      |
| ------ | ------------------ | ---------------- |
| POST   | `/api/auth/login`  | User login       |
| POST   | `/api/auth/logout` | User logout      |
| GET    | `/api/auth/me`     | Get current user |

## Dashboard

| Method | Endpoint               | Description          |
| ------ | ---------------------- | -------------------- |
| GET    | `/api/dashboard/stats` | Dashboard statistics |

## Files

| Method | Endpoint                   | Description        |
| ------ | -------------------------- | ------------------ |
| POST   | `/api/files/upload`        | Upload file        |
| GET    | `/api/files/personal`      | Get personal files |
| GET    | `/api/files/common`        | Get common files   |
| GET    | `/api/files/download/<id>` | Download file      |
| DELETE | `/api/files/<id>`          | Delete file        |

## Admin

| Method | Endpoint                               | Description      |
| ------ | -------------------------------------- | ---------------- |
| GET    | `/api/admin/stats`                     | Admin statistics |
| GET    | `/api/admin/users`                     | Get users        |
| POST   | `/api/admin/users`                     | Create user      |
| PUT    | `/api/admin/users/<id>`                | Update user      |
| DELETE | `/api/admin/users/<id>`                | Delete user      |
| POST   | `/api/admin/users/<id>/reset-password` | Reset password   |
| GET    | `/api/admin/files`                     | Get all files    |

---

# 🗄️ Database

The application uses SQLite with three main tables:

### Users

```text
users
├── id
├── username
├── password_hash
├── role
├── is_active
└── created_at
```

### Files

```text
files
├── id
├── user_id
├── username
├── folder
├── original_name
├── stored_name
├── size
└── uploaded_at
```

### Activity Logs

```text
activity_logs
├── id
├── user_id
├── username
├── action
├── detail
├── ip
├── status
└── created_at
```

---

# 📁 File Storage

The application uses separate personal folders for employees and a common folder for shared files.

```text
/srv/office/
│
├── common/
│
└── users/
    ├── employee1/
    ├── employee2/
    └── employee3/
```

The web portal and Samba shared folders use the same physical storage location.

---

# 🔐 Security

The system provides:

* Authentication
* Role-Based Access Control
* Password Hashing
* Personal File Protection
* Session Timeout
* Failed Login Protection
* File Type Restrictions
* Maximum File Size Validation
* Activity Logging
* IP Address Logging

Blocked file types include:

```text
.exe
.bat
.sh
.msi
.vbs
.cmd
```

---

# 🚀 Installation

## Backend

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate the environment:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

## Frontend

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Create a production build:

```bash
npm run build
```

---

# 🎯 Project Goal

The **Office Web Portal** provides a centralized and secure platform for managing employee files, shared documents, users, and system activity through a simple web interface.
