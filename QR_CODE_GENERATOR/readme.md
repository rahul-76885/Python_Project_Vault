# 📦 Branded QR Code Generator

A **professional, research-oriented Python project** that generates **branded QR codes** with a logo embedded at the center while maintaining **high scannability** using QR error-correction principles.

This approach mirrors how **real-world brands** (Paytm, Spotify, LinkedIn, Google Pay) design QR codes for marketing and payments.

---

## 🚀 Overview

Standard QR codes are functional but visually plain. This project enhances QR codes by:

* Applying **high error correction**
* Embedding a **center logo** without breaking scannability
* Preserving **transparency and visual quality** using RGBA images

The project demonstrates how **computer vision principles + QR standards** can be applied in a practical branding use case.

---

## ✨ Features

* Generate QR codes from URLs or text
* High error correction (H) for fault tolerance
* Center logo embedding (industry-safe zone)
* RGBA image processing for transparency
* Production-ready PNG output

---

## 🛠 Tech Stack

* **Python 3.x**
* **qrcode** – QR encoding & error correction
* **Pillow (PIL)** – Image processing & manipulation

---

## 📦 Installation

Install all required dependencies using:

```bash
pip install qrcode[pil] pillow
```

---

## ⚙️ How It Works (High-Level)

1. QR data is encoded using the `qrcode` library
2. High-level error correction (H) is applied to tolerate data loss
3. The QR matrix is rendered as an image using Pillow
4. The logo is resized to a safe dimension
5. The logo is placed at the **center**, avoiding QR critical regions
6. RGBA mode ensures clean transparency and professional output

---

## 🧠 Why the QR Does Not Break

QR codes include **Reed–Solomon error correction**, allowing scanners to recover data even if part of the QR is damaged or covered.

| Error Level | Damage Tolerance |
| ----------- | ---------------- |
| L           | ~7%              |
| M           | ~15%             |
| Q           | ~25%             |
| **H**       | **~30%**         |

By combining **ERROR_CORRECT_H** with center logo placement, the QR remains scannable.

---

## 🖼 Example Output

The generated QR code includes:

* Clear finder patterns
* Central logo branding
* Strong black–white contrast

*(Add an image preview here if publishing on GitHub)*

---

## 📁 Project Structure

```text
.
├── brand_qr.png        # Generated QR output
├── logo.png            # Center logo image
├── qr_generator.py     # Main script
├── README.md
```

---

## 🔍 Research & Design Notes

* Logo size should not exceed **25% of QR width**
* Center placement avoids timing and finder patterns
* RGBA prevents unwanted background artifacts
* `fit=True` ensures scalability for larger data

---

## 🔮 Future Improvements

* SVG export for print-quality QR codes
* Gradient and rounded module styling
* Batch QR generation
* QR scannability validation script
* Flask/FastAPI web interface

---

## 📌 Use Cases

* Personal branding (LinkedIn, portfolio)
* Marketing materials
* Event check-ins
* Payment QR customization
* Research & learning projects

---

## 📜 License

This project is open-source and free to use for educational and personal purposes.

---

> **Note:** This project focuses on understanding *why* branded QR codes work, not just *how* to generate them.
