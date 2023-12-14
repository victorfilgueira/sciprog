from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from forceselection import ForceSelection
from mycanvas import *
from mygrid import MyGrid
from temperatureselection import TemperatureSelection
from mymodel import *
import json

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100,100,600,400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        self.tempSelector = TemperatureSelection()
        self.forceSelector = ForceSelection()
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        self.grid = MyGrid()

        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/fit.jpg"),"fit",self)
        tb.addAction(fit)
        grid = QAction(QIcon("icons/grid.png"), "grid", self)
        tb.addAction(grid)
        temp = QAction(QIcon("icons/temp.png"), "temp", self)
        tb.addAction(temp)
        force = QAction(QIcon("icons/force.png"), "force", self)
        tb.addAction(force)
        data = QAction(QIcon("icons/export.png"), "data", self)
        tb.addAction(data)
        tb.actionTriggered[QAction].connect(self.tbpressed)

    def tbpressed(self,a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "grid":
            self.grid.exec_()
            self.canvas.setGrid(self.grid.a, self.grid.b)
        if a.text() == "temp":
            self.tempSelector.exec_()
            self.canvas.setTemp(self.tempSelector.temp)
        if a.text() == "force":
            self.forceSelector.exec_()
            self.canvas.setForce(self.forceSelector.force)
        if a.text() == "data":
            self.generateData()

    def generateData(self):
        pointsDict = dict()
        count = 1
        canvasP = self.canvas.pointsIn
        coords = []
        conexoes = []
        contorno = []
        forcas = []
        pointsForce = self.canvas.pointForce
        
        print("Pontos: ", end="")
        for i in range(len(canvasP) -1 , -1, -1):
            for j in range(0, len(canvasP[i])):
                if(type(canvasP[i][j]) == list):
                    print(canvasP[i][j], end="")
                    coords.append(canvasP[i][j])
                    pointsDict[(canvasP[i][j][0],canvasP[i][j][1])] = count
                    count += 1
        for i in range(len(canvasP) -1 , -1, -1):
            for j in range(0, len(canvasP[i])):
                aux = []
                if(type(canvasP[i][j]) == list):
                    if(j + 1 < len(canvasP[i])):
                        if(canvasP[i][j+1] != 0):
                            aux.append(pointsDict[(canvasP[i][j+1][0],canvasP[i][j+1][1])])
                        else:
                            aux.append(0)
                    else:
                        aux.append(0)
                    if (j - 1 > 0):
                        if(canvasP[i][j - 1] != 0):
                            aux.append(pointsDict[(canvasP[i][j-1][0], canvasP[i][j-1][1])])
                        else:
                            aux.append(0)
                    else:
                        aux.append(0)
                    if (i + 1 < len(canvasP[i])):
                        if(canvasP[i+1][j] != 0):
                            aux.append(pointsDict[(canvasP[i+1][j][0], canvasP[i+1][j][1])])
                        else:
                            aux.append(0)
                    else:
                        aux.append(0)
                    if (i - 1 > 0):
                        if(canvasP[i-1][j] != 0):
                            aux.append(pointsDict[(canvasP[i-1][j][0], canvasP[i-1][j][1])])
                        else:
                            aux.append(0)
                    else:
                        aux.append(0)
                    if(aux != []):
                        conexoes.append(aux)
        
        print("\Conexões: ", conexoes)

        for i in pointsDict.values():
            p = list(pointsDict.keys())[list(pointsDict.values()).index(i)]
            if(p in self.canvas.pointTemp.keys()):
                contorno.append([1, self.canvas.pointTemp[p]])
            else:
                contorno.append([0,0])

        print("Contornos: ", contorno)
        
        for i in pointsDict.values():
            f = list(pointsDict.keys())[list(pointsDict.values()).index(i)]
            if(f in self.canvas.pointForce.keys()):
                forcas.append([1, self.canvas.pointForce[f]])
            else:
                forcas.append([0,0])
        
        print("Forças: ", forcas)

        with open('points.json', 'w', encoding='utf-8') as f:
            json.dump({"coords": coords, "connect": conexoes, "contour": contorno, "forces": forcas}, f, ensure_ascii=False, indent=4)

    def createJson(self):
        conexoes = self.canvas.conexoes
        pointslist = []
        c = 1
        for p in conexoes:
            pointslist.append({"ponto_numero": c, "x": int(p.getX()), "y": p.getY()})
            c += 1
        with open('points.json', 'w', encoding='utf-8') as f:
            json.dump({"Pontos": pointslist}, f, ensure_ascii=False, indent=4)