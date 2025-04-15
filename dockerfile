# Dockerfile

# Official Python base image
FROM python:alpine

# Set the working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8080

# Command to run the app with Gunicorn
CMD ["gunicorn", "-b", ":8080", "run:app"]