# Philly Crime Watch Dashboard

A real-time crime monitoring dashboard for Philadelphia, featuring interactive maps, statistics, forecasting, and an automated notification system.

## Project Architecture

This project uses a dual-backend architecture:
- **Node.js (Port 3000)**: Handles user authentication (Signup/Login), sessions, and serves the frontend HTML.
- **Flask (Port 5001)**: Handles crime data analysis, mapping APIs, and real-time notifications.

---

## Prerequisites

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **MongoDB Atlas** account (or local MongoDB instance)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://gitlab.cci.drexel.edu/cid/2526/fw1023/e4/crime_dashboard.git
cd crime_dashboard
```

### 2. Configure Environment Variables
You need to set up two `.env` files using the provided examples.

**Root Directory (Node.js)**:
- Copy `.env.example` to `.env`.
- Update `MONGODB_URI` with your connection string.
- Set a `SESSION_SECRET` for security.

**flask_backend Directory (Python)**:
- Navigate to `flask_backend/`.
- Copy `.env.example` to `.env`.
- Enter your **NotificationAPI** credentials and **MongoDB** details.

### 3. Install Dependencies

**Node.js**:
```bash
npm install
```

**Python**:
```bash
cd flask_backend
pip install -r requirements.txt
cd ..
```

---

## Running the Dashboard

### Windows (One-Click Launch)
Simply double-click the `run_all.bat` file in the root directory. It will open two terminal windows: one for the Flask API and one for the Node.js server.

### Manual Launch
If you prefer to run them separately:

1. **Start Flask**:
   ```bash
   cd flask_backend
   python app.py
   ```

2. **Start Node.js**:
   ```bash
   # In a new terminal from the root
   node server.js
   ```

Access the application at: **[http://localhost:3000](http://localhost:3000)**

---

## Features
- **Interactive Heatmap**: Visualize crime density across Philadelphia.
- **Crime Forecasting**: Predictive analytics for future crime trends.
- **Automated Alerts**: Email and SMS notifications for nearby incidents.
- **User Dashboard**: Save locations and manage notification preferences.

## Data Sources
Crime data is provided by the [OpenDataPhilly](https://opendataphilly.org/) API.
