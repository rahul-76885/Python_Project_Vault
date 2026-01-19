# 🌐 Flask Projects (Backend & APIs)

This folder contains **Flask-based backend projects** built as part of my applied Python learning journey. These projects focus on **practical backend development**, **API design**, and **real-world use cases**, rather than frontend-heavy applications.

Flask is used here as a **lightweight, flexible backend framework** to understand how real systems expose functionality via HTTP APIs.

---

## 🎯 Purpose of This Folder

The goal of these Flask projects is to:

* Learn **backend fundamentals** (routing, requests, responses)
* Build **REST-style APIs**
* Integrate Python logic with web interfaces
* Prepare a foundation for **FastAPI, Django, and ML-serving APIs**

These projects emphasize **clarity, modularity, and correctness** over complexity.

---

## 🧠 Why Flask?

Flask is chosen because it:

* Is minimal and easy to reason about
* Does not hide backend logic behind heavy abstractions
* Helps understand core concepts like:

  * Request–response cycle
  * URL routing
  * Templates vs APIs
  * Middleware & extensions

This makes Flask ideal for **learning-oriented and utility backend projects**.

---

## 📁 Folder Structure (Typical)

```text
Flask-Projects/
│
├── project-name/
│   ├── app.py
│   ├── templates/
│   ├── static/
│   ├── requirements.txt
│   └── README.md
│
└── README.md   ← You are here
```

Each project:

* Is self-contained
* Can be run independently
* Has its own README explaining the specific use case

---

## 🧩 Types of Projects Included

Projects in this folder focus on **Flask fundamentals + database-backed applications**, such as:

* CRUD-based applications using Flask & SQLAlchemy
* Template-driven web apps (Jinja2)
* Database modeling with ORM (SQLite for learning)
* Transition projects from static data → database-driven systems

These projects emphasize:

* Clean separation of concerns
* ORM-based data access (no raw SQL)
* Readable, maintainable backend code

They act as a **bridge between Python scripting and full backend systems**.

---

## ⚙️ Core Concepts Practiced

* Flask application fundamentals
* Application configuration & context
* SQLAlchemy ORM models
* Database querying via Python objects
* Passing database results to templates

---

> This folder represents my backend foundation work using Flask, databases, and clean project structure before moving to FastAPI and ML-backed services.

---

## ⚙️ Common Technologies Used

* **Python**
* **Flask**
* Jinja2 (templates, where applicable)
* SQLAlchemy / SQLite (if database is used)
* Third-party Python libraries (project-specific)

---
🧠 Why Flask (at This Stage)

Flask is chosen here not because it is "easy", but because it is explicit.

Flask:

Exposes the request–response lifecycle clearly

Does not hide routing, configuration, or extensions

Forces the developer to understand what is happening

Key concepts learned through Flask:

Application context

URL routing

Template rendering vs APIs

Extension initialization (SQLAlchemy)

This makes Flask an ideal stepping stone before moving to FastAPI (async, typed APIs) or Django (full-stack systems).

📁 Actual Project Structure (Package-Based Flask App)

FLASK_MARKET/
│
├── market/                 # Python package (application logic)
│   ├── __init__.py         # App creation & extension binding
│   ├── model.py            # Database models (ORM layer)
│   ├── routes.py           # HTTP routes / views
│   └── templates/          # Jinja2 templates
│
├── instance/               # Runtime data (SQLite DB, config)
├── env/                    # Virtual environment (ignored by git)
├── run.py                  # Application entry point
├── README.md               # Documentation
└── .gitignore

This structure mirrors real Flask applications, not tutorials.

### 🔹 Learning Outcome

This Flask setup is intentionally simple. It exists to:

* Build backend intuition
* Understand ORM-based database access
* Prepare for larger systems (FastAPI, ML services, dashboards)

Complex research-grade systems are maintained in **separate standalone repositories**.

---

> These notes are intentionally kept in the README so the code remains clean while the **conceptual understanding is preserved for future revision**.


## 🚀 How to Run a Flask Project (General)

```bash
pip install -r requirements.txt
python app.py
```

Then open:

```
http://127.0.0.1:5000/
```

---

## 🧠 Learning Focus

These projects help develop:

* Backend logic building
* Clean API structure
* Debugging skills
* Understanding of how Python powers web services

They also act as a **stepping stone toward FastAPI-based ML services** and full-stack systems.

---

## 📌 Notes

* Flask projects here are intentionally kept **simple and focused**
* Larger ML or research systems are maintained in **separate dedicated repositories**
* This folder supports my overall goal of building **end-to-end systems**

---

## 📫 Author

Rahul Raj
B.Tech CSE (AI) | Backend & Applied Python

---

> This folder represents my backend foundation work using Flask before moving to larger-scale systems.

---
