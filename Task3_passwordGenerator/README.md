# Password Generator (Desktop GUI + Flask Web App)

A modern, cryptographically secure **Password Generator** application built with pure **Python**, featuring both a **Modern Desktop GUI (CustomTkinter)** and a **Deployable Web Application (Flask)**.

---

## 🚀 Overview

The **Password Generator** creates strong, customizable passwords using Python's standard `secrets` module for cryptographically secure randomness.

The project offers **two interfaces** sharing the exact same secure Python password-generation and strength scoring algorithms:
1. **Desktop GUI App**: Built with CustomTkinter and Tkinter.
2. **Web Application**: Built with Flask (Python backend) + responsive modern dark UI.

---

## ✨ Key Features

- **🔐 Cryptographically Secure Randomness**: Powered by Python's `secrets` module (`secrets.choice` and `secrets.randbelow`), immune to pseudo-random predictability.
- **🎚️ Dynamic Length Slider**: Select password lengths between **4** and **32** characters (Default: 16).
- **⚙️ Granular Character Customization**:
  - Uppercase letters (`A-Z`)
  - Lowercase letters (`a-z`)
  - Numbers (`0-9`)
  - Special symbols (`!@#$%^&*()-_=+[]{}?`)
- **🛡️ Guaranteed Character Diversity**: Guarantees at least one character from every active category, securely shuffled with a Fisher-Yates algorithm.
- **📊 Real-time Strength Indicator**: Evaluates entropy and categorizes strength as *Weak*, *Medium*, *Strong*, or *Very Strong*.
- **📋 One-Click Copy**: Click anywhere on the password card or the copy button to copy to the system clipboard with feedback (`✓ Copied!`).
- **↺ Reset to Defaults**: Restore standard settings with a single click.
- **🛡️ Input Validation**: Friendly, graceful error handling if all character types are disabled.

---

## 📦 Project Structure

```
password-generator/
│
├── app.py                 # Flask Web Server (Python Backend)
├── main.py                # Desktop GUI App & Core Python Generation Logic
├── password_generator.py  # Wrapper execution entry point
│
├── templates/             # Web HTML Templates
│   └── index.html         # Modern web interface layout
│
├── static/                # Static Web Assets
│   ├── style.css          # Premium Dark Navy CSS styling
│   └── script.js          # Client-side UI controller (communicates with Flask)
│
├── requirements.txt       # Project dependencies
└── README.md              # Documentation & Deployment Guide
```

---

## 💻 Installation & Setup

1. Open your terminal in the project directory:
   ```bash
   cd "c:/Users/ss/OneDrive/Desktop/password generator"
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ How to Run

### Option A: Run the Web App (Flask)
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

### Option B: Run the Desktop GUI
```bash
python main.py
```
or
```bash
python password_generator.py
```

---

## 🌐 Public Deployment Guide

To host this project online so anyone can access it via a public link (e.g. for internships and portfolios):

### Recommended Free / Easy Hosting Options:

1. **Render (Recommended)**:
   - Push your code to GitHub.
   - Go to [render.com](https://render.com) and create a new **Web Service**.
   - Connect your repository.
   - Set **Build Command**: `pip install -r requirements.txt`
   - Set **Start Command**: `gunicorn app:app`
   - Render will generate a free public HTTPS URL (e.g., `https://your-password-generator.onrender.com`).

2. **PythonAnywhere**:
   - Create a free account on [pythonanywhere.com](https://www.pythonanywhere.com).
   - Upload the project files or pull from GitHub.
   - Configure a Flask Web App pointing to `app.py`.

3. **Railway / Vercel**:
   - Deploy directly from GitHub repository.

---

## 📄 License
This project is open-source and built for educational and portfolio demonstration.
