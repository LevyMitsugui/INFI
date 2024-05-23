import sys
from opcua import ua, Client
import time
import threading

class OPCUAClient:
    def __init__(self, inWHQueue, outWHQueue, machineUpdateQueue, gateUpdateQueue, host = "opc.tcp://localhost:4840/freeopcua/server/"):
        try:
            self.client = Client(host)
            self.client.connect()

            self.inWHQueue = inWHQueue
            self.outWHQueue = outWHQueue
            self.machineUpdateQueue = machineUpdateQueue
            self.gateUpdateQueue = gateUpdateQueue
            print("Opcua Connected")
        except Exception as err:
            print(err)
            sys.exit(1)

        self.MES_machine_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_machine_update")
        self.MES_warehouse_in_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_in_update")
        self.MES_warehouse_out_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_out_update")
        self.MES_spawner_pieceNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_piece_spawn_update")

        self.machinesStatusNodes = []
        self.machinesStatusNodes.append(self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.append(self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        #self.updateNodesAndVars(self)

    def kill(self):
        self.client.disconnect()

    def updateNodesAndVars(self):
        self.MES_machine_update = self.MES_machine_updateNode.get_value()
        self.MES_warehouse_in_update = self.MES_warehouse_in_updateNode.get_value()
        self.MES_warehouse_out_update = self.MES_warehouse_out_updateNode.get_value()
        self.MES_spawn_piece = self.MES_spawner_pieceNode.get_value()

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
        print('setWarehouseInUpdate')
        self.updateNodesAndVars()
        self.MES_warehouse_in_update[0] = change
        self.MES_warehouse_in_update[1] = conveyour
        self.MES_warehouse_in_update[2] = piece
        self.MES_warehouse_in_updateNode.set_value(self.MES_warehouse_in_update, ua.VariantType.Int16)
        print(self.MES_warehouse_in_update)

    def getWarehouseInUpdate(self):
        self.updateNodesAndVars()
        return self.MES_warehouse_in_update

    def setWarehouseOutUpdate(self, change, conveyour, piece):
        self.updateNodesAndVars()
        self.MES_warehouse_out_update[0] = change
        self.MES_warehouse_out_update[1] = conveyour
        self.MES_warehouse_out_update[2] = piece
        self.MES_warehouse_out_updateNode.set_value(self.MES_warehouse_out_update, ua.VariantType.Int16)

    def getWarehouseOutUpdate(self):
        self.updateNodesAndVars()
        return self.MES_warehouse_out_update

    def setPieceSpawn(self, change, conveyour, pieceType, quantity):
        self.updateNodesAndVars()
        self.MES_spawn_piece[0] = change
        self.MES_spawn_piece[1] = conveyour
        self.MES_spawn_piece[2] = pieceType
        self.MES_spawn_piece[3] = quantity
        self.MES_spawner_pieceNode.set_value(self.MES_spawn_piece, ua.VariantType.Int16)

    def getPieceSpawn(self):
        self.updateNodesAndVars()
        return self.MES_spawn_piece
    
    def setPieceSpawn(self, change, conveyour, pieceType, quantity):
        self.updateNodesAndVars()
        self.MES_spawn_piece[0] = change
        self.MES_spawn_piece[1] = conveyour
        self.MES_spawn_piece[2] = pieceType
        self.MES_spawn_piece[3] = quantity
        self.MES_spawner_pieceNode.set_value(self.MES_spawn_piece, ua.VariantType.Int16)

    def opcManager(self):
        try:
            threading.Thread(target=self.__opcManager__, daemon=True).start()
        except:
            print('[OPC Client] Could not start opcManager thread')

    def __opcManager__(self):
        while True:
            time.sleep(0.5)
            self.updateNodesAndVars()
            #update machines and warehouses
            if self.inWHQueue.qsize() > 0 and self.getWarehouseInUpdate()[0] == 0:
                print('[OPC Client] updating warehouse in')
                update = self.inWHQueue.get()
                self.setWarehouseInUpdate(1, update['conveyour'], update['piece'])

            if self.outWHQueue.qsize() > 0 and self.getWarehouseOutUpdate()[0] == 0:
                print('[OPC Client] updating warehouse out')
                update = self.outWHQueue.get()
                self.setWarehouseOutUpdate(1, update['conveyour'], update['piece'])

            if self.machineUpdateQueue.qsize() > 0 and self.getMachineUpdate()[0] == 0:
                print('[OPC Client] updating machine')
                update = self.machineUpdateQueue.get()
                self.setMachineUpdate(1, update['machine'], update['tool'], update['time'])

            if self.gateUpdateQueue.qsize() > 0 and self.getGateUpdate()[0] == 0:
                print('[OPC Client] updating gate')
                update = self.gateUpdateQueue.get()
                self.setGateUpdate(1, update['gate'], update['piece'])
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