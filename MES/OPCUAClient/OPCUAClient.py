import sys
from opcua import ua, Client
import time
import threading

class OPCUAClient:
    def __init__(self, host = "opc.tcp://localhost:4840/freeopcua/server/"):
        try:
            self.client = Client(host)
            self.client.connect()
            #self.machineUpdateQueue = machineUpdateQueue
            print("Connected")
        except Exception as err:
            print(err)
            sys.exit(1)

        self.MES_machine_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_machine_update")
        self.MES_warehouse_in_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_in_update")
        self.MES_warehouse_out_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_out_update")

        self.machinesStatusNodes = []
        self.machinesStatusNodes.append(self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.work"))
        self.machinesStatusNodes.append(self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.work"))
        #self.updateNodesAndVars(self)


    def updateNodesAndVars(self):
        self.MES_machine_update = self.MES_machine_updateNode.get_value()
        self.MES_warehouse_in_update = self.MES_warehouse_in_updateNode.get_value()
        self.MES_warehouse_out_update = self.MES_warehouse_out_updateNode.get_value()

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
    
    def getMachineStatus(self, cell, machine):
        return self.machinesStatusNodes[(cell + (machine) * 6)-1].get_value()
    def setWarehouseInUpdate(self, change, conveyour, piece):
        self.updateNodesAndVars()
        self.MES_warehouse_in_update[0] = change
        self.MES_warehouse_in_update[1] = conveyour
        self.MES_warehouse_in_update[2] = piece
        self.MES_warehouse_in_updateNode.set_value(self.MES_warehouse_update, ua.VariantType.Int16)
        
    def setWarehouseOutUpdate(self, change, conveyour, piece):
        self.updateNodesAndVars()
        self.MES_warehouse_out_update[0] = change
        self.MES_warehouse_out_update[1] = conveyour
        self.MES_warehouse_out_update[2] = piece
        self.MES_warehouse_out_updateNode.set_value(self.MES_warehouse_update, ua.VariantType.Int16)

    def getWarehouseInUpdate(self):
        self.updateNodesAndVars()
        return self.MES_warehouse_update
    
    def __opcManager__(self):
        while True:
            time.sleep(1)


    def run(self):
        threading.Thread(target=self.__opcManager__, daemon=True).start()
    

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

#myClient = OPCUAClient()
#myClient.run()
#input() 