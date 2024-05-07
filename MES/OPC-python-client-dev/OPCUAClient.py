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
        testVarNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.test_var")
        testVecNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.test_vec")


        while True:
            testVar = testVarNode.get_value()
            testVec = testVecNode.get_value()

            print(testVar)
            print(testVec)

            testVar += 1
            testVec[0] += 1

            testVarNode.set_value(testVar, ua.VariantType.Int16)
            testVecNode.set_value(testVec, ua.VariantType.Int16)
            
            print("connected")
            time.sleep(2)
    
    def run(self):
        threading.Thread(target=self.__opcuaClient, daemon=True).start()

    def setMachineTool(self, machine, tool):


myClient = OPCUAClient()
myClient.run()
input()