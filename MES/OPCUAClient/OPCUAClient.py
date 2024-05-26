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

            self.prevTransferCellStatus = False
            print("Opcua Connected")
        except Exception as err:
            print(err)
            sys.exit(1)

        self.MES_machine_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_machine_update")
        self.MES_warehouse_in_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_in_update")
        self.MES_warehouse_out_updateNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_warehouse_out_update")
        self.MES_spawner_pieceNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.MES_piece_spawn_update")

        self.machinesStatusNodes = []
        self.machinesStatusNodes.insert(0,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.insert(1,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.insert(2,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.insert(3,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.insert(4,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.insert(5,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M1.available"))
        self.machinesStatusNodes.insert(6,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        self.machinesStatusNodes.insert(7,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        self.machinesStatusNodes.insert(8,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        self.machinesStatusNodes.insert(9,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        self.machinesStatusNodes.insert(10,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        self.machinesStatusNodes.insert(11,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.M7.available"))
        
        self.spawnStatusNodes = []
        self.spawnStatusNodes.insert(0,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Input_line_New.LC1.done"))
        self.spawnStatusNodes.insert(1,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Input_line_New.LC2.done"))
        self.spawnStatusNodes.insert(2,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Input_line_New.LC3.done"))
        self.spawnStatusNodes.insert(3,self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Input_line_New.LC4.done"))

        self.Tranfer_cell = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Processing_line_New.Win_going_up.transfer_done")

        #self.updateNodesAndVars(self)

    def kill(self):
        self.client.disconnect()

    def updateNodesAndVars(self):
        self.MES_machine_update = self.MES_machine_updateNode.get_value()
        self.MES_warehouse_in_update = self.MES_warehouse_in_updateNode.get_value()
        self.MES_warehouse_out_update = self.MES_warehouse_out_updateNode.get_value()
        self.MES_spawn_piece = self.MES_spawner_pieceNode.get_value() 

    def setMachineUpdate(self, change, machine, tool, time, secondTime = 0):
        self.updateNodesAndVars()
        self.MES_machine_update[0] = change
        self.MES_machine_update[1] = machine
        self.MES_machine_update[2] = tool
        self.MES_machine_update[3] = time
        self.MES_machine_update[4] = secondTime
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

    def getSpawnStatus(self, gate):
        return self.spawnStatusNodes[gate].get_value()
    
    def getAllSpawnStattus(self):
        valid = []
        for gt in self.spawnStatusNodes:
            valid.append(gt.get_value())

        return all(valid)
    
    def getTransferCellStatusEdge(self):
        curr = self.Tranfer_cell.get_value()
        if self.prevTransferCellStatus == False and curr == True:
            self.prevTransferCellStatus = curr
            return 'Rise'
        elif self.prevTransferCellStatus == True and curr == False:
            self.prevTransferCellStatus = curr
            return 'Fall'
        else:
            self.prevTransferCellStatus = curr
            return 'None'
    
    def opcManager(self):
        try:
            threading.Thread(target=self.__opcManager__, daemon=True).start()
        except:
            print('[OPC Client] Could not start opcManager thread')

    def __opcManager__(self):
        while True:
            time.sleep(0.01)
            self.updateNodesAndVars()
            #update machines and warehouses
            if self.inWHQueue.qsize() > 0 and self.getWarehouseInUpdate()[0] == 0:
                update = self.inWHQueue.get()
                print('[OPC Client] updating warehouse in. Values: ', update)
                self.setWarehouseInUpdate(1, update['conveyour'], update['piece'])

            if self.outWHQueue.qsize() > 0 and self.getWarehouseOutUpdate()[0] == 0:
                update = self.outWHQueue.get()
                print('[OPC Client] updating warehouse out. Values: ', update)
                self.setWarehouseOutUpdate(1, update['conveyour'], update['piece'])

            if self.machineUpdateQueue.qsize() > 0 and self.getMachineUpdate()[0] == 0:
                update = self.machineUpdateQueue.get()
                print('[OPC Client] updating machine. Values: ', update)
                self.setMachineUpdate(1, update['machine'], update['tool'],  update['time'], update['secondTime'])

            if self.gateUpdateQueue.qsize() > 0 and self.getPieceSpawn()[0] == 0:
                update = self.gateUpdateQueue.get()
                print('[OPC Client] updating gate. Values: ', update)
                self.setPieceSpawn(1, update['gate'], update['piece'], update['quantity'])
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