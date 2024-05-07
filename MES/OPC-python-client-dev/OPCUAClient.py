import sys
from opcua import ua, Client
import time
import threading

class OPCUAClient:
    def __init__(self, host = "opc.tcp://localhost:4840/freeopcua/server/"):
        try:
            self.client = Client(host)
            self.client.connect()
            print("Connected")
        except Exception as err:
            print(err)
            sys.exit(1)
    
    def __opcuaClient(self):
        test_var = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.test_var")
        
        while True:
            print(test_var.get_value())
            test_var.set_value(test_var.get_value()+1, ua.VariantType.Int16)
            print("connected")
            time.sleep(2)
    
    def run(self):
        threading.Thread(target=self.__opcuaClient, daemon=True).start()

myClient = OPCUAClient()
myClient.run()
