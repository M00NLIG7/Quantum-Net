import subprocess

def start_iperf_server():
    subprocess.Popen(["iperf3", "-s", "-p", "5202"])

if __name__ == "__main__":
    start_iperf_server()
