CineBook – Setup & Usage Guide

This project consists of a backend (Django) and a frontend (Vite / React) application. Follow the steps below to run the project locally.

Prerequisites

Make sure you have the following installed:

Python 3.9+

Node.js 18+

npm

pip

Virtual environment (recommended)

Backend Setup

Navigate to the backend directory:

cd backend


Install Python dependencies:

pip install -r requirements.txt


Run the Django development server:

python manage.py runserver


The backend will start at:

http://127.0.0.1:8000/

Frontend Setup

Navigate to the frontend directory:

cd frontend/bmshow_frontend


Install frontend dependencies:

npm install


Start the development server:

npm run dev


The frontend will start at:

http://localhost:5173/

Login Credentials

Use the following test credentials to sign in:

Email:    test@example.com
Password: testpass123

Application Features

Once logged in, you can:

Browse movies and shows

Select available seats

Book movie tickets

Notes

Ensure both backend and frontend servers are running simultaneously.

If you face dependency issues, try using a fresh virtual environment or deleting node_modules and reinstalling.