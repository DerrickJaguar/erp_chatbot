# 🤖 BizBot ERP Assistant (Django + OpenAI)

A Django-based chatbot that guides customers to sign up for ERP software using conversational AI.

## Features

- 🤖 AI-powered chatbot with OpenAI integration
- 📝 Lead capture (name, company, email)
- 🔐 ERP signup and authentication
- 📊 Simple ERP dashboard
- 💾 SQLite database
- 🎨 Responsive UI with Tailwind CSS

## Setup Instructions

### 1. Clone/Extract the Project

bash
cd erp_chatbot

### 2. Create Virtual Environment

bash
python -m venv venv
venv\Scripts\activate

### 3. Install Dependencies

bash
pip install -r requirements.txt

### 4. Configure Environment Variables

bash
cp .env.example .env

# Edit .env and add your OPENAI_API_KEY (optional)

### 5. Run Migrations

bash
python manage.py makemigrations
python manage.py migrate

### 6. Create Superuser (Optional)

bash
python manage.py createsuperuser

### 7. Run Development Server

bash
python manage.py runserver

### 8. Access the Application

- Chatbot: http://127.0.0.1:8000/
- ERP Signup: http://127.0.0.1:8000/erp/signup/
- ERP Login: http://127.0.0.1:8000/erp/login/
- Admin Panel: http://127.0.0.1:8000/admin/

## Usage

### Chatbot Flow

1. User opens the chatbot interface
2. Bot asks for name
3. Bot asks for company name
4. Bot asks for email
5. Bot provides ERP signup link
6. Lead is saved to database

### AI Integration

- If `OPENAI_API_KEY` is set, the bot uses GPT for responses
- Otherwise, uses rule-based scripted responses
- AI generates contextual, friendly messages

## Project Structure

- `chatbot/` - Chatbot app with lead management
- `erp/` - ERP signup, login, and dashboard
- `erp_chatbot/` - Main project configuration

## Technologies

- Django 5.0.1
- OpenAI API (GPT-4)
- SQLite
- Tailwind CSS
- Vanilla JavaScript
