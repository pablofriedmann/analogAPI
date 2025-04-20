# AnalogAPI 📸

![License](https://img.shields.io/badge/license-MIT-black)

**AnalogAPI** is a RESTful API lovingly crafted for analog photography lovers. Built as a backend portfolio project, it lets you explore and manage a collection of analog cameras and films, much like organizing your gear in a darkroom notebook. With full CRUD, tagging, relationships, and scraping in the roadmap, it's ready to grow.

<p align="center">
  <img src="AnalogAPI.svg" alt="AnalogAPI Logo" width="200" />
</p>

---

## 🌍 Overview

AnalogAPI lets you interact with a database of analog gear—from your favorite SLRs to expired ISO 400 film rolls. It's designed to be scalable, clean, and ready for integration with any frontend (like React) or other developers' tools.

### Core Features

- ✅ **CRUD for Cameras** - `/cameras`: Add, edit, browse, and remove analog cameras.
- ✅ **CRUD for Films** - `/films`: Manage your favorite film stocks.
- ✅ **Tagging System** - `/tags`: Add, edit, browse, and remove tags; associate tags with cameras and films.
- ✅ **Format-based Compatibility** - `/cameras/{id}/compatible-films` and `/films/{id}/compatible-cameras`: Find films compatible with a camera or cameras compatible with a film based on format.
- ✅ **Preferences Enhancement**: Added predefined options for `favorite_photography_type` (e.g., `portrait`, `street`, `nature`, etc.), `preferred_format`, `color_preference`, `preferred_camera_type`, `preferred_focal_length`, and `favourite_look`, allowing multiple photography types. Fixed database schema issues to ensure proper functionality.
- ✅ **User Auth (JWT)**: Register, login, and secure endpoints with JWT authentication (`/users/register`, `/users/login`, `/users/me`, `/users/preferences`).
- ✅ **Favorites** - `/favorites`: Allow users to mark cameras and films as favorites, remove them, and list their favorites (`/favorites/cameras`, `/favorites/films`).
- ✅ **Render Deployment**: Deployed the API to Render! 

---

## 📊 Tech Stack

- **Python** — Language for the backend <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
- **FastAPI** — Fast and modern web framework <img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" />
- **PostgreSQL** + **SQLAlchemy** — Database & ORM <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
- **Docker** — For containerized local setup <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
- **Swagger UI** — Auto-generated docs at `/docs` <img src="https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=Swagger&logoColor=white" />
- **Uvicorn** — ASGI server for running the API <img src="https://img.shields.io/badge/Uvicorn-29313A?style=for-the-badge&logo=uvicorn&logoColor=white" />
- **JWT** — For user authentication (via python-jose) <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON-Web-Tokens&logoColor=white" />
- **Render** — Deployment platform for production <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" />
- **Postman** — For testing API endpoints <img src="https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=Postman&logoColor=white" />
- **requests + BeautifulSoup** — For web scraping (Phase 2) <img src="https://img.shields.io/badge/Requests-000000?style=for-the-badge&logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/BeautifulSoup-000000?style=for-the-badge&logo=python&logoColor=white" />

**Note:** All dependencies are listed in `requirements.txt`. Install them using `pip install -r requirements.txt`.

---

## 📚 Roadmap

### ✅Phase 1: 🎉MVP COMPLETED!🎉
- [x] CRUD for Cameras & Films
- [x] Tags
- [x] Format-based compatibility
- [x] Seed: 5 Cameras + 5 Films
- [x] Recommendations
- [x] User Auth (JWT)
- [x] Favorites
- [x] Postman collection
- [x] Render Deployment

### ✅ Phase 2: Data Expansion & Scraping — COMPLETED!
- [x] Manual scraping for cameras (e.g., Camera-wiki.org) — **COMPLETED!** Scraping includes `brand`, `model`, `format`, `type`, `years`, `lens_mount`, and `scraped_at`.
- [x] Manual scraping for films (e.g., Wikipedia) — **COMPLETED!** Scraping includes `brand`, `name`, `iso`, `format`, `color`, `grain`, and `scraped_at`.
- [x] Store source info (URL, date) — **COMPLETED!** Added `source_url` and `scraped_at` fields to both `Camera` and `Film` models.
- [x] Add tech specs: shutter type, lens system, country, etc. — **Partially Completed:** Currently extracting `lens_mount` for cameras; more specs can be added in the future.
- [x] Endpoints `/scrape/films` and `/scrape/cameras` — **COMPLETED!** Both endpoints are functional, scraping data from Camera-wiki.org and Wikipedia respectively.

### Phase 3: User Experience
- User collections
- Comments / reviews
- Kits (e.g., "Street Photography Kit, Fashin Kit, Holidays Kit")
- History log

### Phase 4: Scale & Community
- Optional microservices
- WebSocket features
- OAuth2 (optional)
- Export to JSON/CSV

---

## 📢 Contact

Questions, feedback, collaborations??
- GitHub: [@pablofriedmann](https://github.com/pablofriedmann)

---

## How to use AnalogAPI! Get Started!

### Option 1: GitHub Codespaces

```bash
# 1. Open repo in Codespaces
# 2. Activate virtual environment:
source env/bin/activate

# 3. Install dependencies:
pip install -r requirements.txt

# 4. Start PostgreSQL with Docker
docker-compose up -d

# 5. Run the app
cd src
uvicorn analogapi.main:app --reload --host 0.0.0.0 --port 8000
```

Access the docs at:
```
https://<your-codespace>.app.github.dev:8000/docs
```

### Option 2: Local Development

```bash
# 1. Clone project
git clone <REPOSITORY_URL>
cd analogapi

# 2. Set up virtual env
python -m venv env
source env/bin/activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Start PostgreSQL with Docker
docker-compose up -d

# 5. Navigate to the source directory
cd src

# 6. Run the app
uvicorn analogapi.main:app --reload
```

Access the docs at:
```
http://localhost:8000/docs
```

---

## 🌱 Seeding the Database
AnalogAPI includes a script to populate the database with initial data, which is useful for testing and demonstrations. The script inserts 5 cameras (e.g., Canon AE-1, Nikon F3), 5 films (e.g., Kodak Portra 400, Ilford HP5 Plus), and 5 tags (e.g., SLR, Color), along with their associations.

To run the seed script:
```bash
cd src
python -m analogapi.seed
```

## 🔧 Running Tests

```bash
# 1. Navigate to the project root
cd /path/to/analogapi  # Use /workspaces/analogAPI in Codespaces

# 2. Ensure the test database URL is set (or loaded from .env)
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/analogapi_test

# 3. Run the tests with coverage
PYTHONPATH=$PYTHONPATH:./src pytest --cov=src/analogapi tests/
```
Note: Make sure the test database (analogapi_test) is created in PostgreSQL before running the tests. You can create it using:
```sql
CREATE DATABASE analogapi_test;
```


---

## 📨Postman Collection

<img src="https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=Postman&logoColor=white" /> 

A Postman collection is available to test the API endpoints:

- Collection: AnalogAPI.postman_collection.json
- Environment: AnalogAPI-Dev.postman_environment.json

To use the collection:

1. Import the collection and environment into Postman.
2. Set the base_url variable in the AnalogAPI-Dev environment to your API's URL (e.g., https://<your-codespace>.app.github.dev without the :8000 port, as GitHub Codespaces may redirect external requests).
3. Use the POST Login User request to authenticate and automatically set the access_token variable.
4. Test the other endpoints, which use the access_token for authentication.

Note: If requests using {{base_url}} fail with a 404 Not Found, double-check the base_url value in the environment. I had several problems with this situation. Ensure there are no extra spaces, hidden characters, or truncated parts in the URL (Postman may truncate long URLs in the UI). Test the base_url directly in a browser to confirm it works. 

---

## 🔺 Project Architecture

```mermaid
graph TD
  subgraph Client
    A1[Swagger UI] --> B1[API Endpoints]
  end

  subgraph Backend
    B1[FastAPI App] --> B2[Router Layer]
    B2 --> B3[SQLAlchemy Models]
  end

  B3 --> C1[(PostgreSQL DB)]
  B1 --> D1[Swagger Docs]

  subgraph DevOps
    E1[Docker] --> F1[PostgreSQL Container]
    E1 --> B1
  end
```

---


> Made with love for film, chemistry, and clean code.


