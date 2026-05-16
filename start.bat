@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
cd backend
pip install -r requirements.txt

echo Starting Django server...
python manage.py runserver