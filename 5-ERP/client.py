import socket
from xml.dom import minidom

file = minidom.parse('command1.xml')
print(file.toprettyxml())
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)

print('Received from', addr)
print(minidom.parseString(data).toprettyxml())

