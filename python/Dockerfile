# Use the official Python 2.7 image based on Debian Buster
FROM python:2.7-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Define the command to run your application
CMD ["python", "./main.py"]