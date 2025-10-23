from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from src.middleware import register_logging_middleware
from src.error_handlers import register_exception_handlers
from .routes.blog_routes import blog_router
from .routes.auth_routes import auth_router

version = "v1"

app = FastAPI(
    title="blog-backend-fastapi",
    description="A REST API for a blog web service",
    version=version
)

# Register middleware and exception handlers
register_logging_middleware(app)
register_exception_handlers(app)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": version
    }

app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(blog_router, prefix="/blogs", tags=['blogs'])
app.include_router(auth_router, prefix="/user", tags=['auth'])
