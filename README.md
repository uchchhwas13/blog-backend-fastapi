# Blog Backend - FastAPI

A REST API for a blog web service built with FastAPI.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
# OR
make install
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/blogdb
JWT_ACCESS_TOKEN_SECRET_KEY=your-access-token-secret
JWT_REFRESH_TOKEN_SECRET_KEY=your-refresh-token-secret
JWT_ALGORITHM=HS256
SERVER_HOST=localhost
SERVER_PORT=3000
```

### 3. Run Migrations

```bash
alembic upgrade head
# OR
make upgrade
```

### 4. Start the Server

```bash
python run.py
# OR
make run
```

The server will start on `http://localhost:3000` (or your configured port).

## Running the Server

### Option 1: Using run.py (Recommended)

```bash
python run.py
```

This automatically uses your `.env` configuration for host, port, and base URL.

### Option 2: Using Make

```bash
make run
```

### Option 3: Using uvicorn directly

```bash
uvicorn src.main:app --reload --port 3000
```

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

## Available Make Commands

```bash
make help      # Show available commands
make run       # Run the development server
make dev       # Alias for run
make install   # Install dependencies
make migrate   # Generate new migration (use msg="description")
make upgrade   # Apply pending migrations
```

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
make migrate msg="Add new feature"

# Apply migrations
make upgrade
```
