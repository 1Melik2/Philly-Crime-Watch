@echo off
echo Starting Philly Crime Watch Dashboard...

:: Start Flask Backend in a new window
echo Starting Flask Data API on port 5001...
start "Flask Backend" cmd /k "cd flask_backend && python app.py"

:: Start Node.js Backend in the current window
echo Starting Node.js Auth/Frontend on port 3000...
npm start

pause
