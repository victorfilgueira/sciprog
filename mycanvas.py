from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import *
from OpenGL.GL import *
from PyQt5 import QtCore
from hetool.he.hecontroller import HeController
from hetool.he.hemodel import HeModel
from hetool.geometry.segments.line import Line
from hetool.geometry.point import Point
from hetool.compgeom.tesselation import Tesselation

class MyCanvas(QtOpenGL.QGLWidget):
    
    def __init__(self):
        super(MyCanvas, self).__init__()
        self.m_model = None
        self.m_w = 0 # width: GL canvas horizontal size
        self.m_h = 0 # height: GL canvas vertical size
        self.m_L = -1000.0
        self.m_R = 1000.0
        self.m_B = -1000.0
        self.m_T = 1000.0
        self.list = None
        self.m_buttonPressed = False
        self.m_buttonPressedF = False
        self.m_pt0 = QtCore.QPoint(0, 0)
        self.m_pt1 = QtCore.QPoint(0, 0)
        self.m_hmodel = HeModel()
        self.m_controller = HeController(self.m_hmodel)
        self.tol = 0.1
        self.m_ptf0 = QtCore.QPointF(0.0,0.0)
        self.m_ptf1 = QtCore.QPointF(0.0,0.0)
        self.pointsIn = []
        self.pointTemp = dict()
        self.pointForce = dict()
        self.points = []
        self.selections = []
        
    def initializeGL(self):
        #glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glEnable(GL_LINE_SMOOTH)
        self.list = glGenLists(1)
        
    def resizeGL(self, _width, _height):
        self.m_w = _width
        self.m_h = _height
        if(self.m_model==None)or(self.m_model.isEmpty()): self.scaleWorldWindow(1.0)
        else:
            self.m_L,self.m_R,self.m_B,self.m_T = self.m_model.getBoundBox()
            self.scaleWorldWindow(1.1)
        glViewport(0, 0, self.m_w, self.m_h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L,self.m_R,self.m_B,self.m_T,-1.0,1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        # if(self.m_model==None)or(self.m_model.isEmpty()): return
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)

        # desenho dos pontos coletados
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)

        if not ((self.m_model == None) and (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            glColor3f(0.0, 1.0, 0.0)  # green
            # glBegin(GL_TRIANGLES)
            # for vtx in verts:
            #     glVertex2f(vtx.getX(), vtx.getY())
            # glEnd()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0)  # blue
            glBegin(GL_LINES)
            for curv in curves:
                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()

        glColor3f(2.0, 2.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()

        if not (self.m_hmodel.isEmpty()):

            patches = self.m_hmodel.getPatches()
            glColor3f(5.0, 0.0, 1.0)
            for pat in patches:
                triangs = Tesselation.tessellate(pat.getPoints())
                for triang in triangs:
                    glBegin(GL_TRIANGLES)
                    for pt in triang:
                        glVertex2d(pt.getX(), pt.getY())
                    glEnd()

            segments = self.m_hmodel.getSegments()
            glColor3f(0.0, 1.0, 1.0)
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glBegin(GL_LINES)

                glVertex2f(ptc[0].getX(), ptc[0].getY())
                glVertex2f(ptc[1].getX(), ptc[1].getY())

                glEnd()

            verts = self.m_hmodel.getPoints()
            glColor3f(3.0, 0.0, 1.0)
            glPointSize(5)
            glBegin(GL_POINTS)
            ptf0_U = self.convertPtCoordsToUniverse(self.m_ptf0)
            ptf1_U = self.convertPtCoordsToUniverse(self.m_ptf1)
            k = []
            for vert in verts:
                if (
                        ((ptf0_U.x() <= vert.getX() <= ptf1_U.x()) and (ptf1_U.y() <= vert.getY() <= ptf0_U.y())) or
                        ((ptf0_U.x() >= vert.getX() >= ptf1_U.x()) and (ptf0_U.y() >= vert.getY() >= ptf1_U.y())) or
                        ((ptf0_U.x() >= vert.getX() >= ptf1_U.x()) and (ptf0_U.y() <= vert.getY() <= ptf1_U.y())) or
                        ((ptf0_U.x() <= vert.getX() <= ptf1_U.x()) and (ptf0_U.y() <= vert.getY() <= ptf1_U.y()))
                ):
                    glColor3f(1.0, 0.0, 0.0)

                    self.selections.append([vert.getX(), vert.getY()])
                    glVertex2f(vert.getX(), vert.getY())
                else:
                    glColor3f(0.0, 1.0, 0.0)
                    glVertex2f(vert.getX(), vert.getY())
            glEnd()

        ptf0_U = self.convertPtCoordsToUniverse(self.m_ptf0)
        ptf1_U = self.convertPtCoordsToUniverse(self.m_ptf1)

        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(ptf0_U.x(), ptf0_U.y())
        glVertex2f(ptf1_U.x(), ptf0_U.y())
        glVertex2f(ptf1_U.x(), ptf1_U.y())
        glVertex2f(ptf0_U.x(), ptf1_U.y())
        glVertex2f(ptf0_U.x(), ptf0_U.y())
        glEnd()
        glEndList()
    
    def setGrid(self, a, b):
        spacebtnw = self.m_w /a
        spacebtnh = self.m_h /b
        point = 0
        xpoints = []
        ypoints = []
        for i in range(a):
            pt = [self.convertPtCoordsToUniverse(QtCore.QPointF(point,0)).x(),
                self.convertPtCoordsToUniverse(QtCore.QPointF(point,0)).y()]
            xpoints.append(pt)
            point += spacebtnw

        point = 0

        for j in range(b):
            pt = [self.convertPtCoordsToUniverse(QtCore.QPointF(0, point)).x(),
                self.convertPtCoordsToUniverse(QtCore.QPointF(0, point)).y()]
            ypoints.append(pt)
            point += spacebtnh

        patches = self.m_hmodel.getPatches()
        pointsDict = dict()
        pointsInMatrix = [[0 for x in range(a)] for y in range(b)]

        cx = 0
        cy = 0
        for i in xpoints:
            for j in ypoints:
                for pat in patches:
                    p = Point(i[0],j[1])
                    self.points.append(Point(i[0],j[1]))
                    if pat.isPointInside(p):
                        pointsInMatrix[cy][cx] = [i[0],j[1]]
                        self.m_controller.insertPoint([i[0],j[1]], self.tol)
                cy += 1
            cy = 0
            cx += 1

        self.pointsIn = pointsInMatrix
        self.update()
        self.paintGL()
    
    def isPointInsideRegion(self, point, polygon_vertices):
        x, y = point
        n = len(polygon_vertices)
        inside = False

        p1x, p1y = polygon_vertices[0].getX(), polygon_vertices[0].getY()
        for i in range(1, n + 1):
            p2x, p2y = polygon_vertices[i % n].getX(), polygon_vertices[i % n].getY()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
            
    def convertPtCoordsToUniverse(self, _pt):
        dX = self.m_R - self.m_L
        dY = self.m_T - self.m_B
        mX = _pt.x() * dX / self.m_w
        mY = (self.m_h - _pt.y()) * dY / self.m_h
        x = self.m_L + mX
        y = self.m_B + mY
        return QtCore.QPointF(x,y)
    
    def mousePressEvent(self, event):
        if event.button() == 1:
            self.m_buttonPressed = True
            self.m_pt0 = event.pos()
        else:
            self.m_buttonPressedF = True
            self.m_ptf0 = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()
        if self.m_buttonPressedF:
            self.m_ptf1 = event.pos()
            self.update()
        
    def mouseReleaseEvent(self, event):
        if event.button() == 1:
            pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
            pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)

            self.m_model.setCurve(pt0_U.x(),pt0_U.y(),pt1_U.x(),pt1_U.y())
            self.m_controller.insertSegment([pt0_U.x(),pt0_U.y(),pt1_U.x(),pt1_U.y()], self.tol)
            self.m_buttonPressed = False
            self.m_pt0.setX(0)
            self.m_pt0.setY(0)
            self.m_pt1.setX(0)
            self.m_pt1.setY(0)
            self.update()
            self.paintGL()

        else:
            ptf0_U = self.convertPtCoordsToUniverse(self.m_ptf0)
            ptf1_U = self.convertPtCoordsToUniverse(self.m_ptf1)

            self.m_ptf0 = QtCore.QPointF(0.0,0.0)
            self.m_ptf1 = QtCore.QPointF(0.0,0.0)
            self.m_buttonPressedF = False
            self.update()
            
    def setTemp(self, temp):
        for p in self.selections:
            self.pointTemp[(p[0],p[1])] = temp
        self.selections = []
        
    def setForce(self, force):
        for p in self.selections:
            self.pointForce[(p[0],p[1])] = force
        self.selections = []
    
    def setModel(self,_model):
        self.m_model = _model

    def fitWorldToViewport(self):
        if (self.m_model==None)or(self.m_model.isEmpty()): return
        self.m_L,self.m_R,self.m_B,self.m_T=self.m_model.getBoundBox()
        self.scaleWorldWindow(1.10)
        self.update()

    def scaleWorldWindow(self,_scaleFac):
        # Compute canvas viewport distortion ratio.
        vpr = self.m_h / self.m_w
        # Get current window center.
        cx = (self.m_L + self.m_R) / 2.0
        cy = (self.m_B + self.m_T) / 2.0
        # Set new window sizes based on scaling factor.
        sizex = (self.m_R - self.m_L) * _scaleFac
        sizey = (self.m_T - self.m_B) * _scaleFac
        # Adjust window to keep the same aspect ratio of the viewport.
        if sizey > (vpr*sizex):
            sizex = sizey / vpr
        else:
            sizey = sizex * vpr
        self.m_L = cx - (sizex * 0.5)
        self.m_R = cx + (sizex * 0.5)
        self.m_B = cy - (sizey * 0.5)
        self.m_T = cy + (sizey * 0.5)
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)

    def panWorldWindow(self, _panFacX, _panFacY):
        # Compute pan distances in horizontal and vertical directions.
        panX = (self.m_R - self.m_L) * _panFacX
        panY = (self.m_T - self.m_B) * _panFacY
        # Shift current window.
        self.m_L += panX
        self.m_R += panX
        self.m_B += panY
        self.m_T += panY
        # Establish the clipping volume by setting up an
        # orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self.m_L, self.m_R, self.m_B, self.m_T, -1.0, 1.0)