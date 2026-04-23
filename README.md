# FastAPI Enterprise Task Manager API

A robust, production-ready RESTful API built with Python and FastAPI. This project implements high-performance asynchronous backend architecture, utilizing a Dockerized PostgreSQL environment, hierarchical data relationships, and strict RS256 security protocols.

## 🚀 Key Features

* **Asynchronous Architecture:** Fully non-blocking I/O operations using SQLAlchemy 2.0 (Async) and asyncpg for high-concurrency performance.
* **Dockerized Infrastructure:** Seamless deployment and environment consistency using Docker and Docker Compose.
* **Hierarchical Data:** Supports Tasks, Subtasks, and Categories with optimized relationship loading (selectinload) to prevent N+1 query issues.
* **Advanced Querying:** Pagination, fuzzy search filtering, and multi-parameter sorting implemented at the database level.
* **Ironclad Security:** RS256 asymmetric JWT signing, IDOR protection (resource ownership verification), and bcrypt password hashing.
* **Automated Table Initialization:** Intelligent database startup logic that handles table creation within the async lifecycle.

## 🛠️ Tech Stack

* **Framework:** FastAPI (Async)
* **Language:** Python 3.12
* **Database:** PostgreSQL 16 (via Docker)
* **ORM:** SQLAlchemy 2.0 (Asyncio)
* **Driver:** asyncpg
* **Authentication:** RS256 (Asymmetric Encryption), cryptography
* **Containerization:** Docker & Docker Compose

## 💻 Setup & Installation

The easiest way to run the API is using Docker Compose, which handles the application and the PostgreSQL database automatically.

### 1. Clone the repository

    git clone https://github.com/MOHOLOG/task_manager_fastapi.git
    cd fastapi-task-manager

### 2. Configure Environment

Create a `.env` file in the root directory:

    DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/task_db
    POSTGRES_USER=user
    POSTGRES_PASSWORD=pass
    POSTGRES_DB=task_db

### 3. Generate Security Certificates

The API uses asymmetric RSA keys for JWT signing. Create a `certs` folder and generate the keys:

    mkdir certs
    # Generate Private Key
    openssl genrsa -out certs/private_key.pem 4096
    # Extract Public Key
    openssl rsa -in certs/private_key.pem -pubout -out certs/public_key.pem

### 4. Run with Docker

    docker compose up --build

## 📖 API Documentation

The API is served at `http://localhost:8000`. Navigate to the following endpoints to test the system:

* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`

## 🗂️ Core Endpoints

* `POST /register` - Register a new user
* `POST /login` - Receive an RS256-signed JWT
* `GET /tasks` - Fetch paginated, sorted, and filtered tasks (including category data)
* `POST /categories` - Manage custom organizational buckets
* `PUT /tasks/{id}` - Securely update task status and details