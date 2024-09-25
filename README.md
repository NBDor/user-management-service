# User Management Service

## Overview
The User Management Service is a FastAPI-based microservice designed to handle user-related operations such as authentication, authorization, and user data management. It provides a robust and scalable solution for managing users, their roles, and groups within a larger system architecture.

## Features
- User registration and authentication
- Role-based access control
- User group management
- Secure password hashing
- JWT token-based authentication

## Technologies
- Python 3.11.3
- FastAPI 0.115.0
- SQLAlchemy
- Pydantic 2.9.2
- PyJWT

## Setup
1. Ensure you have Python 3.11.3 installed. If using pyenv:
   ```
   pyenv install 3.11.3
   pyenv local 3.11.3
   ```

2. Clone the repository:
   ```
   git clone https://github.com/your-username/user-management-service.git
   cd user-management-service
   ```

3. Create and activate a virtual environment:
   ```
   python -m venv user-management-env
   source user-management-env/bin/activate  # On Windows, use `user-management-env\Scripts\activate`
   ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables (create a `.env` file in the project root):
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   SECRET_KEY=your_secret_key_here
   ```

## Running the Service
To run the service locally:
```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the interactive API documentation at `http://localhost:8000/docs`.

## API Endpoints
- `/users`: User management operations
- `/auth`: Authentication endpoints
- `/roles`: Role management
- `/groups`: Group management

For detailed API documentation, refer to the Swagger UI available at `/docs` when the service is running.

## Development
We use several tools to maintain code quality:

- Black for code formatting
- Flake8 for linting
- Mypy for static type checking
- Pytest for testing

To run all checks, use the `lint.sh` script:
```
./lint.sh
```

Run this script before committing changes to ensure code quality.

## Testing
To run the test suite:
```
pytest
```

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.