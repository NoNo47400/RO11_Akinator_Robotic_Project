FROM python:3.12-slim
WORKDIR /app

# Copy and install the Python 3 requirements
RUN pip install pyzmq akipy

COPY my_akinator.py .

CMD ["python3", "my_akinator.py"]