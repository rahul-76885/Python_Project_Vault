# Image Downloader CLI (imgdl)

> A **research-oriented, system-level Python CLI project** demonstrating how real-world command-line tools are designed, packaged, and executed globally.

This project aligns with my long-term goal of becoming a **strong software engineer with deep system and tooling knowledge**, beyond just writing scripts.

---

## 📌 Abstract

Command-line interfaces (CLIs) are foundational tools in software engineering, DevOps, backend systems, and research workflows.  
This project explores how a Python function can be transformed into a **globally accessible CLI tool**, similar to `pip`, `git`, or `flask`.

The tool allows users to download images from the internet using a direct image URL while showcasing:
- Python packaging
- Argument parsing
- Entry-point based execution
- Cross-platform global availability

---

## 🎯 Motivation

Most beginners write Python scripts that only work when run from a specific folder.  
This project answers **research-level questions** such as:

- How does a Python command become globally accessible?
- What happens internally when we type a command in CMD?
- How does `pip` expose executables?
- How should logic and interface layers be separated?

This project was built to **understand those mechanisms deeply**, not just to download images.

---

## 🧠 System Design Overview

```text
User Command (imgdl)
        │
        ▼
Python Launcher (Scripts/imgdl.exe)
        │
        ▼
entry_points (setup.py)
        │
        ▼
CLI Interface (argparse)
        │
        ▼
Core Logic Function
        │
        ▼
File System (image saved locally)
```

---

## 🧩 Project Architecture

```
image-downloader-cli/
├── image_downloader/
│   ├── __init__.py      # Package marker
│   └── cli.py           # Core logic + CLI interface
├── setup.py             # Packaging & global command exposure
├── README.md
```

---

## 🧪 Execution Modes

### 1️⃣ Individual Script Execution (Research / Testing)

```bash
python cli.py
```

Used during development to validate logic without CLI overhead.

---

### 2️⃣ Global CLI Execution (Production Mode)

```bash
imgdl --url IMAGE_URL --output filename.png
```

Enabled via `setup.py` entry points.

---

## ⚙️ Installation

### Install directly from GitHub

```bash
pip install git+https://github.com/<your-username>/image-downloader-cli.git
```

### Or clone and install locally

```bash
git clone https://github.com/<your-username>/image-downloader-cli.git
cd image-downloader-cli
pip install .
```

---

## 🪟 Windows Environment Note

On Windows, Python CLI executables are installed in:

```
C:\Users\<USERNAME>\AppData\Roaming\Python\Python3XX\Scripts
```

This directory **must be added to PATH**.  
Restart CMD after updating PATH.

---

## ▶️ Usage

```bash
imgdl --help
```

```bash
imgdl --url https://images.unsplash.com/photo-1503023345310-bd7c1de61c7d --output rahul.png
```

---


## 🧠 Key Engineering Concepts Demonstrated

- Separation of concerns (logic vs interface)
- Safe imports using `if __name__ == "__main__"`
- Argument parsing with `argparse`
- Global CLI exposure using `entry_points`
- OS-level PATH resolution
- Cross-platform packaging

---

## 📈 Relevance to Long-Term Goals

This project supports my goal of becoming a **high-impact engineer / AI-ML researcher** by:

- Strengthening system-level understanding
- Building tooling used in real research workflows
- Moving beyond notebook-only development
- Learning how professional developer tools are built

---

## 🗑️ Uninstall

```bash
pip uninstall image-downloader-cli
```

---

## 🔚 Conclusion

This project is not just a utility —  
it is an **experiment in understanding how software tools work beneath the surface**.

