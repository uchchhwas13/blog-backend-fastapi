# Blog Backend - FastAPI

A REST API for a blog web service built with FastAPI.

## Project Overview

A full-featured backend REST API for a blogging platform that enables users to create, manage, and interact with blog posts. Built with FastAPI and PostgreSQL, this project demonstrates modern backend development practices including authentication, authorization, database migrations, file handling, and comprehensive error management.

### Key Features

- **User Management**: User registration, login, and profile management with JWT-based authentication and refresh token mechanism
- **Blog Post Management**: Create, read, update, and delete blog posts with cover images and full-text content
- **Comments System**: Add and manage comments on blog posts with user attribution
- **Like System**: Track and manage blog post likes with duplicate prevention
- **Image Upload**: File upload support for user profile pictures and blog cover images
- **Pagination**: Efficient data retrieval with pagination support for blog posts and comments
- **Authentication & Authorization**: Secure JWT-based authentication with role-based access control
- **Error Handling**: Comprehensive error handling and custom exception management
- **Database Migrations**: Automatic schema versioning using Alembic
- **Logging & Monitoring**: Request logging middleware and health check endpoints
- **API Documentation**: Auto-generated Swagger UI documentation

### Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT tokens
- **File Storage**: Local file system
- **Migrations**: Alembic
- **Server**: Uvicorn

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/blogdb
JWT_ACCESS_TOKEN_SECRET_KEY=your-access-token-secret
JWT_REFRESH_TOKEN_SECRET_KEY=your-refresh-token-secret
JWT_ALGORITHM=HS256
SERVER_HOST=http://localhost
SERVER_PORT=3000
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=blog_db
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start the Server

```bash
python run.py
```

The server will start on `http://localhost:3000` (or your configured port).

## Running the Server

### Option 1: Using run.py (Recommended)

```bash
python run.py
```

This automatically uses your `.env` configuration for host, port, and base URL.

### Option 2: Using uvicorn directly

```bash
uvicorn src.main:app --reload --port 3000
```

## Option 3: Using Docker

**Start the application (builds and runs in the background):**

```bash
docker compose up --build -d
```

**Stop the application:**

```bash
docker compose down
```

**View logs:**

```bash
docker compose logs -f
```

The application will be available at `http://localhost:3000` and PostgreSQL will be accessible at `localhost:5432`.

## Configuration

All configuration is managed through environment variables in `.env`:

| Variable                       | Description                      | Default                       |
| ------------------------------ | -------------------------------- | ----------------------------- |
| `SERVER_HOST`                  | Server host address              | `localhost`                   |
| `SERVER_PORT`                  | Server port                      | `3000`                        |
| `BASE_URL`                     | Public base URL (for production) | Auto-generated from host:port |
| `DATABASE_URL`                 | PostgreSQL connection string     | Required                      |
| `JWT_ACCESS_TOKEN_SECRET_KEY`  | Access token secret              | Required                      |
| `JWT_REFRESH_TOKEN_SECRET_KEY` | Refresh token secret             | Required                      |
| `JWT_ALGORITHM`                | JWT algorithm                    | `HS256`                       |

### Production Deployment

For production, set the `BASE_URL` environment variable to your public domain:

```env
BASE_URL=https://api.yourdomain.com
SERVER_PORT=8000
```

This ensures that file URLs (images, uploads) are generated with your production domain.

## Project Structure

```
blog-backend-fastapi/
├── src/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── utils.py             # Utility functions
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API routes
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
├── migrations/              # Alembic migrations
├── images/                  # Default images
├── uploads/                 # User uploaded files
├── run.py                   # Server startup script
└── requirements.txt         # Python dependencies
```

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`

## API Endpoints

### Authentication

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### Blog Management

- `POST /blogs` - Create a new blog post
- `GET /blogs` - Get all blog posts (public)
- `GET /blogs/{blog_id}` - Get blog details with comments
- `PATCH /blogs/{blog_id}` - Update a blog post (author only)
- `DELETE /blogs/{blog_id}` - Delete a blog post (author only)

### Blog Interactions

- `POST /blogs/{blog_id}/comments` - Add a comment to a blog
- `PUT /blogs/{blog_id}/comments/{comment_id}` - Update a comment (author only)
- `POST /blogs/{blog_id}/likes` - Like/unlike a blog
- `GET /blogs/{blog_id}/likes` - Get blog likes count and users

### Request/Response Examples

#### Create Blog Post

```bash
POST /blogs
Content-Type: multipart/form-data

{
  "title": "My Blog Post",
  "body": "This is the content of my blog post...",
  "coverImage": [file]
}
```

#### Update Blog Post

```bash
PATCH /blogs/{blog_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "body": "Updated content...",
  "coverImageUrl": "new-image.jpg"
}
```

#### Delete Blog Post

```bash
DELETE /blogs/{blog_id}
Authorization: Bearer <access_token>
```

#### Add Comment

```bash
POST /blogs/{blog_id}/comments
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "content": "Great blog post!"
}
```

#### Like/Unlike Blog

```bash
POST /blogs/{blog_id}/likes
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "isLiked": true
}
```

## Features

### Blog Management

- ✅ **Create Blog Posts** - Upload cover images and create rich blog content
- ✅ **Update Blog Posts** - Partial updates (title, body, cover image)
- ✅ **Delete Blog Posts** - Secure deletion with cascade cleanup
- ✅ **View Blog Lists** - Public access to all blog posts
- ✅ **Blog Details** - Full blog content with comments and likes

### User Interactions

- ✅ **Comments System** - Users can comment on blog posts
- ✅ **Like System** - Users can like/unlike blog posts
- ✅ **User Authentication** - JWT-based authentication
- ✅ **Authorization** - Role-based access control

### Security Features

- 🔒 **Authentication Required** - Protected endpoints require valid JWT tokens
- 🔒 **Authorization Checks** - Users can only modify their own content
- 🔒 **Input Validation** - Comprehensive request validation
- 🔒 **Error Handling** - Secure error responses without sensitive data exposure
- 🔒 **CASCADE DELETE** - Automatic cleanup of related data when blogs are deleted

### Data Management

- 📊 **Database Migrations** - Alembic-based schema management
- 📊 **File Uploads** - Secure image upload handling
- 📊 **Relationship Management** - Proper foreign key constraints
- 📊 **Transaction Safety** - ACID-compliant database operations

## Development

The server runs with auto-reload enabled by default, so changes to your code will automatically restart the server.

### Adding New Features

1. **Models**: Add new SQLModel classes in `src/models/`
2. **Schemas**: Define Pydantic schemas in `src/schemas/`
3. **Services**: Implement business logic in `src/services/`
4. **Routes**: Create API endpoints in `src/routes/`
5. **Migrations**: Generate and run database migrations with `make migrate`

### Database Migrations

```bash
# Generate new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head
```
