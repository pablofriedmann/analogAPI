# AnalogAPI 📸

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
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

### Upcoming Features

☐ **Compatibility Logic** (e.g., 120 film for medium format cameras): Enhance compatibility logic beyond format matching.  

---

## 📊 Tech Stack

- **Python**— Language for the backend <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
- **FastAPI** — Fast and modern web framework <img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" />
- **PostgreSQL** + **SQLAlchemy** — Database & ORM <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" />  <img src="https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white" />

- **Docker** — For containerized local setup <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
- **Swagger UI** — Auto-generated docs at `/docs` <img src="https://img.shields.io/badge/Swagger-85EA2D?style=for-the-badge&logo=Swagger&logoColor=white" />
- **Pytest** — For testing endpoints

---

## 📚 Roadmap

### Phase 1: MVP (In Progress)
- [x] CRUD for Cameras & Films
- [x] Tags
- [x] Format-based compatibility
- [x] Seed: 5 Cameras + 5 Films
- [x] Recommendations
- [x] User Auth (JWT)
- [x] Favorites
- [x] Postman collection
- [ ] Render Deployment

### Phase 2: Data Expansion & Scraping
- Manual scraping (e.g., Lomography, Film Photography Project)
- Store source info (URL, date)
- Add tech specs: shutter type, lens system, country, etc.
- Endpoints `/scrape/films` and `/scrape/cameras`

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

# 5. Run the app
uvicorn analogapi.main:app --reload
```

Access the docs at:
```
http://localhost:8000/docs
```

---

## 🌱 Seeding the Database
AnalogAPI includes a script to populate the database with initial data, which is useful for testing and demonstrations. The script inserts 5 cameras, 5 films, and 5 tags, along with their associations.

To run the seed script:
```bash
cd src
python -m analogapi.seed
```

## 🔧 Running Tests

```bash
# 1. Set the test database URL
cd /workspaces/analogAPI
export TEST_DATABASE_URL=postgresql://user:password@localhost:5432/analogapi_test

# 2. Run the tests with coverage
PYTHONPATH=$PYTHONPATH:/workspaces/analogAPI/src pytest --cov=src/analogapi tests/
```

---

## 🔺 Project Architecture

```mermaid
graph TD
  subgraph Client
    A1[Swagger UI] --> B1[API Endpoints]
  end

  subgraph Backend
    B1[FastAPI App] --> B2[Router Layer]
    B2 --> B3[Service Layer]
    B3 --> B4[SQLAlchemy Models]
  end

  B4 --> C1[(PostgreSQL DB)]
  B1 --> D1[Swagger Docs]

  subgraph DevOps
    E1[Docker] --> F1[PostgreSQL Container]
    E1 --> B1
  end
```
```

---


> Made with love for film, chemistry, and clean code.


