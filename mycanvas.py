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
        self.m_pt0 = QtCore.QPoint(0, 0)
        self.m_pt1 = QtCore.QPoint(0, 0)
        self.m_hmodel = HeModel()
        self.m_controller = HeController(self.m_hmodel)
        self.tol = 0.1
        
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
        if(self.m_model==None)or(self.m_model.isEmpty()): 
            return
        glCallList(self.list)
        glDeleteLists(self.list, 1)
        self.list = glGenLists(1)
        glNewList(self.list, GL_COMPILE)
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINE_STRIP)
        glVertex2f(pt0_U.x(), pt0_U.y())
        glVertex2f(pt1_U.x(), pt1_U.y())
        glEnd()
        if not((self.m_model == None) and (self.m_model.isEmpty())):
            verts = self.m_model.getVerts()
            glColor3f(0.0, 1.0, 0.0) # green
            glBegin(GL_TRIANGLES)
            for vtx in verts:
                glVertex2f(vtx.getX(), vtx.getY())
            glEnd()
            curves = self.m_model.getCurves()
            glColor3f(0.0, 0.0, 1.0) # blue
            glBegin(GL_LINES)
            for curv in curves:
                glVertex2f(curv.getP1().getX(), curv.getP1().getY())
                glVertex2f(curv.getP2().getX(), curv.getP2().getY())
            glEnd()
        
        if not(self.m_hmodel.isEmpty()):
            print("teste")
            patches = self.m_hmodel.getPatches() # retalhos, regioes construídas automaticamente
            glColor3f(3.0, 0.0, 1.0)
            for pat in patches:
                print('Patches: ' + str(len(patches)))
                triangs = Tesselation.tessellate(pat.getPoints())
                for triang in triangs:
                    glBegin(GL_TRIANGLES)
                    for pt in triang:
                        glVertex2d(pt.getX(), pt.getY())
                    glEnd()

            segments = self.m_hmodel.getSegments()
            glColor3f(0.0, 1.0, 1.0)
            print(len(segments))
            for curv in segments:
                ptc = curv.getPointsToDraw()
                glBegin(GL_LINES)

                glVertex2f(ptc[0].getX(), ptc[0].getY())
                glVertex2f(ptc[1].getX(), ptc[1].getY())
                
                glEnd()
                
            verts = self.m_hmodel.getPoints()
            glColor3f(1.0, 0.0, 0.0)
            glPointSize(5)
            glBegin(GL_POINTS)
            for vert in verts:
                glVertex2f(vert.getX(), vert.getY())
            glEnd()
            print(verts)
            
        glEndList()
        
        if(len(patches) > 0):
            x_min = min(vtx.getX() for vtx in verts)
            x_max = max(vtx.getX() for vtx in verts)
            y_min = min(vtx.getY() for vtx in verts)
            y_max = max(vtx.getY() for vtx in verts)
            spacing = 60
            
            grid_points = self.generateGridPoints(x_min, x_max, y_min, y_max, spacing)

            points_inside_region = [pt for pt in grid_points if self.isPointInsideRegion(pt, verts)]
            
            glColor3f(1.0, 1.0, 0.0)  # Cor amarela para os pontos do grid
            glPointSize(5)
            glBegin(GL_POINTS)
            for pt in points_inside_region:
                glVertex2f(pt[0], pt[1])
            glEnd()
    
    def generateGridPoints(self, x_min, x_max, y_min, y_max, spacing):
        points = []
        y = y_min
        while y <= y_max:
            x = x_min
            while x <= x_max:
                points.append((x, y))
                x += spacing
            y += spacing
        return points
    
    # def isPointInsideRegion(self, point, region_vertices):
    #     x_min = min(vertex.getX() for vertex in region_vertices)
    #     x_max = max(vertex.getX() for vertex in region_vertices)
    #     y_min = min(vertex.getY() for vertex in region_vertices)
    #     y_max = max(vertex.getY() for vertex in region_vertices)
    #     x, y = point
    #     return x_min <= x <= x_max and y_min <= y <= y_max
    
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
        self.m_buttonPressed = True
        self.m_pt0 = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.m_buttonPressed:
            self.m_pt1 = event.pos()
            self.update()
        
    def mouseReleaseEvent(self, event):
        pt0_U = self.convertPtCoordsToUniverse(self.m_pt0)
        pt1_U = self.convertPtCoordsToUniverse(self.m_pt1)
        self.m_model.setCurve(pt0_U.x(), pt0_U.y(), pt1_U.x(), pt1_U.y())
        # self.m_model.setCurve(self.m_pt0.x(), self.m_pt0.y(), self.m_pt1.x(), self.m_pt1.y())
        self.m_buttonPressed = False
        self.m_pt0.setX(0)
        self.m_pt0.setY(0)
        self.m_pt1.setX(0)
        self.m_pt1.setY(0)
        p0 = Point(pt0_U.x(), pt0_U.y())
        p1 = Point(pt1_U.x(), pt1_U.y())
        segment = Line(p0, p1)
        self.m_controller.insertSegment(segment, 0.01)
        self.update()
        self.repaint()

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