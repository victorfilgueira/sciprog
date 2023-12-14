from PyQt5.QtWidgets import *

class MyGrid(QDialog):
    def __init__(self):
        super(MyGrid, self).__init__()
        self.setGeometry(200,50,50,200)
        
        self.r1 = QLabel("Quantidade de pontos no eixo x:")
        self.r2 = QLabel("Quantidade de pontos no eixo y:")
        self.t1 = QLineEdit()
        self.t2 = QLineEdit()
        self.b1 = QPushButton("Confirmar")

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.r1)
        self.vbox.addWidget(self.t1)
        self.vbox.addWidget(self.r2)
        self.vbox.addWidget(self.t2)
        self.vbox.addWidget(self.b1)

        self.setLayout(self.vbox)
        self.b1.clicked.connect(self.getValues)
        self.a = 0
        self.b = 0

    def getValues(self):
        self.a = int(self.t1.text())
        self.b = int(self.t2.text())
        self.accept()