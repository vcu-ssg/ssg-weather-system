# Use a lightweight Python image
FROM python:3.13-slim

# Set the working directory
WORKDIR /app

# Copy the Python script and requirements
COPY wunderground.py /app/exporter.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port for Prometheus to scrape
EXPOSE 9123

# Command to run the Python script
CMD ["python", "exporter.py"]
