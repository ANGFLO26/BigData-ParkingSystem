FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy producer code
COPY camera_producer.py .

# Run producer
CMD ["python", "camera_producer.py"]

