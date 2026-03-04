![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

# Notevergent
### *Tune your own note.*

Notevergent is a security-aware, minimal note management system built with Flask. It focuses on clarity, controlled access, and traceable change history while maintaining a distraction-free interface. The name combines "Note" and "Divergent", carrying a double meaning: musical notes and written notes. The design philosophy values diversity, personal rhythm, and cognitive simplicity.

---

## 💡 Project Motivation

This project originated from a personal need for a clean, low-friction note tracking environment. Many productivity tools are visually and functionally overwhelming. Notevergent was designed around the idea of reducing visual noise and providing a controlled, calm workspace. Interface decisions were guided by clarity and focus. Design concepts are intentionally based on simplicity and minimalism. Additionally, tracking change can be as important as storing information for control-oriented users. Therefore, the action history system provides a structured and auditable foundation.

---

## 🧰 Technologies Used

| 🖥️ Backend | 🎨 Frontend & Styling |🔧 Tools & Infrastructure |
| :--- | :--- | :--- |
| • Python 3.11+ | • HTML5 | • Brevo SMTP |
| • Flask & SQLAlchemy | • Bootstrap 5 | • aiosmtpd (Testing)  |
| • Flask-Migrate | • Custom SCSS | • Environment Config |
| • Flask-Login | • Vanilla JS (AJAX) |  |
| • Flask-WTF (CSRF) | • Node.js & npm  |   |
| • Flask-Limiter | • Sass (via npx CLI) | |
| • bcrypt | | |
| • SQLite (local)| | |
| • PostgreSQL (Neon) |||

---

## 🏗️ Technical Architecture

### ⚙️ Backend Architecture

- Flask application structured using the **App Factory** pattern
- **SQLAlchemy ORM** for relational modeling
- **UUID-based** internal identifiers, abstracted with public short IDs
- Centralized token validation system for authentication and security
- Environment-based configuration with production-ready structure

### 🔐 Authentication & Account Lifecycle

- Mandatory **email verification** (token-based)
- Token-based **password reset** for account recovery
- Secure account deletion with **confirmation token**
- Password change feature for authenticated users
- Expired unverified account cleanup
- Login session management with **remember-me** support

### 🛡️ Security Design

- **CSRF protection** (including AJAX requests)
- **Rate limiting** on sensitive authentication routes to prevent brute-force attacks
- Password hashing with **bcrypt**
- Token types separated via **enum** structure
- No-cache headers on authentication routes
- Security logging (IP address and User-Agent tracking)

### 📝 Note System

- Full **CRUD** operations
- Field-level change detection
- Automatic structured **history logging**
- Filterable history **API** (JSON-based)
- Many-to-many sharing infrastructure (backend-ready)
- **Server-side filtering** (Today, Week, Month, Action Type)
- Local timezone normalization

### 🎨 Frontend Interaction Layer

- **AJAX-based** state updates
- Dynamic DOM reordering without framework dependency
- Modal-based create, edit, and read system
- UTC to local timezone conversion
- JSON API consumption for history filtering

### 📧 Email Infrastructure

- **SMTP** integration via **Brevo**
- Verification and password reset workflow emails
- Production-ready email templating

---

## 📐 Architecture Decisions

Several deliberate design choices differentiate this project from a basic CRUD application:

- **App Factory** pattern ensures scalability and testability
- Centralized token validation prevents scattered security logic
- Token types are explicitly separated for lifecycle control
- Internal UUIDs are abstracted from public-facing identifiers
- Expired account cleanup is triggered during authentication flow
- Note history is structured for auditability rather than simple logging
- Backend-ready many-to-many sharing system for future UI integration
- Environment-based configuration separates development and production behavior
- Orphan removal on account deletion to maintain a privacy-focused design

These decisions prioritize maintainability, traceability, and security awareness.

---

## 🧬 Core Features

- Create, edit, and delete notes
- Dynamic status switching (In Progress / Completed)
- Full structured action history with filters (Today, Week, Month, Action Type)
- Server-side filtering API for enhanced performance and privacy
- Automatic deletion of all user-related tracking data upon account deletion
- Email verification workflow
- Secure password reset flow
- Account recovery system
- Shared notes backend infrastructure (planned UI integration)

---

## 🤖 AI Usage Disclosure

AI tools were used during development as an assistant for:

- Debugging support
- JavaScript timezone conversion suggestions
- AJAX structure refinement
- Refactoring recommendations
- Security pattern review discussions
- Frontend implementation in specific areas

All architectural decisions, database modeling, security logic, and feature implementation were authored and fully understood by the developer. AI functioned strictly as a development assistant, not as an autonomous implementation engine.

---

## 🚀 Deployment

> **Live Demo:** https://notevergent.vercel.app

Designed to be deployable on production platforms such as Vercel + Neon:

- Environment-based configuration
- External SMTP provider (Brevo)
- Secure secret management
- Production-ready project structure
- Deployed on Vercel (Frankfurt region)
- PostgreSQL database hosted on Neon.tech

---

## 🗺️ Future Roadmap

- [ ] Shared notes UI integration
- [ ] PDF and DOCX export system
- [ ] Tag-based filtering
- [ ] Full-text search
- [ ] Background task queue for automated cleanup
- [ ] Role-based access control
- [ ] Improved audit referential integrity
- [ ] Accessibility testing refinement

---

## 📍 Closing Perspective

Notevergent is not designed to be a feature-heavy productivity suite. It is intentionally structured, security-conscious, and minimal. The focus is not on maximizing features, but on creating a controlled environment where notes remain traceable, secure, and intentional. Tune your own note.

---

## 🛠️ Requirements & Setup

### Prerequisites

- Python 3.11+
- pip package manager
- Node.js (for SCSS compilation)
- npm (Node Package Manager)
- SQLite (for local development only)
- PostgreSQL via Neon.tech (for production)
- Brevo (formerly Sendinblue) account for email delivery
  or
- Local SMTP test server using aiosmtpd

### Installation
```bash
# Clone the repository
git clone https://github.com/JaguarKaptan/Final_Project.git
cd Final_Project

# Create a virtual environment
python -m venv venv
# Activate it
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root with the following format:
```
SECRET_KEY=your_secret_key_here
SQLALCHEMY_DATABASE_URI=sqlite:///notevergent.db  # local development
# For production use Neon.tech PostgreSQL connection string
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_brevo_username
MAIL_PASSWORD=your_brevo_password
MAIL_DEFAULT_SENDER="Notevergent Bot <noreply@example.com>"
```

**Configuration Notes**

- `SECRET_KEY`: Flask secret key used for session security. A secure key can be generated using the included `secret.py` script.
- `SQLALCHEMY_DATABASE_URI`: Database connection string (SQLite or another supported database engine).
- `MAIL_*`: Brevo SMTP credentials used for verification and password reset emails.

### Optional: Local Mail Testing

For development purposes, a local SMTP test server can be used instead of Brevo.
Example configuration in `.env` and application settings:
```
MAIL_SERVER=localhost
MAIL_PORT=8025
MAIL_USE_TLS=False
MAIL_USE_SSL=False
MAIL_SUPPRESS_SEND=False
MAIL_DEFAULT_SENDER="Test Bot <test@example.com>"
```

Start a local SMTP listener:
```bash
python -m aiosmtpd -n -l localhost:8025
```

### Database Setup

Before running the project, initialize and migrate the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

### Running the Project

1. Create and configure the `.env` file.
2. Complete the database setup.
3. Start the application:
```bash
   python run.py
```
4. Open: `http://localhost:5000`

The mail system will function if Brevo credentials are properly configured or if the local SMTP listener is running.

### Frontend Styling Workflow

The project uses custom **SCSS** for styling. SCSS files are compiled into CSS using the **Sass CLI** via npx. This approach enables modular styling, variable management, and maintainable design structure compared to plain CSS.

**Prerequisites for Styling**

- Node.js
- npm

To install Sass locally (if not already installed globally):
```bash
npm install sass
```

**Compiling SCSS (Watch Mode)**

The project uses the following command to continuously compile SCSS into CSS:
```bash
npx sass --watch static/scss/custom.scss:static/css/custom.css
```

This command watches the `custom.scss` file and automatically regenerates `custom.css` whenever changes are detected.

**Styling Structure**

- `static/scss/custom.scss` → Main SCSS source file
- `static/css/custom.css` → Compiled CSS output file

The compiled CSS file is served by Flask in production.