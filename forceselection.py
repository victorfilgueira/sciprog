from PyQt5.QtWidgets import *


class ForceSelection(QDialog):
    def __init__(self):
        super(ForceSelection, self).__init__()
        self.setGeometry(200, 50, 50, 200)

        self.r1 = QLabel("Digite a força para os pontos selecionados: ")
        self.t1 = QLineEdit()
        self.b1 = QPushButton("Confirmar")

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.r1)
        self.vbox.addWidget(self.t1)
        self.vbox.addWidget(self.b1)

        self.setLayout(self.vbox)
        self.b1.clicked.connect(self.getValues)
        self.force = 0

    def getValues(self):
        self.force = int(self.t1.text())
        self.accept()