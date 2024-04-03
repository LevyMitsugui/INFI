import sys
from opcua import Client
import time

client = Client("opc.tcp://localhost:4840/freeopcua/server/")
client.connect()

try: 
    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    client.connect()
    print("Connected")
except Exception as err:
    print(err)
    sys.exit(1)

if __name__ == "__main__":
    set_M1_T1 = client.get_node("")
    set_M1_T2 = client.get_node("")
    set_Input_Piece = client.get_node("")
    
    num_node = client.get_node(ua.NodeId(1002, 2))


while True:
    print("connected")
    time.sleep(1)