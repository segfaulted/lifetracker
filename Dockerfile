# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Run the FastAPI backend
FROM python:3.12-slim
WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy backend requirements files
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Sync/install backend dependencies
WORKDIR /app/backend
RUN uv pip install --system -r pyproject.toml

# Copy backend application code
COPY backend/app ./app

# Copy the frontend built assets
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PORT=8000

# Run uvicorn on startup
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
