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

        self.machineStatusNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.machine_status")
        self.toolSelectNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.tool_select")
        self.toolTimeNode = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.tool_time")
        self.WH1Node = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.WH1_piece_count")
        self.WH2Node = self.client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.WH2_piece_count")
        
        #self.updateNodesAndVars(self)


    def updateNodesAndVars(self):
        
        self.machineStatus = self.machineStatusNode.get_value()
        self.toolSelect = self.toolSelectNode.get_value()
        self.toolTime = self.toolTimeNode.get_value()
        self.WH1 = self.WH1Node.get_value()
        self.WH2 = self.WH2Node.get_value()

    def setMachineToolAndTime(self, machine, cell, tool, time):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars()

        self.toolSelect[cell-1] = tool
        self.toolTime[cell-1] = time

        self.toolSelectNode.set_value(self.toolSelect, ua.VariantType.Int16)
        self.toolTimeNode.set_value(self.toolTime, ua.VariantType.Int16)

    def getMachineTool(self, machine, cell):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars()

        return self.toolSelect[cell-1]

    def getMachineStatus(self, machine, cell):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars()

        return self.machineStatus[cell-1]
    

    def setMachineStatus(self, machine, cell, status):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars()

        self.machineStatus[cell-1] = status

        self.machineStatusNode.set_value(self.machineStatus, ua.VariantType.Int16)

    def getWH1PieceCount(self, piece):
        self.updateNodesAndVars()

        return self.WH1[piece-1]

    def getWH2PieceCount(self, piece):
        self.updateNodesAndVars()

        return self.WH2[piece-1]
    
    def spawn(self, pieceType, quantity, gate): #TODO implement this
        #set a "quantity" of "pieceType" on "gate"
        pass

    def getGateStatus(self, gate): #TODO implement this
        #returns the status of the gate
        pass

    def __cellRefToMachine__(self, machine, cell):
        """
        Converts the given cell reference to the corresponding machine INDEX reference.

        Parameters:
            machine (int): The machine number (1 or 2).
            cell (int): The cell number (1 to 6).

        Returns:
            int: The converted machine INDEX (0-11).
        """
        
        """ ret = -1
        if cell < 4:
            ret = cell + (machine-1)*3
        elif cell>=4:
            ret = cell + 3 + (machine-1)*3
        return ret-1 """

        ret = -1
        ret = (cell+6*(machine-1))-1

        return ret
    
    
    """ 
i = 0
while True:
    try:
        
        myClient = OPCUAClient()
        i += 1
        myClient.setMachineToolAndTime(1, 1, i, 10)
        myClient.setMachineToolAndTime(2, 1, i+1, 20)
        myClient.setMachineToolAndTime(1, 2, i+2, 30)
        myClient.setMachineToolAndTime(2, 2, i+3, 40)
        myClient.setMachineStatus(1, 1, 1)
        myClient.setMachineStatus(2, 1, 0)
        myClient.setMachineStatus(1, 2, 1)
        myClient.setMachineStatus(2, 2, 0)
        print(myClient.getMachineTool(1, 1))
        print(myClient.getMachineTool(2, 1))
        print(myClient.getMachineTool(1, 2))
        print(myClient.getMachineTool(2, 2))
        print(myClient.getMachineStatus(1, 1))
        print(myClient.getMachineStatus(2, 1))
        print(myClient.getMachineStatus(1, 2))
        print(myClient.getMachineStatus(2, 2))
        print(myClient.getWH1PieceCount(1))
        print(myClient.getWH1PieceCount(2))
        print(myClient.getWH2PieceCount(1))
        print(myClient.getWH2PieceCount(2))
        time.sleep(1)
    except KeyboardInterrupt:
        print("Bye")
        break

myClient = OPCUAClient()
myClient.run()
input() """