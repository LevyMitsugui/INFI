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

        #PRECISA TESTAR, SE ISSO DEVE FICAR AQUI OU NO updateNodesAndVars!!!
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

        self.updateNodesAndVars(self)

        self.toolSelect[cell-1] = tool
        self.toolTime[cell-1] = time

        self.toolSelectNode.setvalue(self.toolSelect, ua.VariantType.Int16)
        self.toolTimeNode.setvalue(self.toolTime, ua.VariantType.Int16)

    def getMachineTool(self, machine, cell):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars(self)

        return self.toolSelect[cell-1]

    def getMachineStatus(self, machine, cell):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars(self)

        return self.machineStatus[cell-1]
    

    def setMachineStatus(self, machine, cell, status):
        if machine == 2:
            cell += 6

        self.updateNodesAndVars(self)

        self.machineStatus[cell-1] = status

        self.machineStatusNode.setvalue(self.machineStatus, ua.VariantType.Int16)

    def getWH1PieceCount(self, piece):
        self.updateNodesAndVars(self)

        return self.WH1[piece-1]

    def getWH2PieceCount(self, piece):
        self.updateNodesAndVars(self)

        return self.WH2[piece-1]


myClient = OPCUAClient()
myClient.run()
input()