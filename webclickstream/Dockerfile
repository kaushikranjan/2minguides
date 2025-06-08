# Set the base image to Apache Spark with Python 3
# This provides a pre-configured environment for running Spark applications
from apache/spark:3.5.3-python3

# Switch to root user to perform system-level operations
# This is necessary for installing packages and setting permissions
USER root

# Set the working directory for the application
# All subsequent commands will be executed in this directory
WORKDIR /opt/application

# Copy requirements.txt into the container
# This file lists all Python dependencies needed for the application
COPY requirements.txt .

# Install Python dependencies from requirements.txt
# This ensures all required packages are available in the container
RUN pip install -r requirements.txt

# Copy source code and runners into the container
# These contain the application logic and execution scripts
COPY src/ src/
COPY runners/ .

# Set full permissions on the application directory
# This ensures the application can read/write files as needed
RUN chmod -R 777 /opt/application