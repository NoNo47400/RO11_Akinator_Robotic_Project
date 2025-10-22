FROM ubuntu:18.04

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y --no-install-recommends tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update -o Acquire::Check-Valid-Until=false && \
    apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    python2.7 \
    libpython2.7 \
    python-pip \
    # Boost libraries for Ubuntu 18.04
    libboost-python1.65.1 \
    libboost-system1.65.1 \
    libboost-thread1.65.1 \
    libboost-chrono1.65.1 \
    libboost-regex1.65.1 \
    # Other potential Naoqi dependencies
    libssl1.1 \
    libavahi-client3 \
    libavahi-common3 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pyzmq using pip
RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN pip install pyzmq --trusted-host pypi.org --trusted-host files.pythonhosted.org

WORKDIR /app

COPY Naoqi/pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327.tar.gz .
RUN tar xzf pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327.tar.gz

# Create a variable for the long directory name
ENV SDK_DIR=pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327

# Set the PYTHONPATH to the correct sub-directory
ENV PYTHONPATH="/app/${SDK_DIR}/lib/python2.7/site-packages:${PYTHONPATH}"

# Set the LD_LIBRARY_PATH for the C++ shared libraries (.so files)
ENV LD_LIBRARY_PATH="/app/${SDK_DIR}/lib:${LD_LIBRARY_PATH}"

COPY Naoqi/my_naoqi_no_mic_version.py .

CMD ["python2.7", "my_naoqi_no_mic_version.py"]