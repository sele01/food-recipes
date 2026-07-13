# Food Recipes — Project Commands

This file contains all the commands you need to manage, test, and deploy the Food Recipes project.

---

## 🔧 Setup & Environment

| Task | Command |
|------|---------|
| Create virtual environment | `python -m venv venv` |
| Activate (Fish shell) | `source venv/bin/activate.fish` |
| Install dependencies | `pip install -r requirements.txt` |
| Update dependencies | `pip freeze > requirements.txt` |

---

## 🗄️ Database

| Task | Command |
|------|---------|
| Run migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Backup recipes (fixture) | `python manage.py dumpdata recipes > fixtures/recipes_fixture.json` |
| Restore recipes (fixture) | `python manage.py loaddata fixtures/recipes_fixture.json` |
| Reset database (dev only) | `rm db.sqlite3 && python manage.py migrate` |

---

## 🧪 Testing

| Task | Command |
|------|---------|
| Run all tests (app by app) | `python manage.py test apps.accounts apps.recipes apps.notifications apps.core` |
| Run tests for one app | `python manage.py test apps.recipes` |
| Run a specific test file | `python manage.py test apps.recipes.tests.test_models` |
| Run tests with verbose output | `python manage.py test -v 2` |

---

## 🌐 Local Server

| Task | Command |
|------|---------|
| Start development server | `python manage.py runserver` |
| Run with different port | `python manage.py runserver 8080` |

---

## ☁️ Deployment (Vercel)

| Task | Command |
|------|---------|
| Build project | `vercel build` |
| Deploy to production | `vercel --prod` |
| Deploy to preview | `vercel` |
| Add environment variable | `vercel env add` |
| List environment variables | `vercel env ls` |

---

## 🧹 Maintenance

| Task | Command |
|------|---------|
| Collect static files | `python manage.py collectstatic --noinput` |
| Check for issues | `python manage.py check` |
| Open Django shell | `python manage.py shell` |
| Show all URLs | `python manage.py show_urls` |

---

## 📦 Data Management

| Task | Command |
|------|---------|
| Export all data | `python manage.py dumpdata > full_backup.json` |
| Import all data | `python manage.py loaddata full_backup.json` |
| Export specific app | `python manage.py dumpdata recipes > recipes_backup.json` |

---

## 🧠 Notes

- Always activate the virtual environment before running any command.
- Use `python manage.py` — never `django-admin` unless you know why.
- For Fish shell users, replace `source venv/bin/activate` with `source venv/bin/activate.fish`.

---

> 📌 Add new commands here as the project grows.