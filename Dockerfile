# Use Python 3.13 slim image
FROM python:3.13-slim

# Install system dependencies (if any needed for your tools)
# curl is often useful for healthchecks or downloading tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen ensures we use the exact versions in uv.lock
# --no-install-project installs only dependencies, not the project itself yet
RUN uv sync --frozen --no-install-project

# Copy the rest of the application
COPY . .

# Install the project itself
RUN uv sync --frozen

# Expose the port ADK web runs on
EXPOSE 9000

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Run the agent
# Using --host 0.0.0.0 is crucial for Docker networking
CMD ["adk", "web", "--port", "9000", "--host", "0.0.0.0"]
