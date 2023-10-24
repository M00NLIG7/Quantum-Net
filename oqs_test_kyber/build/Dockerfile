FROM ubuntu:latest

# Install dependencies
RUN apt-get -y update && \
    apt-get install -y build-essential git cmake libssl-dev python3 python3-venv python3-pip iperf3 tcpdump iputils-ping iproute2 libcap2-bin

# Get liboqs
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs

# Install liboqs
RUN cmake -S liboqs -B liboqs/build -DBUILD_SHARED_LIBS=ON && \
    cmake --build liboqs/build --parallel 4 && \
    cmake --build liboqs/build --target install

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

# Enable a normal user
RUN useradd -m -c "Open Quantum Safe" oqs && \
    groupadd pcap && \
    usermod -aG pcap oqs && \
    usermod -aG sudo oqs && \
    chgrp pcap /usr/bin/tcpdump && \
    chmod 750 /usr/bin/tcpdump && \
    setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump

USER oqs
WORKDIR /home/oqs

# Create a Python virtual environment and activate it
RUN python3 -m venv venv
RUN echo "source venv/bin/activate" >> ~/.bashrc
RUN /bin/bash -c "source venv/bin/activate && python3 -m ensurepip --upgrade"

# Clone the liboqs-python repository and install it in the virtual environment
RUN git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python
RUN /bin/bash -c "source venv/bin/activate && cd liboqs-python && pip install . && pip install pycryptodome"

COPY server.py /home/oqs/
COPY client.py /home/oqs/

CMD ["/bin/bash"]
