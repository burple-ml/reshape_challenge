# Use a base image and avoid installation of important drivers by hand
FROM python:3.10

# Copy the files and folder required for setting up environment.
COPY requirements.txt .
COPY app/ app/

# Install dependencies and remove requirements.txt, to avoid unnecessary files
RUN pip install --no-cache-dir -r requirements.txt && rm -rf requirements.txt

# Set the working directory inside the container
WORKDIR /app

# Expose port 5000
EXPOSE 5000

# Run command
CMD ["uvicorn", "app:app", "--port", "5000"]
