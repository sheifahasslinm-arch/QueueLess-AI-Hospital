# QueueLess AI Hospital

A full-stack AI-assisted hospital queue management system designed to help reduce patient waiting time and improve queue management.

## 📌 Project Overview

QueueLess AI Hospital is a web-based hospital queue management system with separate workflows for patients and hospital staff.

Patients can register, select a service and doctor, receive a queue token, and monitor their queue status and estimated waiting time.

Hospital staff can manage active queues, call the next patient, complete queue entries, and monitor the current queue.

The system uses AI-assisted waiting-time estimation while the actual queue order is controlled by live queue data.

## 🚀 Features

### Patient
- Patient registration and login
- Service and doctor selection
- Queue token generation
- Patient dashboard
- Live queue-status monitoring
- Current token and people-ahead information
- Estimated waiting time

### Staff / Admin
- Staff login
- Queue monitoring
- Call next patient
- Complete queue entries
- Manage active queues
- Monitor patient queue status

### AI-Assisted Estimation
- Estimates patient waiting time using queue-related data
- Uses people ahead and service-time information
- AI assists with estimation only
- Actual queue order is controlled by live queue data

## 🛠️ Technology Stack

### Frontend
- React
- TypeScript
- Vite
- HTML
- CSS

### Backend
- Python
- Flask
- REST APIs

### Database
- MySQL
- phpMyAdmin
- XAMPP

### Machine Learning
- Python
- Machine learning model for waiting-time estimation
- Synthetic queue training data

### Tools
- VS Code
- Git
- GitHub

## 🔄 System Architecture

```text
React + TypeScript Frontend
          ↓
     Flask Backend
          ↓
       MySQL
          ↓
     Flask Backend
          ↓
React + TypeScript Frontend
The machine-learning component assists the backend with estimated waiting-time prediction.

📂 Project Structure
QueueLess-AI-Hospital/
│
├── backend/
│   ├── app.py
│   ├── model_features.pkl
│   ├── queue_model.pkl
│   └── requirements.txt
│
├── database/
│   └── schema_public.sql
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
└── ml/
    ├── queue_data.csv
    ├── train_model.py
    ├── queue_model.pkl
    ├── model_features.pkl
    └── README.md
▶️ Running the Project

This project was developed and tested locally.

Frontend
npm install
npm run dev
Backend

Install the required Python packages:

pip install -r requirements.txt

Then run the Flask application:

python app.py

The frontend and backend communicate through REST APIs.

🗄️ Database

The project uses MySQL for storing:

Users
Doctors
Services
Queue tokens

The public database schema is available in:

database/schema_public.sql
🤖 AI Component

The AI component is used to assist with estimating patient waiting time.

It does not decide the actual queue order.

The actual queue is managed using live queue data from the hospital system.

🎓 Academic Project

This project was developed as a full-stack academic project to explore practical applications of web development, databases, REST APIs, and AI-assisted prediction.

👩‍💻 Developer

Sheifa Hasslin

B.Sc. Artificial Intelligence & Machine Learning Student

Interested in:

Full-Stack Development
Python
AI/ML
Generative AI
Practical AI Applications
