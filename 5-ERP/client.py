import socket
import time
from xml.dom import minidom

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server



""" file = minidom.parse('II_comands_2023-2024_v1/command1.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)

print('Received from', addr)
print(minidom.parseString(data).toprettyxml()) """

""" input()

file = minidom.parse('II_comands_2023-2024_v1/command2a.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)

print('Received from', addr)
print(minidom.parseString(data).toprettyxml())

input()

file = minidom.parse('II_comands_2023-2024_v1/command2b.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)

print('Received from', addr)
print(minidom.parseString(data).toprettyxml())

input()

file = minidom.parse('II_comands_2023-2024_v1/command3.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)

print('Received from', addr)
print(minidom.parseString(data).toprettyxml())

input() """

""" file = minidom.parse('II_comands_2023-2024_v1/command4.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)
 
print('Received from', addr)
print(minidom.parseString(data).toprettyxml()) """


""" file = minidom.parse('II_comands_2023-2024_v1/command6.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)
 
print('Received from', addr)
print(minidom.parseString(data).toprettyxml()) """

file = minidom.parse('II_comands_2023-2024_v1/command7.xml')
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(file.toprettyxml().encode(), (HOST, PORT))
    data, addr = s.recvfrom(1024)
 
print('Received from', addr)
print(minidom.parseString(data).toprettyxml())
