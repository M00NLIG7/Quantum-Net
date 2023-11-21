#!/bin/bash

# Define the log file path
log_file="/opt/quantum_net/script.log"

# Function to log a message
log_message() {
    echo "$(date): $1" | tee -a "$log_file"
}

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null
then
    log_message "docker-compose could not be found, please install it first."
    exit 1
fi

# Check if tcpdump is installed
if ! command -v tcpdump &> /dev/null
then
    log_message "tcpdump could not be found, please install it first."
    exit 1
fi

# Check if tc is installed
if ! command -v tc &> /dev/null
then
    log_message "tc (traffic control) could not be found, please install it first."
    exit 1
fi

# Define the secure directory for storing logs
secure_directory="/opt/quantum_net"
mkdir -p "$secure_directory"

# Run Docker Compose
log_message "Starting Docker Compose..."
sudo docker-compose up -d >> "$log_file" 2>&1

# Wait a moment for Docker Compose to fully initialize
sleep 5

# Define the Docker Compose network name
docker_compose_network="oqs_test_kyber_quantum_net"

# Get the full network ID
full_network_id=$(docker network inspect "$docker_compose_network" --format '{{.Id}}')

if [ -z "$full_network_id" ]; then
    log_message "No network ID found for Docker network: $docker_compose_network"
    exit 1
fi

# Shorten the network ID to get the network adapter name (usually the first 12 characters)
network_adapter="br-${full_network_id:0:12}"

# List all veth interfaces
veth_interfaces=$(ip link show type veth | grep -o 'veth[^:@]*')

# Function to set packet loss on a veth interface
set_packet_loss_on_veth() {
    local interface=$1
    local loss_percent=$2
    log_message "Setting $loss_percent% packet loss on interface $interface..."
    sudo tc qdisc add dev $interface root netem loss $loss_percent% >> "$log_file" 2>&1
}

# Function to clear packet loss on a veth interface
clear_packet_loss_on_veth() {
    local interface=$1
    log_message "Clearing packet loss settings on interface $interface..."
    sudo tc qdisc del dev $interface root >> "$log_file" 2>&1
}

# Initialize packet loss percentage
packet_loss=100

# Loop to increment packet loss every 2 hours, and continue testing at 100%
while true; do
    # Apply packet loss to all veth interfaces
    for interface in $veth_interfaces; do
        set_packet_loss_on_veth $interface $packet_loss
    done

    # Start tcpdump on the Docker network bridge
    log_message "Starting tcpdump on Docker network adapter $network_adapter with packet loss $packet_loss%..."
    sudo tcpdump -i $network_adapter -w "$secure_directory/dump_$packet_loss.pcap" >> "$log_file" 2>&1 &
    tcpdump_pid=$!

    # Wait for 2 hours
    sleep 2h

    # Stop tcpdump
    sudo kill $tcpdump_pid

    # Copy and rename server and client logs
    cp ./build/server_logs.txt "$secure_directory/server_logs_$packet_loss.txt"
    echo "" > ./build/server_logs.txt
    cp ./build/client_logs.txt "$secure_directory/client_logs_$packet_loss.txt"
    echo "" > ./build/client_logs.txt

    # Clear existing packet loss settings
    for interface in $veth_interfaces; do
        clear_packet_loss_on_veth $interface
    done

    # Increment packet loss
    if [ $packet_loss -lt 100 ]; then
        packet_loss=$((packet_loss + 5))
    fi

    # Maintain packet loss at 100% once reached
    if [ $packet_loss -gt 100 ]; then
        packet_loss=100
        log_message "Packet loss maintained at 100%."
    fi
done

