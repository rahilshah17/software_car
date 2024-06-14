# server.py
import socket
import subprocess
import os
import io

def run_image_script():
    # Run the script that generates the image
    script_path = 'gen_img.py'  # Adjust this to your script's path
    subprocess.run(['python3', script_path], check=True)
    
    # Read the generated image file
    image_path = 'image.png'  # Adjust this to your image's path
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    return image_data

def start_server(host='172.29.196.47', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Listening on {host}:{port}")
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode('utf-8')
                if command == 'GENERATE_IMAGE':
                    image_data = run_image_script()
                    # Send the length of the image data first
                    conn.sendall(len(image_data).to_bytes(4, 'big'))
                    # Send the actual image data
                    conn.sendall(image_data)
                elif command == 'EXIT':
                    break
        print("Connection closed")

if __name__ == "__main__":
    start_server()

