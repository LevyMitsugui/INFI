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

        self.MES_machine_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_machine_update")
        self.MES_warehouse_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_update")
        #self.updateNodesAndVars(self)


    def updateNodesAndVars(self):
        self.MES_machine_update = self.MES_machine_updateNode.get_value()
        self.MES_warehouse_update = self.MES_warehouse_updateNode.get_value()

    def setMachineUpdate(self, change, machine, tool, time):
        self.updateNodesAndVars()
        self.MES_machine_update[0] = change
        self.MES_machine_update[1] = machine
        self.MES_machine_update[2] = tool
        self.MES_machine_update[3] = time
        self.MES_machine_updateNode.set_value(self.MES_machine_update, ua.VariantType.Int16)

    def getMachineUpdate(self):
        self.updateNodesAndVars()
        return self.MES_machine_update

    def setWarehouseUpdate(self, change, piece, cell):
        self.updateNodesAndVars()
        self.MES_warehouse_update[0] = change
        self.MES_warehouse_update[1] = piece
        self.MES_warehouse_update[2] = cell
        self.MES_warehouse_updateNode.set_value(self.MES_warehouse_update, ua.VariantType.Int16)

    def getWarehouseUpdate(self):
        self.updateNodesAndVars()
        return self.MES_warehouse_update

# i = 0
# while True:
#     try:
        
#         myClient = OPCUAClient()
#         i += 1
#         myClient.setMachineUpdate(1, 1, i, 10)
#         print(myClient.getMachineUpdate())
#         myClient.setMachineUpdate(2, 1, i+1, 20)
#         print(myClient.getMachineUpdate())
#         myClient.setMachineUpdate(1, 2, i+2, 30)
#         print(myClient.getMachineUpdate())
#         myClient.setMachineUpdate(2, 2, i+3, 40)
#         print(myClient.getMachineUpdate())
#         myClient.setWarehouseUpdate(1, 1, i+10)
#         print(myClient.getWarehouseUpdate())
#         myClient.setWarehouseUpdate(2, 2, i+20)
#         print(myClient.getWarehouseUpdate())
#         time.sleep(1)
#     except KeyboardInterrupt:
#         print("Bye")
#         break

myClient = OPCUAClient()
myClient.run()
input() """