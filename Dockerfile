FROM python:3.13-slim

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
