# 🏥 Dental Clinic Management System (SaaS / Desktop)

A modern desktop application built for managing clinic appointments, budgets, and patient records efficiently. Designed with a sleek, dark-themed UI for optimal usability and fast financial workflow management.

---

## 🚀 Key Features

* **Financial Dashboard:** Dynamic cards displaying pending, approved, and canceled quotes in real-time.
* **Smart Budget Management:** Easily approve or cancel budgets with interactive action buttons and instant status updates.
* **Advanced Filtering:** Search budgets by patient name, status, and date range.
* **PDF Report Generation:** Export filtered financial reports directly to PDF with one click using ReportLab.
* **Patient & Consultation Management:** Organized view of patient records, consultation history, and missings/absences.

---

## 🛠️ Tech Stack & Technologies Used

* **Language:** [Python 3.10+](https://www.python.org/)
* **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Modern, dark-themed Tkinter extension)
* **Database / ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) & PyODBC / SQLite
* **PDF Reporting:** [ReportLab](https://www.reportlab.com/)

---

## 📦 Installation & Setup Guide

Follow these steps to set up and run the project locally on your machine.

### Prerequisites

Ensure you have **Python 3.10** or higher installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/Marcelo-Manzo/Consultorio.git
```

### 2. Create a Virtual Environment  (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 3. Install Dependencies
Install all required Python libraries:
```bash
pip install customtkinter sqlalchemy reportlab pyodbc
```

### Getting Started:
1- First, activate the Virtual Enviroment: .venv\Scripts\activate
2- run: python main.py
