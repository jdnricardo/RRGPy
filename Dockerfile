# Use a slim Python image
FROM python:3.13.3-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# (Optional) If you want to use pyproject.toml instead, uncomment:
# COPY pyproject.toml .
# RUN pip install --no-cache-dir .

# Copy the rest of your app code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Healthcheck (optional)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Remove build tools after install
RUN apt-get purge -y build-essential && apt-get autoremove -y

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
