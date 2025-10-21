# Start from Ubuntu 14.04 (Trusty) to get the old libboost packages
FROM ubuntu:14.04

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install base Python 2.7 and build tools
RUN apt-get update && apt-get install -y \
    python2.7 \
    python-pip \
    wget \
    software-properties-common

# Add the trusty repos and keys to find the old libboost packages
RUN echo "deb http://archive.ubuntu.com/ubuntu trusty main universe" > /etc/apt/sources.list.d/trusty.list
RUN echo "deb http://archive.ubuntu.com/ubuntu trusty-updates main universe" >> /etc/apt/sources.list.d/trusty.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 40976EAF437D05B5
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
RUN apt-get update

# Install the specific libboost dependencies
RUN apt-get install -y \
    libboost-regex1.55.0 \
    libboost-python1.55.0 \
    libboost-system1.55.0 \
    libboost-thread1.55.0 \
    libboost-chrono1.55.0

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install pyzmq

# --- Install Naoqi SDK ---
WORKDIR /app

# Copy the SDK you downloaded in Step 1
COPY Naoqi/pynaoqi-python2.7-2.1.4.13-linux64.tar.gz .
RUN tar xzf pynaoqi-python2.7-2.1.4.13-linux64.tar.gz

# Set the PYTHONPATH to include the Naoqi library
ENV PYTHONPATH="/app/pynaoqi-python2.7-2.1.4.13-linux64:$PYTHONPATH"

# Copy your Naoqi script
COPY Naoqi/my_naoqi.py .

# Run the script on start
CMD ["python2.7", "my_naoqi.py"]