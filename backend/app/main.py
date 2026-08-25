"""Main FastAPI application module for Raksha."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.app.api.v1 import api_v1_router
from backend.app.core.config import settings


# Application rate limiter (30 requests per minute per IP per security.md)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for backend startup and shutdown."""
    # Model loading and resource initialization hook
    yield
    # Cleanup hook


app = FastAPI(
    title="Raksha Regional Phishing Detection API",
    description="AI-powered regional-language phishing detection system.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# Attach state limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers adhering to ErrorResponse schema in api-specification.md
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Format Pydantic request validation errors consistently."""
    error_messages = []
    for err in exc.errors():
        msg = err.get("msg", "Invalid input.")
        # Clean standard ValueErrors
        if msg.startswith("Value error, "):
            msg = msg.replace("Value error, ", "")
        error_messages.append(msg)
    message = "; ".join(error_messages) or "Invalid request payload."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error_type": "validation_error", "message": message},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Format HTTP exceptions into standard error structure."""
    error_type = (
        "validation_error"
        if exc.status_code in (status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY)
        else "http_error"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_type": error_type, "message": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected server errors without leaking stack traces."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_type": "internal_error",
            "message": "An internal server error occurred.",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "raksha-backend"}


# Mount API Routers
app.include_router(api_v1_router)
