# client.py
import socket

def receive_image(conn):
    # First, receive the length of the image data
    length_data = conn.recv(4)
    if not length_data:
        return None
    length = int.from_bytes(length_data, 'big')
    
    # Then, receive the actual image data
    image_data = b''
    while len(image_data) < length:
        packet = conn.recv(4096)
        if not packet:
            break
        image_data += packet
    return image_data

def save_image(image_data, filename):
    with open(filename, 'wb') as f:
        f.write(image_data)

def send_command_and_get_image(conn, command):
    conn.sendall(command.encode('utf-8'))
    return receive_image(conn)

if __name__ == "__main__":
    remote_host = '172.29.196.47'  # Replace with the remote device's IP address
    remote_port = 65432            # Must match the port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((remote_host, remote_port))
        while True:
            command = input("Enter command (GENERATE_IMAGE to generate image, EXIT to close): ")
            if command in ('GENERATE_IMAGE', 'EXIT'):
                if command == 'GENERATE_IMAGE':
                    image_data = send_command_and_get_image(s, command)
                    if image_data:
                        save_image(image_data, 'received_image.png')
                        print("Image received and saved as 'received_image.png'")
                    else:
                        print("Failed to receive image")
                elif command == 'EXIT':
                    s.sendall(command.encode('utf-8'))
                    break
            else:
                print("Invalid command")
