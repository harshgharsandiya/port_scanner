import sys
import socket
import threading
from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

scan_results = []
stop_scan_event = threading.Event()

def scan_port(target, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        if stop_scan_event.is_set():
            return
        result = s.connect_ex((target, port))
        if result == 0:
            scan_results.append(f"Port {port} is open")

def scan_ports(target, start_port, end_port):
    threads = []
    for port in range(start_port, end_port + 1):
        if stop_scan_event.is_set():
            break
        thread = threading.Thread(target=scan_port, args=(target, port))
        threads.append(thread)
        thread.start()
        
    for thread in threads:
        thread.join()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    global scan_results, stop_scan_event
    scan_results = []
    stop_scan_event.clear()
    
    target = request.form.get('hostname')
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        return jsonify({"error": "Hostname could not be resolved!"})
    
    try:
        start_port = int(request.form.get('start_port'))
        end_port = int(request.form.get('end_port'))
    except ValueError:
        return jsonify({"error": "Invalid port range"})
    
    threading.Thread(target=scan_ports, args=(target_ip, start_port, end_port)).start()
    return jsonify({"message": f"Scanning {target_ip} from port {start_port} to {end_port}..."})

@app.route('/stop', methods=['POST'])
def stop_scan():
    stop_scan_event.set()
    return jsonify({"message": "Scan has been stopped."})

@app.route('/results')
def results():
    return jsonify(scan_results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')