# Fraud Apps Kainat Amna

Fraud_apps_Kainat-Amna is an application for analysing app reviews and potentially fraudulent apps.

![Django](https://img.shields.io/badge/Django-2563EB?style=flat-square) ![SQLite](https://img.shields.io/badge/SQLite-0F172A?style=flat-square)

## Overview

The data model covers `user_register`, `Application`, `Review`, `SystemFeedback`.

## Implemented workflows

The source defines these handlers:

- **Register** — `register`
- **Login** — `login_view`
- **Logout** — `logout_view`
- **Home** — `home`
- **Get Sentiment Score** — `get_sentiment_score`
- **App Details** — `app_details`
- **Update Profile** — `update_profile`
- **Submit Feedback** — `submit_feedback`
- **Feedback List** — `feedback_list`

## Getting started

### 1. Get the project

```bash
git clone https://github.com/nasirabbas827/Fraud_apps_Kainat-Amna.git
cd Fraud_apps_Kainat-Amna
```

### 2. Prepare Python

Create an isolated environment:

```bash
python -m venv .venv
```

Activate it with `.venv\Scripts\activate` on Windows Command Prompt, or `source .venv/bin/activate` on macOS/Linux.

No requirements file is included. The inspected Python imports indicate these dependencies as a starting point:

```bash
python -m pip install Django nltk Pillow
```

Dependency versions are not pinned in this repository.

### 3. Configure and run

Review [`fakeapps/settings.py`](fakeapps/settings.py) for database, media, and any email configuration. Use a local copy of the supplied database when available.

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/. If you need a Django administration account, run `python manage.py createsuperuser`. Application-specific user roles may be managed separately.

## Repository guide

| Path | Purpose |
| --- | --- |
| [`db.sqlite3`](db.sqlite3) | Included SQLite database |
| [`manage.py`](manage.py) | Django command-line entry point |
| [`myapp`](myapp) | Django application modules |
| [`templates`](templates) | HTML page templates |

## Development notes

These setup instructions are based on the repository source. The application has not been executed as part of this documentation update; verify dependencies and configuration in your local environment.
