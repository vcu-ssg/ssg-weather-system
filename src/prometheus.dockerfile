# Use the official Prometheus base image
FROM prom/prometheus:latest

# Set the working directory inside the container
WORKDIR /etc/prometheus

# Copy the configuration file into the container
COPY prometheus.yml /etc/prometheus/prometheus.yml
