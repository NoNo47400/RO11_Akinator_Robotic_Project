# Use a standard Python 3.8 image
FROM python:3.8-slim
WORKDIR /app

# Copy and install the Python 3 requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Akinator script
COPY my_akinator.py .

# Run the script on start
CMD ["python3", "my_akinator.py"]