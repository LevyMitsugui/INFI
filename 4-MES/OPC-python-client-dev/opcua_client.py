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
    setCM = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.setCM")
    setPieceIO = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.setPieceIO")
    
    ##num_node = client.get_node(ua.NodeId(1002, 2))


while True:
    print(setCM.get_value())
    print(setPieceIO.get_value())
    print("connected")
    time.sleep(2)
