# PML Sales Draft Generator 🚗

A professional web application designed to streamline the car sales process by generating polished, accurate, and ready-to-send sales drafts with automated calculations and professional formatting.

## 🌟 Features

- **Real-time Calculations**: Dynamic updates for net price, downpayment, trade-in balance, and finance details
- **Professional PDF Generation**: Clean, branded sales drafts with customer-specific details
- **Modern UI/UX**: Responsive design with intuitive user interface
- **Secure Authentication**: Flask-Login integration for user management
- **Admin Interface**: Database management capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.x
- Node.js (for Tailwind CSS)
- SQLite (or your preferred database)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sales-draft-generator.git
cd sales-draft-generator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:
```bash
npm install
```

4. Build Tailwind CSS:
```bash
npm run build:css
```

5. Run the application:
```bash
python main.py
```

## 🏗️ Project Structure

```
sales-draft-generator/
├── config.py           # Flask and SQLAlchemy configuration
├── main.py            # Application entry point
├── models.py          # Database models
├── pdf_utils.py       # PDF generation utilities
├── templates/         # HTML templates
│   ├── form.html
│   ├── login.html
│   ├── register.html
│   ├── sales_draft.html
│   └── index.html
├── static/            # Static assets
│   ├── js/           # JavaScript files
│   ├── css/          # CSS files
│   ├── images/       # Brand assets
│   └── audio/        # Sound effects
└── package.json      # Node.js dependencies
```

## 💡 Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **PDF Generation**: ReportLab
- **Authentication**: Flask-Login
- **Deployment**: Vercel

## 🛠️ Key Components

### Backend
- Flask framework for web application
- SQLAlchemy ORM for database management
- Flask-Login for authentication
- ReportLab for PDF generation

### Frontend
- Tailwind CSS for modern, responsive design
- Vanilla JavaScript for dynamic form behavior
- Interactive sound effects and animations

## 🔒 Security Features

- User authentication and session management
- Secure password handling
- Protected routes and resources
- Database connection pooling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


