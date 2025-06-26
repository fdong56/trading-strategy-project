FROM python:3.10.14

# Set the working directory inside the container
WORKDIR /app

# Copy all backend files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (optional, for clarity)
EXPOSE 80

# Start the FastAPI app using Uvicorn
ENTRYPOINT ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=80"]
