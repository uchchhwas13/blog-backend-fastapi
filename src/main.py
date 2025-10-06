from fastapi import FastAPI
from src.middleware import register_middleware
from .routes.blog_routes import blog_router
from .routes.auth_routes import auth_router

version = "v1"

app = FastAPI(
    title="blog-backend-fastapi",
    description="A REST API for a blog web service",
    version=version
)

register_middleware(app)

app.include_router(blog_router, prefix="/api/blogs", tags=['blogs'])
app.include_router(auth_router, prefix="/api/auth", tags=['auth'])
