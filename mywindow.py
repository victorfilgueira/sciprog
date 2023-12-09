from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *
import tkinter as tk
from tkinter import simpledialog

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100,100,600,400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        # create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)

        # create a Toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("icons/fit.jpg"),"fit",self)
        tb.addAction(fit)
        dd = QAction(QIcon("icons/dd.png"),"dd",self)
        tb.addAction(dd)
        tb.actionTriggered[QAction].connect(self.tbpressed)
        
    def get_distance(self):
        root = tk.Tk()
        root.withdraw()
        distancia = simpledialog.askstring("Input", "Insira o valor da distância padrão:", parent=root)
        if distancia is not None:
            print("Distância inserida:", distancia)

        root.destroy()

    def tbpressed(self,a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "dd":
            self.get_distance()