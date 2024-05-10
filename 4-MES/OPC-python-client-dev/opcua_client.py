import sys
from opcua import ua, Client
import time



try: 
    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    client.connect()
    print("Connected")
except Exception as err:
    print(err)
    sys.exit(1)

if __name__ == "__main__":
    test_var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.test_var")
    
    ##num_node = client.get_node(ua.NodeId(1002, 2))


while True:
    print(test_var.get_value())
    test_var.set_value(test_var.get_value()+1, ua.VariantType.Int16)
    print("connected")
    time.sleep(2)
