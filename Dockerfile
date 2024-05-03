# Use a base image and avoid installation of important drivers by hand
FROM python:3.10

# Copy the files and folder required for setting up environment.
COPY requirements.txt .
COPY app/ app/

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies and remove requirements.txt, to avoid unnecessary files
RUN pip install --no-cache-dir -r requirements.txt && rm -rf requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run command
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]