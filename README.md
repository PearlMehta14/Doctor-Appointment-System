# 🏥 MedCare | Premium Doctor Appointment System

MedCare is a modern, full-stack healthcare portal designed to streamline medical appointments between doctors and patients. Built with a focus on high-end aesthetics (Glassmorphism) and real-time user feedback.

## 📝 Description
**MedCare** is an advanced Doctor Appointment Management System designed to bridge the gap between healthcare providers and patients through a seamless digital experience. 

The application addresses common pain points in medical scheduling by providing:
*   **Dynamic Resource Allocation**: Real-time availability tracking that instantly releases slots upon cancellation.
*   **Proactive Patient Engagement**: Integrated notification system to ensure patients never miss their scheduled consultations.
*   **Operational Efficiency for Doctors**: A simplified dashboard that filters out cancelled appointments, allowing practitioners to focus on active patient care.
*   **Modern Design Language**: Utilizing glassmorphism and ambient animations to reduce "medical anxiety" and provide a premium, user-friendly interface.


## ✨ Key Features

### 🩺 For Patients
*   **Modern UI/UX**: Premium glassmorphism design with smooth animations and dynamic backgrounds.
*   **Real-time Scheduling**: View available time slots for any date and book in seconds.
*   **Smart Validation**: Prevents booking on Sundays (holidays) or selecting past dates/times.
*   **Live Notifications**: Automated alerts on the dashboard 15 minutes prior to appointments.
*   **Appointment Management**: Track booking history and cancel appointments with instant slot recovery.
*   **Health & Wellness**: Integrated wellness tips for a better patient experience.

### 👨‍⚕️ For Doctors
*   **Centralized Dashboard**: View all daily 'Confirmed' appointments in a clean, professional grid.
*   **Patient Directory**: Searchable database of all registered patients by name or phone.
*   **Streamlined Workflow**: Automatic hiding of cancelled appointments to keep the focus on active care.

## 🛠️ Tech Stack
- **Backend**: Python / Flask
- **Database**: SQLite (SQLAlchemy ready)
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism Design System), JavaScript (ES6)
- **Security**: Werkzeug password hashing
- **Icons/Fonts**: Google Fonts (Outfit), CSS-based micro-interactions

## 🚀 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PearlMehta14/Doctor-Appointment-System.git
   cd "mini project"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000`

## 🔑 Test Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Doctor** | `doctor@example.com` | `password123` |
| **Patient** | `patient@example.com` | `patient123` |

## 📂 Project Structure
- `/static`: Design system, CSS tokens, and images.
- `/templates`: Premium Jinja2 HTML templates.
- `/instance`: SQLite database (auto-generated on first run).
- `app.py`: Core Flask application logic and database interactions.

---

