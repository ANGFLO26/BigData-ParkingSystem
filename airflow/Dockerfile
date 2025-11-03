FROM apache/airflow:2.7.0

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python packages if needed
# RUN pip install --user <package-name>

