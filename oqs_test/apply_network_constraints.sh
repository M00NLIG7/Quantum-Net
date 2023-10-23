#!/bin/bash

# Apply network constraints to the lo interface
tc qdisc add dev lo root netem delay 100ms loss 10% rate 1mbit

# Run the passed command
exec "$@"
