# JWT Mini-API

## Description

A small Flask API that demonstrates JWT (JSON Web Token) authentication.
A user logs in with a username and password, receives a token, and then uses
that token to access protected endpoints. One endpoint is available only to
users with the `admin` role.

## Technologies

- Python 3
- Flask
- PyJWT
- python-dotenv

## Installation

1. Create and activate a virtual environment.

   macOS / Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   Windows PowerShell:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project folder with the secret key:

   ```
   JWT_SECRET=super_secret_key_123
   ```

   The `.env` file is listed in `.gitignore` and is not stored in Git.

## Running

```bash
python app.py
```

The server starts at `http://127.0.0.1:5001`.

## Users

| username | password   | role    |
|----------|------------|---------|
| student  | student123 | student |
| admin    | admin123   | admin   |

## Example: /login

Request:

```bash
curl -X POST http://127.0.0.1:5001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

Response (HTTP 200):

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
}
```

The token is signed with HS256, expires after 5 minutes and contains:
`sub` (username), `role`, `iat` (issued at) and `exp` (expires at).

## Example: using the JWT

Send the token in the `Authorization` header:

```bash
curl http://127.0.0.1:5001/profiil \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Response (HTTP 200):

```json
{
  "role": "student",
  "username": "student"
}
```

## Endpoints

| Method | Path      | Access        | Responses                                                                  |
|--------|-----------|---------------|----------------------------------------------------------------------------|
| POST   | /login    | public        | 200 + token for valid credentials, 401 for wrong username or password      |
| GET    | /profiil  | valid JWT     | 200 + user info, 401 if the token is missing, invalid, changed or expired  |
| GET    | /admin    | JWT, admin    | 200 for admin, 403 for student, 401 if the token is missing or invalid     |

## Testing

The API was tested manually with `curl`. All 7 tests passed.

| #  | Test                              | Endpoint        | Expected | Actual | Result |
|----|-----------------------------------|-----------------|----------|--------|--------|
| 1  | Successful login                  | POST /login     | 200      | 200    | Pass   |
| 2  | Wrong password                    | POST /login     | 401      | 401    | Pass   |
| 3  | Profile with valid token          | GET /profiil    | 200      | 200    | Pass   |
| 4  | Profile without token             | GET /profiil    | 401      | 401    | Pass   |
| 5  | Tampered token                    | GET /profiil    | 401      | 401    | Pass   |
| 6  | Expired token                     | GET /profiil    | 401      | 401    | Pass   |
| 7  | Student uses admin endpoint       | GET /admin      | 403      | 403    | Pass   |

## Security notes

- The secret key is stored in `.env`, not in the source code, and `.env` is not committed to Git.
- Tokens are signed with HS256 and expire after 5 minutes.
- The server accepts only the HS256 algorithm when verifying tokens.
- A changed token fails the signature check and a token past `exp` is rejected; both return 401.
- Users and passwords are stored in plain text in the code. This is acceptable for a learning project only. A real application would use a database and hashed passwords.
- The server runs in debug mode and over plain HTTP. A real application must use HTTPS and turn debug mode off.
- Anyone can read the contents of a JWT, so never put passwords or other secrets inside it.
