# Dockerfile for Super RoastBot with resource constraints
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ["super roast bot/requirements.txt", "./"]
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ["super roast bot/", "./"]

# Create .env file placeholder (should be mounted or set via environment variables)
# Note: Users should provide their own GROQ_KEY via environment variables

# Expose Streamlit port
EXPOSE 8501

# Set resource limits via environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application with resource constraints
# Note: Memory and CPU limits should be set when running the container
# Example: docker run --memory="512m" --cpus="1.0" <image>
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
