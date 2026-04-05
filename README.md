# FastAPI Enterprise Task Manager API

A robust, production-ready RESTful API built with Python and FastAPI. This project goes beyond a simple CRUD application by implementing enterprise-level backend architecture, including hierarchical database relationships, advanced query optimization, and strict security protocols.

## 🚀 Key Features

* **Hierarchical Data Architecture:** Utilizes SQLAlchemy Adjacency Lists to support infinitely nested Subtasks under main Tasks.
* **Advanced Querying:** Fully implemented pagination, search filtering, and multi-parameter sorting for optimal database performance.
* **Ironclad Security (IDOR Protection):** Strict resource ownership checks ensure users can only access and modify their own data.
* **JWT Authentication:** Secure user registration and login flows using RSA-256 JSON Web Tokens and `bcrypt` password hashing.
* **Role-Based Access Control (RBAC):** Dependency-injected admin routes and user role verification.
* **Separation of Concerns:** Clean codebase architecture dividing Routers, CRUD operations, Database Models, Pydantic Schemas, and Security Utilities.

## 🛠️ Tech Stack

* **Framework:** FastAPI
* **Language:** Python 3.10+
* **Database:** SQLite (Easily swappable to PostgreSQL)
* **ORM:** SQLAlchemy 2.0
* **Data Validation:** Pydantic V2
* **Authentication:** PyJWT, Passlib (Bcrypt)

## 💻 Local Setup & Installation

Follow these steps to run the API on your local machine.

### 1. Clone the repository
```bash
git clone [https://github.com/MOHOLOG/task_manager_fastapi.git](https://github.com/MOHOLOG/task_manager_fastapi.git)
cd fastapi-task-manager
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate Security Certificates
This application uses asymmetric RSA keys for JWT signing. You must generate your own keys locally (they are strictly ignored by Git for security).
Create a `certs` folder in the root directory and generate the keys:
```bash
mkdir certs
cd certs
ssh-keygen -t rsa -b 4096 -m PEM -f jwt-private.pem
openssl rsa -in jwt-private.pem -pubout -outform PEM -out jwt-public.pem
cd ..
```

### 5. Run the Server
```bash
uvicorn main:app --reload
```

## 📖 API Documentation

Once the server is running, FastAPI automatically generates interactive API documentation. 
Navigate to your browser to explore and test all endpoints:

* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 🗂️ Core Endpoints

* `POST /register` - Register a new user
* `POST /login` - Authenticate and receive a JWT token
* `PUT /users/me` - Securely update username and password
* `GET /tasks` - Fetch paginated, sorted, and filtered tasks
* `GET /tasks/{id}/subtasks` - Fetch paginated children of a specific task
* `POST /categories` - Create custom organizational categories