#!/bin/python3

from vcdvcd import VCDVCD
from pyqtgraph import ArrowItem, CurveArrow
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (
    QWidget, 
    QApplication, 
    QMainWindow, 
    QLabel, 
    QGroupBox, 
    QPushButton, 
    QGraphicsScene, 
    QGridLayout, 
    QGraphicsView, 
    QVBoxLayout, 
    QProgressBar, 
    QHBoxLayout, 
    QShortcut, 
    QGraphicsRectItem, 
    QGraphicsSimpleTextItem,
    QGraphicsLineItem,
    QGraphicsItemGroup
)
from PyQt5.QtGui import QKeySequence, QBrush, QPen, QColor
from functools import partial
import sys
import os

# constants
SWERV_TOP = "TOP.tb_top.rvtop.swerv."
SWERV_DEC_DECODE = SWERV_TOP + "dec.decode."
SWERV_DEC_IB     = SWERV_TOP + "dec.instbuff."
SWERV_EXU        = SWERV_TOP + "exu."

# ===[ GUI Class ]=========================================
class SweRVisual(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SweRVisualize")
        self.setGeometry(200, 200, 1000, 800)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self._createGraphicsView()
        self._createCycleLabel()
        self._createButtons()
        self._setupDrawing()
        self._addObjectsToScene()
        self._addForwardingArrows()
        self._hideAllArrows()
        self._positionObjects()

    # define brushes etc.
    def _setupDrawing(self):
        self.brush_stage_valid = QBrush(QColor(0x71, 0xff, 0x7d))
        self.brush_stage_invalid = QBrush(QColor(0xff, 0x5b, 0x62))

        self.brush_freeze = QBrush(QColor(0x25, 0xb4, 0xda))
        self.brush_flush = QBrush(Qt.black)

        self.pen_line_rs1 = QPen(Qt.cyan, 3, Qt.DotLine)
        self.pen_arrow_rs1 = QPen(Qt.cyan, 1, Qt.SolidLine)
        self.brush_arrow_head_rs1 = QBrush(Qt.cyan)

        self.pen_line_rs2 = QPen(Qt.magenta, 3, Qt.DotLine)
        self.pen_arrow_rs2 = QPen(Qt.magenta, 1, Qt.SolidLine)
        self.brush_arrow_head_rs2 = QBrush(Qt.magenta)

    # center object within its parents bounding rect
    def _centerObjectWithinParent(self, obj):
        x_offset = (obj.parentItem().boundingRect().width() - obj.boundingRect().width()) / 2
        y_offset = (obj.parentItem().boundingRect().height() - obj.boundingRect().height()) / 2
        obj.setPos(x_offset, y_offset)

    def _addForwardingArrows(self):
        # forwarding arrows

        # I0_E1 -> I0 RS1
        self.I0_E1_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(110, 40, 115, 40, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(115, 40, 115, -10, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(115, -10, -30, -10, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, -10, -30, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E1_I0_RS1.addToGroup(line1)
        self.I0_E1_I0_RS1.addToGroup(line2)
        self.I0_E1_I0_RS1.addToGroup(line3)
        self.I0_E1_I0_RS1.addToGroup(line4)
        self.I0_E1_I0_RS1.addToGroup(arrow)

        # I0_E1 -> I0 RS2
        self.I0_E1_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(110, 50, 120, 50, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(120, 50, 120, -15, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(120, -15, -35, -15, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, -15, -35, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E1_I0_RS2.addToGroup(line1)
        self.I0_E1_I0_RS2.addToGroup(line2)
        self.I0_E1_I0_RS2.addToGroup(line3)
        self.I0_E1_I0_RS2.addToGroup(line4)
        self.I0_E1_I0_RS2.addToGroup(arrow)

        # I0_E2 -> I0 RS1
        self.I0_E2_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(230, 40, 235, 40, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(235, 40, 235, -10, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(235, -10, -30, -10, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, -10, -30, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E2_I0_RS1.addToGroup(line1)
        self.I0_E2_I0_RS1.addToGroup(line2)
        self.I0_E2_I0_RS1.addToGroup(line3)
        self.I0_E2_I0_RS1.addToGroup(line4)
        self.I0_E2_I0_RS1.addToGroup(arrow)

        # I0_E2 -> I0 RS2
        self.I0_E2_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(230, 50, 240, 50, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(240, 50, 240, -15, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(240, -15, -35, -15, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, -15, -35, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E2_I0_RS2.addToGroup(line1)
        self.I0_E2_I0_RS2.addToGroup(line2)
        self.I0_E2_I0_RS2.addToGroup(line3)
        self.I0_E2_I0_RS2.addToGroup(line4)
        self.I0_E2_I0_RS2.addToGroup(arrow)

        # I0_E3 -> I0 RS1
        self.I0_E3_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(350, 40, 355, 40, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(355, 40, 355, -10, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(355, -10, -30, -10, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, -10, -30, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E3_I0_RS1.addToGroup(line1)
        self.I0_E3_I0_RS1.addToGroup(line2)
        self.I0_E3_I0_RS1.addToGroup(line3)
        self.I0_E3_I0_RS1.addToGroup(line4)
        self.I0_E3_I0_RS1.addToGroup(arrow)

        # I0_E2 -> I0 RS2
        self.I0_E3_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(350, 50, 360, 50, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(360, 50, 360, -15, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(360, -15, -35, -15, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, -15, -35, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E3_I0_RS2.addToGroup(line1)
        self.I0_E3_I0_RS2.addToGroup(line2)
        self.I0_E3_I0_RS2.addToGroup(line3)
        self.I0_E3_I0_RS2.addToGroup(line4)
        self.I0_E3_I0_RS2.addToGroup(arrow)

        # I0_E4 -> I0 RS1
        self.I0_E4_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(470, 40, 475, 40, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(475, 40, 475, -10, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(475, -10, -30, -10, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, -10, -30, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E4_I0_RS1.addToGroup(line1)
        self.I0_E4_I0_RS1.addToGroup(line2)
        self.I0_E4_I0_RS1.addToGroup(line3)
        self.I0_E4_I0_RS1.addToGroup(line4)
        self.I0_E4_I0_RS1.addToGroup(arrow)

        # I0_E4 -> I0 RS2
        self.I0_E4_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(470, 50, 480, 50, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(480, 50, 480, -15, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(480, -15, -35, -15, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, -15, -35, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E4_I0_RS2.addToGroup(line1)
        self.I0_E4_I0_RS2.addToGroup(line2)
        self.I0_E4_I0_RS2.addToGroup(line3)
        self.I0_E4_I0_RS2.addToGroup(line4)
        self.I0_E4_I0_RS2.addToGroup(arrow)

        # I0_WB -> I0 RS1
        self.I0_WB_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(590, 40, 605, 40, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(605, 40, 605, -10, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(605, -10, -30, -10, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, -10, -30, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_WB_I0_RS1.addToGroup(line1)
        self.I0_WB_I0_RS1.addToGroup(line2)
        self.I0_WB_I0_RS1.addToGroup(line3)
        self.I0_WB_I0_RS1.addToGroup(line4)
        self.I0_WB_I0_RS1.addToGroup(arrow)

        # I0_WB -> I0 RS2
        self.I0_WB_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(590, 50, 610, 50, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(610, 50, 610, -15, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(610, -15, -35, -15, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, -15, -35, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_WB_I0_RS2.addToGroup(line1)
        self.I0_WB_I0_RS2.addToGroup(line2)
        self.I0_WB_I0_RS2.addToGroup(line3)
        self.I0_WB_I0_RS2.addToGroup(line4)
        self.I0_WB_I0_RS2.addToGroup(arrow)

        #----------------------------------------------
        # I0_E1 -> I1 RS1
        self.I0_E1_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(110, 70, 120, 70, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(120, 70, 120, 118, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(120, 118, -30, 118, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 118, -30, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E1_I1_RS1.addToGroup(line1)
        self.I0_E1_I1_RS1.addToGroup(line2)
        self.I0_E1_I1_RS1.addToGroup(line3)
        self.I0_E1_I1_RS1.addToGroup(line4)
        self.I0_E1_I1_RS1.addToGroup(arrow)

        # I0_E1 -> I1 RS2
        self.I0_E1_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(110, 80, 115, 80, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(115, 80, 115, 113, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(115, 113, -35, 113, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 113, -35, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E1_I1_RS2.addToGroup(line1)
        self.I0_E1_I1_RS2.addToGroup(line2)
        self.I0_E1_I1_RS2.addToGroup(line3)
        self.I0_E1_I1_RS2.addToGroup(line4)
        self.I0_E1_I1_RS2.addToGroup(arrow)

        # I0_E2 -> I1 RS1
        self.I0_E2_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(230, 70, 240, 70, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(240, 70, 240, 118, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(240, 118, -30, 118, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 118, -30, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E2_I1_RS1.addToGroup(line1)
        self.I0_E2_I1_RS1.addToGroup(line2)
        self.I0_E2_I1_RS1.addToGroup(line3)
        self.I0_E2_I1_RS1.addToGroup(line4)
        self.I0_E2_I1_RS1.addToGroup(arrow)

        # I0_E2 -> I1 RS2
        self.I0_E2_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(230, 80, 235, 80, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(235, 80, 235, 113, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(235, 113, -35, 113, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 113, -35, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E2_I1_RS2.addToGroup(line1)
        self.I0_E2_I1_RS2.addToGroup(line2)
        self.I0_E2_I1_RS2.addToGroup(line3)
        self.I0_E2_I1_RS2.addToGroup(line4)
        self.I0_E2_I1_RS2.addToGroup(arrow)

        # I0_E3 -> I1 RS1
        self.I0_E3_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(350, 70, 360, 70, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(360, 70, 360, 118, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(360, 118, -30, 118, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 118, -30, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E3_I1_RS1.addToGroup(line1)
        self.I0_E3_I1_RS1.addToGroup(line2)
        self.I0_E3_I1_RS1.addToGroup(line3)
        self.I0_E3_I1_RS1.addToGroup(line4)
        self.I0_E3_I1_RS1.addToGroup(arrow)

        # I0_E2 -> I1 RS2
        self.I0_E3_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(350, 80, 355, 80, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(355, 80, 355, 113, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(355, 113, -35, 113, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 113, -35, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E3_I1_RS2.addToGroup(line1)
        self.I0_E3_I1_RS2.addToGroup(line2)
        self.I0_E3_I1_RS2.addToGroup(line3)
        self.I0_E3_I1_RS2.addToGroup(line4)
        self.I0_E3_I1_RS2.addToGroup(arrow)

        # I0_E4 -> I1 RS1
        self.I0_E4_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(470, 70, 480, 70, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(480, 70, 480, 118, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(480, 118, -30, 118, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 118, -30, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_E4_I1_RS1.addToGroup(line1)
        self.I0_E4_I1_RS1.addToGroup(line2)
        self.I0_E4_I1_RS1.addToGroup(line3)
        self.I0_E4_I1_RS1.addToGroup(line4)
        self.I0_E4_I1_RS1.addToGroup(arrow)

        # I0_E4 -> I1 RS2
        self.I0_E4_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(470, 80, 475, 80, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(475, 80, 475, 113, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(475, 113, -35, 113, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 113, -35, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_E4_I1_RS2.addToGroup(line1)
        self.I0_E4_I1_RS2.addToGroup(line2)
        self.I0_E4_I1_RS2.addToGroup(line3)
        self.I0_E4_I1_RS2.addToGroup(line4)
        self.I0_E4_I1_RS2.addToGroup(arrow)

        # I0_WB -> I1 RS1
        self.I0_WB_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(590, 70, 610, 70, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(610, 70, 610, 118, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(610, 118, -30, 118, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 118, -30, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I0_WB_I1_RS1.addToGroup(line1)
        self.I0_WB_I1_RS1.addToGroup(line2)
        self.I0_WB_I1_RS1.addToGroup(line3)
        self.I0_WB_I1_RS1.addToGroup(line4)
        self.I0_WB_I1_RS1.addToGroup(arrow)

        # I0_WB -> I1 RS2
        self.I0_WB_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(590, 80, 605, 80, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(605, 80, 605, 113, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(605, 113, -35, 113, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 113, -35, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I0_WB_I1_RS2.addToGroup(line1)
        self.I0_WB_I1_RS2.addToGroup(line2)
        self.I0_WB_I1_RS2.addToGroup(line3)
        self.I0_WB_I1_RS2.addToGroup(line4)
        self.I0_WB_I1_RS2.addToGroup(arrow)

        #----------------------------------------------
        # I1_E1 -> I1 RS1
        self.I1_E1_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(110, 190, 120, 190, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(120, 190, 120, 255, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(120, 255, -35, 255, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 255, -35, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E1_I1_RS1.addToGroup(line1)
        self.I1_E1_I1_RS1.addToGroup(line2)
        self.I1_E1_I1_RS1.addToGroup(line3)
        self.I1_E1_I1_RS1.addToGroup(line4)
        self.I1_E1_I1_RS1.addToGroup(arrow)

        # I1_E1 -> I1 RS2
        self.I1_E1_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(110, 200, 115, 200, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(115, 200, 115, 250, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(115, 250, -30, 250, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 250, -30, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E1_I1_RS2.addToGroup(line1)
        self.I1_E1_I1_RS2.addToGroup(line2)
        self.I1_E1_I1_RS2.addToGroup(line3)
        self.I1_E1_I1_RS2.addToGroup(line4)
        self.I1_E1_I1_RS2.addToGroup(arrow)

        # I1_E2 -> I1 RS1
        self.I1_E2_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(230, 190, 240, 190, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(240, 190, 240, 255, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(240, 255, -35, 255, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 255, -35, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E2_I1_RS1.addToGroup(line1)
        self.I1_E2_I1_RS1.addToGroup(line2)
        self.I1_E2_I1_RS1.addToGroup(line3)
        self.I1_E2_I1_RS1.addToGroup(line4)
        self.I1_E2_I1_RS1.addToGroup(arrow)

        # I1_E2 -> I1 RS2
        self.I1_E2_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(230, 200, 235, 200, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(235, 200, 235, 250, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(235, 250, -30, 250, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 250, -30, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E2_I1_RS2.addToGroup(line1)
        self.I1_E2_I1_RS2.addToGroup(line2)
        self.I1_E2_I1_RS2.addToGroup(line3)
        self.I1_E2_I1_RS2.addToGroup(line4)
        self.I1_E2_I1_RS2.addToGroup(arrow)

        # I1_E3 -> I1 RS1
        self.I1_E3_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(350, 190, 360, 190, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(360, 190, 360, 255, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(360, 255, -35, 255, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 255, -35, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E3_I1_RS1.addToGroup(line1)
        self.I1_E3_I1_RS1.addToGroup(line2)
        self.I1_E3_I1_RS1.addToGroup(line3)
        self.I1_E3_I1_RS1.addToGroup(line4)
        self.I1_E3_I1_RS1.addToGroup(arrow)

        # I1_E3 -> I1 RS2
        self.I1_E3_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(350, 200, 355, 200, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(355, 200, 355, 250, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(355, 250, -30, 250, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 250, -30, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E3_I1_RS2.addToGroup(line1)
        self.I1_E3_I1_RS2.addToGroup(line2)
        self.I1_E3_I1_RS2.addToGroup(line3)
        self.I1_E3_I1_RS2.addToGroup(line4)
        self.I1_E3_I1_RS2.addToGroup(arrow)

        # I1_E4 -> I1 RS1
        self.I1_E4_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(470, 190, 480, 190, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(480, 190, 480, 255, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(480, 255, -35, 255, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 255, -35, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E4_I1_RS1.addToGroup(line1)
        self.I1_E4_I1_RS1.addToGroup(line2)
        self.I1_E4_I1_RS1.addToGroup(line3)
        self.I1_E4_I1_RS1.addToGroup(line4)
        self.I1_E4_I1_RS1.addToGroup(arrow)

        # I1_E4 -> I1 RS2
        self.I1_E4_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(470, 200, 475, 200, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(475, 200, 475, 250, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(475, 250, -30, 250, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 250, -30, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E4_I1_RS2.addToGroup(line1)
        self.I1_E4_I1_RS2.addToGroup(line2)
        self.I1_E4_I1_RS2.addToGroup(line3)
        self.I1_E4_I1_RS2.addToGroup(line4)
        self.I1_E4_I1_RS2.addToGroup(arrow)

        # I1_WB -> I1 RS1
        self.I1_WB_I1_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 170)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(590, 190, 610, 190, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(610, 190, 610, 255, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(610, 255, -35, 255, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 255, -35, 170, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_WB_I1_RS1.addToGroup(line1)
        self.I1_WB_I1_RS1.addToGroup(line2)
        self.I1_WB_I1_RS1.addToGroup(line3)
        self.I1_WB_I1_RS1.addToGroup(line4)
        self.I1_WB_I1_RS1.addToGroup(arrow)

        # I1_WB -> I1 RS2
        self.I1_WB_I1_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 190)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(590, 200, 605, 200, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(605, 200, 605, 250, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(605, 250, -30, 250, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 250, -30, 190, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_WB_I1_RS2.addToGroup(line1)
        self.I1_WB_I1_RS2.addToGroup(line2)
        self.I1_WB_I1_RS2.addToGroup(line3)
        self.I1_WB_I1_RS2.addToGroup(line4)
        self.I1_WB_I1_RS2.addToGroup(arrow)

        #----------------------------------------------
        # I1_E1 -> I0 RS1
        self.I1_E1_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(110, 160, 115, 160, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(115, 160, 115, 127, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(115, 127, -35, 127, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 127, -35, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E1_I0_RS1.addToGroup(line1)
        self.I1_E1_I0_RS1.addToGroup(line2)
        self.I1_E1_I0_RS1.addToGroup(line3)
        self.I1_E1_I0_RS1.addToGroup(line4)
        self.I1_E1_I0_RS1.addToGroup(arrow)

        # I1_E1 -> I0 RS2
        self.I1_E1_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(110, 170, 120, 170, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(120, 170, 120, 122, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(120, 122, -30, 122, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 122, -30, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E1_I0_RS2.addToGroup(line1)
        self.I1_E1_I0_RS2.addToGroup(line2)
        self.I1_E1_I0_RS2.addToGroup(line3)
        self.I1_E1_I0_RS2.addToGroup(line4)
        self.I1_E1_I0_RS2.addToGroup(arrow)

        # I1_E2 -> I0 RS1
        self.I1_E2_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(230, 160, 235, 160, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(235, 160, 235, 127, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(235, 127, -35, 127, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 127, -35, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E2_I0_RS1.addToGroup(line1)
        self.I1_E2_I0_RS1.addToGroup(line2)
        self.I1_E2_I0_RS1.addToGroup(line3)
        self.I1_E2_I0_RS1.addToGroup(line4)
        self.I1_E2_I0_RS1.addToGroup(arrow)

        # I1_E2 -> I0 RS2
        self.I1_E2_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(230, 170, 240, 170, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(240, 170, 240, 122, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(240, 122, -30, 122, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 122, -30, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E2_I0_RS2.addToGroup(line1)
        self.I1_E2_I0_RS2.addToGroup(line2)
        self.I1_E2_I0_RS2.addToGroup(line3)
        self.I1_E2_I0_RS2.addToGroup(line4)
        self.I1_E2_I0_RS2.addToGroup(arrow)

        # I1_E3 -> I0 RS1
        self.I1_E3_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(350, 160, 355, 160, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(355, 160, 355, 127, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(355, 127, -35, 127, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 127, -35, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E3_I0_RS1.addToGroup(line1)
        self.I1_E3_I0_RS1.addToGroup(line2)
        self.I1_E3_I0_RS1.addToGroup(line3)
        self.I1_E3_I0_RS1.addToGroup(line4)
        self.I1_E3_I0_RS1.addToGroup(arrow)

        # I1_E3 -> I0 RS2
        self.I1_E3_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(350, 170, 360, 170, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(360, 170, 360, 122, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(360, 122, -30, 122, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 122, -30, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E3_I0_RS2.addToGroup(line1)
        self.I1_E3_I0_RS2.addToGroup(line2)
        self.I1_E3_I0_RS2.addToGroup(line3)
        self.I1_E3_I0_RS2.addToGroup(line4)
        self.I1_E3_I0_RS2.addToGroup(arrow)

        # I1_E4 -> I0 RS1
        self.I1_E4_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(470, 160, 475, 160, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(475, 160, 475, 127, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(475, 127, -35, 127, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 127, -35, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_E4_I0_RS1.addToGroup(line1)
        self.I1_E4_I0_RS1.addToGroup(line2)
        self.I1_E4_I0_RS1.addToGroup(line3)
        self.I1_E4_I0_RS1.addToGroup(line4)
        self.I1_E4_I0_RS1.addToGroup(arrow)

        # I1_E4 -> I0 RS2
        self.I1_E4_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(470, 170, 480, 170, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(480, 170, 480, 122, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(480, 122, -30, 122, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 122, -30, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_E4_I0_RS2.addToGroup(line1)
        self.I1_E4_I0_RS2.addToGroup(line2)
        self.I1_E4_I0_RS2.addToGroup(line3)
        self.I1_E4_I0_RS2.addToGroup(line4)
        self.I1_E4_I0_RS2.addToGroup(arrow)

        # I1_WB -> I0 RS1
        self.I1_WB_I0_RS1 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=15, angle=180)
        arrow.setPos(0, 50)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)

        line1 = QGraphicsLineItem(590, 160, 605, 160, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(605, 160, 605, 127, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(605, 127, -35, 127, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-35, 127, -35, 50, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        line3.setPen(self.pen_line_rs1)
        line4.setPen(self.pen_line_rs1)

        self.I1_WB_I0_RS1.addToGroup(line1)
        self.I1_WB_I0_RS1.addToGroup(line2)
        self.I1_WB_I0_RS1.addToGroup(line3)
        self.I1_WB_I0_RS1.addToGroup(line4)
        self.I1_WB_I0_RS1.addToGroup(arrow)

        # I1_WB -> I0 RS2
        self.I1_WB_I0_RS2 = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, 70)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)

        line1 = QGraphicsLineItem(590, 170, 610, 170, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(610, 170, 610, 122, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(610, 122, -30, 122, parent=self.exe_bounding_rect)
        line4 = QGraphicsLineItem(-30, 122, -30, 70, parent=self.exe_bounding_rect)
        line1.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        line3.setPen(self.pen_line_rs2)
        line4.setPen(self.pen_line_rs2)

        self.I1_WB_I0_RS2.addToGroup(line1)
        self.I1_WB_I0_RS2.addToGroup(line2)
        self.I1_WB_I0_RS2.addToGroup(line3)
        self.I1_WB_I0_RS2.addToGroup(line4)
        self.I1_WB_I0_RS2.addToGroup(arrow)

    def _hideAllArrows(self):
        # hide all arrows by default
        self.I0_E1_I0_RS1.hide()
        self.I0_E1_I0_RS2.hide()
        self.I0_E2_I0_RS1.hide()
        self.I0_E2_I0_RS2.hide()
        self.I0_E3_I0_RS1.hide()
        self.I0_E3_I0_RS2.hide()
        self.I0_E4_I0_RS1.hide()
        self.I0_E4_I0_RS2.hide()
        self.I0_WB_I0_RS1.hide()
        self.I0_WB_I0_RS2.hide()
        
        self.I0_E1_I1_RS1.hide()
        self.I0_E1_I1_RS2.hide()
        self.I0_E2_I1_RS1.hide()
        self.I0_E2_I1_RS2.hide()
        self.I0_E3_I1_RS1.hide()
        self.I0_E3_I1_RS2.hide()
        self.I0_E4_I1_RS1.hide()
        self.I0_E4_I1_RS2.hide()
        self.I0_WB_I1_RS1.hide()
        self.I0_WB_I1_RS2.hide()

        self.I1_E1_I1_RS1.hide()
        self.I1_E1_I1_RS2.hide()
        self.I1_E2_I1_RS1.hide()
        self.I1_E2_I1_RS2.hide()
        self.I1_E3_I1_RS1.hide()
        self.I1_E3_I1_RS2.hide()
        self.I1_E4_I1_RS1.hide()
        self.I1_E4_I1_RS2.hide()
        self.I1_WB_I1_RS1.hide()
        self.I1_WB_I1_RS2.hide()
        
        self.I1_E1_I0_RS1.hide()
        self.I1_E1_I0_RS2.hide()
        self.I1_E2_I0_RS1.hide()
        self.I1_E2_I0_RS2.hide()
        self.I1_E3_I0_RS1.hide()
        self.I1_E3_I0_RS2.hide()
        self.I1_E4_I0_RS1.hide()
        self.I1_E4_I0_RS2.hide()
        self.I1_WB_I0_RS1.hide()
        self.I1_WB_I0_RS2.hide()

    # adding all objects to the scene without positioning
    def _addObjectsToScene(self):
        
        width = 100
        spacing = 20
        offset = spacing/2

        # IB 
        self.IB_bounding_rect = self.scene.addRect(0, 0, 2.5*width, width)
        
        self.bypassdebugI0RS1 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)
        self.bypassdebugI0RS2 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)
        self.bypassdebugI1RS1 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)
        self.bypassdebugI1RS2 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)

        self.IB0 = QGraphicsRectItem(0, 0,  30, 25, parent=self.IB_bounding_rect)
        self.IB1 = QGraphicsRectItem(0, 0, 30, 25, parent=self.IB_bounding_rect)
        self.IB2 = QGraphicsRectItem(0, 0, 30, 25, parent=self.IB_bounding_rect)
        self.IB3 = QGraphicsRectItem(0, 0, 30, 25, parent=self.IB_bounding_rect)
        self.IB0_PC = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        self.IB1_PC = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        self.IB2_PC = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        self.IB3_PC = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)

        self.IB0_Ins = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        self.IB1_Ins = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        self.IB2_Ins = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        self.IB3_Ins = QGraphicsRectItem(0, 0, width+offset, 25, parent=self.IB_bounding_rect)
        
        self.IB0_PC_text = QGraphicsSimpleTextItem("PC: 00000000", parent=self.IB0_PC)
        self.IB1_PC_text = QGraphicsSimpleTextItem("PC: 00000000", parent=self.IB1_PC)
        self.IB2_PC_text = QGraphicsSimpleTextItem("PC: 00000000", parent=self.IB2_PC)
        self.IB3_PC_text = QGraphicsSimpleTextItem("PC: 00000000", parent=self.IB3_PC)
        
        self.IB0_Ins_text = QGraphicsSimpleTextItem("Ins: 00000000", parent=self.IB0_Ins)
        self.IB1_Ins_text = QGraphicsSimpleTextItem("Ins: 00000000", parent=self.IB1_Ins)
        self.IB2_Ins_text = QGraphicsSimpleTextItem("Ins: 00000000", parent=self.IB2_Ins)
        self.IB3_Ins_text = QGraphicsSimpleTextItem("Ins: 00000000", parent=self.IB3_Ins)

        self._centerObjectWithinParent(QGraphicsSimpleTextItem("IB0", parent=self.IB0))
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("IB1", parent=self.IB1))
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("IB2", parent=self.IB2))
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("IB3", parent=self.IB3))

        # pipeline stages
        self.exe_bounding_rect = self.scene.addRect(0, 0, 5*(width+spacing), 2*(width+spacing))

        self.freezable_stages = QGraphicsRectItem(0, 0, 2*offset+3*width+2*spacing, 2*offset+2*width+spacing, parent=self.exe_bounding_rect)
        self.flushable_stages = QGraphicsRectItem(0, 0, 2*offset+2*width+spacing, 2*offset+2*width+spacing, parent=self.exe_bounding_rect)
        self.flush_lower = QGraphicsRectItem(0, 0, width, 25, parent=self.exe_bounding_rect)
        self.flush_upper = QGraphicsRectItem(0, 0, width, 25, parent=self.exe_bounding_rect)
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("Flush", parent=self.flush_lower))
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("Flush", parent=self.flush_upper))

        self.I0_1  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I0_2  = QGraphicsRectItem(0, 0 ,width, width, parent=self.exe_bounding_rect)
        self.I0_3  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I0_4  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I0_WB = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)

        self.I1_1  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I1_2  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I1_3  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I1_4  = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)
        self.I1_WB = QGraphicsRectItem(0, 0, width, width, parent=self.exe_bounding_rect)

        self.I0_1_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I0_1)
        self.I0_2_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I0_2)
        self.I0_3_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I0_3)
        self.I0_4_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I0_4)
        self.I0_WB_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I0_WB)
        
        self.I1_1_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I1_1)
        self.I1_2_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I1_2)
        self.I1_3_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I1_3)
        self.I1_4_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I1_4)
        self.I1_WB_class = QGraphicsRectItem(0, 0, width, 20, parent=self.I1_WB)

        self.I0_1_regs = QGraphicsRectItem(0, 0, width, 60, parent=self.I0_1)
        self.I0_2_regs = QGraphicsRectItem(0, 0, width, 60, parent=self.I0_2)
        self.I0_3_regs = QGraphicsRectItem(0, 0, width, 60, parent=self.I0_3)
        self.I0_4_regs = QGraphicsRectItem(0, 0, width, 60, parent=self.I0_4)
        self.I0_WB_regs = QGraphicsRectItem(0, 0, width, 60, parent=self.I0_WB)

        self.I0_1_class_text = QGraphicsSimpleTextItem("I0 class", parent=self.I0_1_class)
        self.I0_2_class_text = QGraphicsSimpleTextItem("I0 class", parent=self.I0_2_class)
        self.I0_3_class_text = QGraphicsSimpleTextItem("I0 class", parent=self.I0_3_class)
        self.I0_4_class_text = QGraphicsSimpleTextItem("I0 class", parent=self.I0_4_class)
        self.I0_WB_class_text = QGraphicsSimpleTextItem("I0 class", parent=self.I0_WB_class)
        
        self.I1_1_class_text = QGraphicsSimpleTextItem("I1 class", parent=self.I1_1_class)
        self.I1_2_class_text = QGraphicsSimpleTextItem("I1 class", parent=self.I1_2_class)
        self.I1_3_class_text = QGraphicsSimpleTextItem("I1 class", parent=self.I1_3_class)
        self.I1_4_class_text = QGraphicsSimpleTextItem("I1 class", parent=self.I1_4_class)
        self.I1_WB_class_text = QGraphicsSimpleTextItem("I1 class", parent=self.I1_WB_class)

        self.I0_1_regs_text = QGraphicsSimpleTextItem("RS1: x00\nRS2: x00\nRD:  x00", parent=self.I0_1_regs)
        self.I0_2_regs_text = QGraphicsSimpleTextItem("RS1: x00\nRS2: x00\nRD:  x00", parent=self.I0_2_regs)
        self.I0_3_regs_text = QGraphicsSimpleTextItem("RS1: x00\nRS2: x00\nRD:  x00", parent=self.I0_3_regs)
        self.I0_4_regs_text = QGraphicsSimpleTextItem("RS1: x00\nRS2: x00\nRD:  x00", parent=self.I0_4_regs)
        self.I0_WB_regs_text = QGraphicsSimpleTextItem("RS1: x00\nRS2: x00\nRD:  x00", parent=self.I0_WB_regs)

        # regfile
        regwidth = 110
        regnamewidth = 30
        regheight = 25
        self.regfile = self.scene.addRect(0, 0, 560, 200)

        self.x0_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x1_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x2_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x3_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x4_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x5_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x6_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x7_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x8_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x9_name  = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x10_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x11_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x12_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x13_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x14_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x15_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x16_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x17_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x18_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x19_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x20_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x21_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x22_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x23_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x24_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x25_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x26_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x27_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x28_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x29_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x30_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)
        self.x31_name = QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile)

        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x0",  parent=self.x0_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x1",  parent=self.x1_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x2",  parent=self.x2_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x3",  parent=self.x3_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x4",  parent=self.x4_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x5",  parent=self.x5_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x6",  parent=self.x6_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x7",  parent=self.x7_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x8",  parent=self.x8_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x9",  parent=self.x9_name )) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x10", parent=self.x10_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x11", parent=self.x11_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x12", parent=self.x12_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x13", parent=self.x13_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x14", parent=self.x14_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x15", parent=self.x15_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x16", parent=self.x16_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x17", parent=self.x17_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x18", parent=self.x18_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x19", parent=self.x19_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x20", parent=self.x20_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x21", parent=self.x21_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x22", parent=self.x22_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x23", parent=self.x23_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x24", parent=self.x24_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x25", parent=self.x25_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x26", parent=self.x26_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x27", parent=self.x27_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x28", parent=self.x28_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x29", parent=self.x29_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x30", parent=self.x30_name)) 
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("x31", parent=self.x31_name)) 

        self.x0  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x1  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x2  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x3  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x4  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x5  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x6  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x7  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x8  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x9  = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x10 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x11 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x12 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x13 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x14 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x15 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x16 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x17 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x18 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x19 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x20 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x21 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x22 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x23 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x24 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x25 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x26 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x27 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x28 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x29 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x30 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        self.x31 = QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile)
        
        self.x0_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x0 ) 
        self.x1_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x1 ) 
        self.x2_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x2 ) 
        self.x3_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x3 ) 
        self.x4_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x4 ) 
        self.x5_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x5 ) 
        self.x6_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x6 ) 
        self.x7_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x7 ) 
        self.x8_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x8 ) 
        self.x9_content  = QGraphicsSimpleTextItem("0x00000000", parent=self.x9 ) 
        self.x10_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x10) 
        self.x11_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x11) 
        self.x12_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x12) 
        self.x13_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x13) 
        self.x14_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x14) 
        self.x15_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x15) 
        self.x16_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x16) 
        self.x17_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x17) 
        self.x18_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x18) 
        self.x19_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x19) 
        self.x20_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x20) 
        self.x21_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x21) 
        self.x22_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x22) 
        self.x23_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x23) 
        self.x24_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x24) 
        self.x25_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x25) 
        self.x26_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x26) 
        self.x27_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x27) 
        self.x28_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x28) 
        self.x29_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x29) 
        self.x30_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x30) 
        self.x31_content = QGraphicsSimpleTextItem("0x00000000", parent=self.x31) 

    # position objects relative to their parent objects 
    def _positionObjects(self):
        width = 100
        spacing = 20
        offset = spacing/2

        # IB relative to parent
        self.IB0.setPos(0, 0)
        self.IB1.setPos(0, 25)
        self.IB2.setPos(0, 50)
        self.IB3.setPos(0, 75)
        self.IB0_PC.setPos(30, 0)
        self.IB1_PC.setPos(30, 25)
        self.IB2_PC.setPos(30, 50)
        self.IB3_PC.setPos(30, 75)
        self.IB0_Ins.setPos(30 + width+offset, 0)
        self.IB1_Ins.setPos(30 + width+offset, 25)
        self.IB2_Ins.setPos(30 + width+offset, 50)
        self.IB3_Ins.setPos(30 + width+offset, 75)
        self._centerObjectWithinParent(self.IB0_PC_text)
        self._centerObjectWithinParent(self.IB1_PC_text)
        self._centerObjectWithinParent(self.IB2_PC_text)
        self._centerObjectWithinParent(self.IB3_PC_text)
        self._centerObjectWithinParent(self.IB0_Ins_text)
        self._centerObjectWithinParent(self.IB1_Ins_text)
        self._centerObjectWithinParent(self.IB2_Ins_text)
        self._centerObjectWithinParent(self.IB3_Ins_text)

        self.bypassdebugI0RS1.setPos(0, -80)
        self.bypassdebugI0RS2.setPos(0, -60)
        self.bypassdebugI1RS1.setPos(0, -40)
        self.bypassdebugI1RS2.setPos(0, -20)

        # pipeline relative to parent
        self.flushable_stages.setPos(2*offset+3*width+2*spacing, 0)
        self.flush_lower.setPos(offset+width+spacing, 2*width+3*spacing)
        self.flush_upper.setPos(offset+3*(width+spacing)+width/2, 2*width+3*spacing)

        self.I0_1.setPos(offset+0*(width+spacing), offset)
        self.I0_2.setPos(offset+1*(width+spacing), offset)
        self.I0_3.setPos(offset+2*(width+spacing), offset)
        self.I0_4.setPos(offset+3*(width+spacing), offset)
        self.I0_WB.setPos(offset+4*(width+spacing), offset)

        self._centerObjectWithinParent(self.I0_1_class_text)
        self._centerObjectWithinParent(self.I0_2_class_text)
        self._centerObjectWithinParent(self.I0_3_class_text)
        self._centerObjectWithinParent(self.I0_4_class_text)
        self._centerObjectWithinParent(self.I0_WB_class_text)

        self.I0_1_regs.setPos(0, 20)
        self.I0_2_regs.setPos(0, 20)
        self.I0_3_regs.setPos(0, 20)
        self.I0_4_regs.setPos(0, 20)
        self.I0_WB_regs.setPos(0, 20)
        self._centerObjectWithinParent(self.I0_1_regs_text)
        self._centerObjectWithinParent(self.I0_2_regs_text)
        self._centerObjectWithinParent(self.I0_3_regs_text)
        self._centerObjectWithinParent(self.I0_4_regs_text)
        self._centerObjectWithinParent(self.I0_WB_regs_text)
        
        self.I1_1.setPos(offset+0*(width+spacing), offset+1*(width+spacing))
        self.I1_2.setPos(offset+1*(width+spacing), offset+1*(width+spacing))
        self.I1_3.setPos(offset+2*(width+spacing), offset+1*(width+spacing))
        self.I1_4.setPos(offset+3*(width+spacing), offset+1*(width+spacing))
        self.I1_WB.setPos(offset+4*(width+spacing), offset+1*(width+spacing))
        self._centerObjectWithinParent(self.I1_1_class_text) 
        self._centerObjectWithinParent(self.I1_2_class_text) 
        self._centerObjectWithinParent(self.I1_3_class_text) 
        self._centerObjectWithinParent(self.I1_4_class_text) 
        self._centerObjectWithinParent(self.I1_WB_class_text) 

        # refile
        regwidth = 110
        regheight = 25
        namewidth = 30

        self.x0_name.setPos(0*namewidth+0*regwidth, 0)
        self.x1_name.setPos(1*namewidth+1*regwidth, 0)
        self.x2_name.setPos(2*namewidth+2*regwidth, 0)
        self.x3_name.setPos(3*namewidth+3*regwidth, 0)
        
        self.x4_name.setPos(0*namewidth+0*regwidth, 1*regheight)
        self.x5_name.setPos(1*namewidth+1*regwidth, 1*regheight)
        self.x6_name.setPos(2*namewidth+2*regwidth, 1*regheight)
        self.x7_name.setPos(3*namewidth+3*regwidth, 1*regheight)
        
        self.x8_name.setPos(0*namewidth+0*regwidth,  2*regheight)
        self.x9_name.setPos(1*namewidth+1*regwidth,  2*regheight)
        self.x10_name.setPos(2*namewidth+2*regwidth, 2*regheight)
        self.x11_name.setPos(3*namewidth+3*regwidth, 2*regheight)
        
        self.x12_name.setPos(0*namewidth+0*regwidth, 3*regheight)
        self.x13_name.setPos(1*namewidth+1*regwidth, 3*regheight)
        self.x14_name.setPos(2*namewidth+2*regwidth, 3*regheight)
        self.x15_name.setPos(3*namewidth+3*regwidth, 3*regheight)

        self.x16_name.setPos(0*namewidth+0*regwidth, 4*regheight)
        self.x17_name.setPos(1*namewidth+1*regwidth, 4*regheight)
        self.x18_name.setPos(2*namewidth+2*regwidth, 4*regheight)
        self.x19_name.setPos(3*namewidth+3*regwidth, 4*regheight)
        
        self.x20_name.setPos(0*namewidth+0*regwidth, 5*regheight)
        self.x21_name.setPos(1*namewidth+1*regwidth, 5*regheight)
        self.x22_name.setPos(2*namewidth+2*regwidth, 5*regheight)
        self.x23_name.setPos(3*namewidth+3*regwidth, 5*regheight)

        self.x24_name.setPos(0*namewidth+0*regwidth, 6*regheight)
        self.x25_name.setPos(1*namewidth+1*regwidth, 6*regheight)
        self.x26_name.setPos(2*namewidth+2*regwidth, 6*regheight)
        self.x27_name.setPos(3*namewidth+3*regwidth, 6*regheight)

        self.x28_name.setPos(0*namewidth+0*regwidth, 7*regheight)
        self.x29_name.setPos(1*namewidth+1*regwidth, 7*regheight)
        self.x30_name.setPos(2*namewidth+2*regwidth, 7*regheight)
        self.x31_name.setPos(3*namewidth+3*regwidth, 7*regheight)

        self.x0.setPos(1*namewidth+0*regwidth, 0)
        self.x1.setPos(2*namewidth+1*regwidth, 0)
        self.x2.setPos(3*namewidth+2*regwidth, 0)
        self.x3.setPos(4*namewidth+3*regwidth, 0)
        
        self.x4.setPos(1*namewidth+0*regwidth, 1*regheight)
        self.x5.setPos(2*namewidth+1*regwidth, 1*regheight)
        self.x6.setPos(3*namewidth+2*regwidth, 1*regheight)
        self.x7.setPos(4*namewidth+3*regwidth, 1*regheight)
        
        self.x8.setPos(1*namewidth+0*regwidth,  2*regheight)
        self.x9.setPos(2*namewidth+1*regwidth,  2*regheight)
        self.x10.setPos(3*namewidth+2*regwidth, 2*regheight)
        self.x11.setPos(4*namewidth+3*regwidth, 2*regheight)
        
        self.x12.setPos(1*namewidth+0*regwidth, 3*regheight)
        self.x13.setPos(2*namewidth+1*regwidth, 3*regheight)
        self.x14.setPos(3*namewidth+2*regwidth, 3*regheight)
        self.x15.setPos(4*namewidth+3*regwidth, 3*regheight)

        self.x16.setPos(1*namewidth+0*regwidth, 4*regheight)
        self.x17.setPos(2*namewidth+1*regwidth, 4*regheight)
        self.x18.setPos(3*namewidth+2*regwidth, 4*regheight)
        self.x19.setPos(4*namewidth+3*regwidth, 4*regheight)
        
        self.x20.setPos(1*namewidth+0*regwidth, 5*regheight)
        self.x21.setPos(2*namewidth+1*regwidth, 5*regheight)
        self.x22.setPos(3*namewidth+2*regwidth, 5*regheight)
        self.x23.setPos(4*namewidth+3*regwidth, 5*regheight)

        self.x24.setPos(1*namewidth+0*regwidth, 6*regheight)
        self.x25.setPos(2*namewidth+1*regwidth, 6*regheight)
        self.x26.setPos(3*namewidth+2*regwidth, 6*regheight)
        self.x27.setPos(4*namewidth+3*regwidth, 6*regheight)

        self.x28.setPos(1*namewidth+0*regwidth, 7*regheight)
        self.x29.setPos(2*namewidth+1*regwidth, 7*regheight)
        self.x30.setPos(3*namewidth+2*regwidth, 7*regheight)
        self.x31.setPos(4*namewidth+3*regwidth, 7*regheight)

        self._centerObjectWithinParent(self.x0_content) 
        self._centerObjectWithinParent(self.x1_content) 
        self._centerObjectWithinParent(self.x2_content) 
        self._centerObjectWithinParent(self.x3_content) 
        self._centerObjectWithinParent(self.x4_content) 
        self._centerObjectWithinParent(self.x5_content) 
        self._centerObjectWithinParent(self.x6_content) 
        self._centerObjectWithinParent(self.x7_content) 
        self._centerObjectWithinParent(self.x8_content) 
        self._centerObjectWithinParent(self.x9_content) 
        self._centerObjectWithinParent(self.x10_content)
        self._centerObjectWithinParent(self.x11_content)
        self._centerObjectWithinParent(self.x12_content)
        self._centerObjectWithinParent(self.x13_content)
        self._centerObjectWithinParent(self.x14_content)
        self._centerObjectWithinParent(self.x15_content)
        self._centerObjectWithinParent(self.x16_content)
        self._centerObjectWithinParent(self.x17_content)
        self._centerObjectWithinParent(self.x18_content)
        self._centerObjectWithinParent(self.x19_content)
        self._centerObjectWithinParent(self.x20_content)
        self._centerObjectWithinParent(self.x21_content)
        self._centerObjectWithinParent(self.x22_content)
        self._centerObjectWithinParent(self.x23_content)
        self._centerObjectWithinParent(self.x24_content)
        self._centerObjectWithinParent(self.x25_content)
        self._centerObjectWithinParent(self.x26_content)
        self._centerObjectWithinParent(self.x27_content)
        self._centerObjectWithinParent(self.x28_content)
        self._centerObjectWithinParent(self.x29_content)
        self._centerObjectWithinParent(self.x30_content)
        self._centerObjectWithinParent(self.x31_content)
        
        # positioning of modules
        self.IB_bounding_rect.setPos(0, (width+spacing)/2)
        self.exe_bounding_rect.setPos(2.5*(width + spacing), 0) 
        self.regfile.setPos(0, 300)

    def _getStageClassText(self, valid, alu, load, mul, sec):
        text = "Other"
        if (valid):
            if int(alu):
                text = "ALU"
            elif (load):
                text = "LOAD"
            elif (mul):
                text = "MUL"
            elif (sec):
                text = "SEC"
        return text

    def _toggleArrowVisibilityI0_RS1(self, val):
        if   (val & 0x200):
            self.I1_E1_I0_RS1.show()
        elif (val & 0x100):
            self.I0_E1_I0_RS1.show()
        elif (val & 0x80):
            self.I1_E2_I0_RS1.show()
        elif (val & 0x40):
            self.I0_E2_I0_RS1.show()
        elif (val & 0x20):
            self.I1_E3_I0_RS1.show()
        elif (val & 0x10):
            self.I0_E3_I0_RS1.show()
        elif (val & 0x8):
            self.I1_E4_I0_RS1.show()
        elif (val & 0x4):
            self.I0_E4_I0_RS1.show()
        elif (val & 0x2):
            self.I1_WB_I0_RS1.show()
        elif (val & 0x1):
            self.I0_WB_I0_RS1.show()

    def _toggleArrowVisibilityI0_RS2(self, val):
        if   (val & 0x200):
            self.I1_E1_I0_RS2.show()
        elif (val & 0x100):
            self.I0_E1_I0_RS2.show()
        elif (val & 0x80):
            self.I1_E2_I0_RS2.show()
        elif (val & 0x40):
            self.I0_E2_I0_RS2.show()
        elif (val & 0x20):
            self.I1_E3_I0_RS2.show()
        elif (val & 0x10):
            self.I0_E3_I0_RS2.show()
        elif (val & 0x8):
            self.I1_E4_I0_RS2.show()
        elif (val & 0x4):
            self.I0_E4_I0_RS2.show()
        elif (val & 0x2):
            self.I1_WB_I0_RS2.show()
        elif (val & 0x1):
            self.I0_WB_I0_RS2.show()
    
    def _toggleArrowVisibilityI1_RS1(self, val):
        if   (val & 0x200):
            self.I1_E1_I1_RS1.show()
        elif (val & 0x100):
            self.I0_E1_I1_RS1.show()
        elif (val & 0x80):
            self.I1_E2_I1_RS1.show()
        elif (val & 0x40):
            self.I0_E2_I1_RS1.show()
        elif (val & 0x20):
            self.I1_E3_I1_RS1.show()
        elif (val & 0x10):
            self.I0_E3_I1_RS1.show()
        elif (val & 0x8):
            self.I1_E4_I1_RS1.show()
        elif (val & 0x4):
            self.I0_E4_I1_RS1.show()
        elif (val & 0x2):
            self.I1_WB_I1_RS1.show()
        elif (val & 0x1):
            self.I0_WB_I1_RS1.show()

    def _toggleArrowVisibilityI1_RS2(self, val):
        if   (val & 0x200):
            self.I1_E1_I1_RS2.show()
        elif (val & 0x100):
            self.I0_E1_I1_RS2.show()
        elif (val & 0x80):
            self.I1_E2_I1_RS2.show()
        elif (val & 0x40):
            self.I0_E2_I1_RS2.show()
        elif (val & 0x20):
            self.I1_E3_I1_RS2.show()
        elif (val & 0x10):
            self.I0_E3_I1_RS2.show()
        elif (val & 0x8):
            self.I1_E4_I1_RS2.show()
        elif (val & 0x4):
            self.I0_E4_I1_RS2.show()
        elif (val & 0x2):
            self.I1_WB_I1_RS2.show()
        elif (val & 0x1):
            self.I0_WB_I1_RS2.show()

    # update all object colors, text etc.
    def _updateView(self, values):

        # paint valid instructions green and invalid ones red
        self.IB0.setBrush(self.brush_stage_valid) if (int(values["ibval"], 2) & 1) else self.IB0.setBrush(self.brush_stage_invalid)
        self.IB1.setBrush(self.brush_stage_valid) if (int(values["ibval"], 2) & 2) else self.IB1.setBrush(self.brush_stage_invalid)
        self.IB2.setBrush(self.brush_stage_valid) if (int(values["ibval"], 2) & 4) else self.IB2.setBrush(self.brush_stage_invalid)
        self.IB3.setBrush(self.brush_stage_valid) if (int(values["ibval"], 2) & 8) else self.IB3.setBrush(self.brush_stage_invalid)

        # valid stages are green, invalid stages are red
        self.I0_1.setBrush(self.brush_stage_valid) if (int(values["e1d.i0valid"])) else self.I0_1.setBrush(self.brush_stage_invalid)
        self.I0_2.setBrush(self.brush_stage_valid) if (int(values["e2d.i0valid"])) else self.I0_2.setBrush(self.brush_stage_invalid)
        self.I0_3.setBrush(self.brush_stage_valid) if (int(values["e3d.i0valid"])) else self.I0_3.setBrush(self.brush_stage_invalid)
        self.I0_4.setBrush(self.brush_stage_valid) if (int(values["e4d.i0valid"])) else self.I0_4.setBrush(self.brush_stage_invalid)
        self.I0_WB.setBrush(self.brush_stage_valid) if (int(values["wbd.i0valid"])) else self.I0_WB.setBrush(self.brush_stage_invalid)
        self.I1_1.setBrush(self.brush_stage_valid) if (int(values["e1d.i1valid"])) else self.I1_1.setBrush(self.brush_stage_invalid)
        self.I1_2.setBrush(self.brush_stage_valid) if (int(values["e2d.i1valid"])) else self.I1_2.setBrush(self.brush_stage_invalid)
        self.I1_3.setBrush(self.brush_stage_valid) if (int(values["e3d.i1valid"])) else self.I1_3.setBrush(self.brush_stage_invalid)
        self.I1_4.setBrush(self.brush_stage_valid) if (int(values["e4d.i1valid"])) else self.I1_4.setBrush(self.brush_stage_invalid)
        self.I1_WB.setBrush(self.brush_stage_valid) if (int(values["wbd.i1valid"])) else self.I1_WB.setBrush(self.brush_stage_invalid)

        # color E1-E3 in a light blue if they are frozen
        if (int(values["flush_final_e3"])):
            self.freezable_stages.setBrush(self.brush_flush)
        elif (int(values["freeze"])):
            self.freezable_stages.setBrush(self.brush_freeze)
        else:
            self.freezable_stages.setBrush(QBrush())

        if (int(values["flush_lower_wb"])):
            self.flushable_stages.setBrush(self.brush_flush)
        else:
            self.flushable_stages.setBrush(QBrush())

        # set instruction and PC in IB
        self.IB0_PC_text.setText("PC: " + "{:08X}".format(int(values["dec_i0_pc_d"], 2)))
        self.IB1_PC_text.setText("PC: " + "{:08X}".format(int(values["dec_i1_pc_d"], 2)))
        self.IB2_PC_text.setText("PC: " + "{:08X}".format(int(values["pc2"], 2)))
        self.IB3_PC_text.setText("PC: " + "{:08X}".format(int(values["pc3"], 2)))
        self.IB0_Ins_text.setText("Ins: " + "{:08X}".format(int(values["ib0"], 2)))
        self.IB1_Ins_text.setText("Ins: " + "{:08X}".format(int(values["ib1"], 2)))
        self.IB2_Ins_text.setText("Ins: " + "{:08X}".format(int(values["ib2"], 2)))
        self.IB3_Ins_text.setText("Ins: " + "{:08X}".format(int(values["ib3"], 2)))

        # set class text of all stages
        self.I0_1_class_text.setText(self._getStageClassText(int(values["e1d.i0valid"]), int(values["i0_e1c.alu"]), int(values["i0_e1c.load"]), int(values["i0_e1c.mul"]), int(values["i0_e1c.sec"])))
        self.I0_2_class_text.setText(self._getStageClassText(int(values["e2d.i0valid"]), int(values["i0_e2c.alu"]), int(values["i0_e2c.load"]), int(values["i0_e2c.mul"]), int(values["i0_e2c.sec"])))
        self.I0_3_class_text.setText(self._getStageClassText(int(values["e3d.i0valid"]), int(values["i0_e3c.alu"]), int(values["i0_e3c.load"]), int(values["i0_e3c.mul"]), int(values["i0_e3c.sec"])))
        self.I0_4_class_text.setText(self._getStageClassText(int(values["e4d.i0valid"]), int(values["i0_e4c.alu"]), int(values["i0_e4c.load"]), int(values["i0_e4c.mul"]), int(values["i0_e4c.sec"])))
        self.I0_WB_class_text.setText(self._getStageClassText(int(values["wbd.i0valid"]), int(values["i0_wbc.alu"]), int(values["i0_wbc.load"]), int(values["i0_wbc.mul"]), int(values["i0_wbc.sec"])))

        self.I1_1_class_text.setText(self._getStageClassText(int(values["e1d.i1valid"]), int(values["i1_e1c.alu"]), int(values["i1_e1c.load"]), int(values["i1_e1c.mul"]), int(values["i1_e1c.sec"])))
        self.I1_2_class_text.setText(self._getStageClassText(int(values["e2d.i1valid"]), int(values["i1_e2c.alu"]), int(values["i1_e2c.load"]), int(values["i1_e2c.mul"]), int(values["i1_e2c.sec"])))
        self.I1_3_class_text.setText(self._getStageClassText(int(values["e3d.i1valid"]), int(values["i1_e3c.alu"]), int(values["i1_e3c.load"]), int(values["i1_e3c.mul"]), int(values["i1_e3c.sec"])))
        self.I1_4_class_text.setText(self._getStageClassText(int(values["e4d.i1valid"]), int(values["i1_e4c.alu"]), int(values["i1_e4c.load"]), int(values["i1_e4c.mul"]), int(values["i1_e4c.sec"])))
        self.I1_WB_class_text.setText(self._getStageClassText(int(values["wbd.i1valid"]), int(values["i1_wbc.alu"]), int(values["i1_wbc.load"]), int(values["i1_wbc.mul"]), int(values["i1_wbc.sec"])))

        self._hideAllArrows()
        if (int(values["dec_i0_decode_d"])): self._toggleArrowVisibilityI0_RS1(int(values["i0_rs1bypass"], 2))
        if (int(values["dec_i0_decode_d"])): self._toggleArrowVisibilityI0_RS2(int(values["i0_rs2bypass"], 2))
        if (int(values["dec_i1_decode_d"])): self._toggleArrowVisibilityI1_RS1(int(values["i1_rs1bypass"], 2))
        if (int(values["dec_i1_decode_d"])): self._toggleArrowVisibilityI1_RS2(int(values["i1_rs2bypass"], 2))

        self.bypassdebugI0RS1.setText(values["i0_rs1bypass"])
        self.bypassdebugI0RS2.setText(values["i0_rs2bypass"])
        self.bypassdebugI1RS1.setText(values["i1_rs1bypass"])
        self.bypassdebugI1RS2.setText(values["i1_rs2bypass"])

    def _createCycleLabel(self):
        layout = QHBoxLayout()
        self.cyclelabel = QLabel("Current cycle: ")
        self.generalLayout.addWidget(self.cyclelabel)
        self.progressbar = QProgressBar()
        self.generalLayout.addWidget(self.progressbar)
        layout.addWidget(self.cyclelabel)
        layout.addWidget(self.progressbar)
        self.generalLayout.addLayout(layout)

    #def keyPressEvent(self, event):
    #    self.rect.setPen(QPen(Qt.cyan))
    #    self.rect.setBrush(QBrush(Qt.green))

    def _createButtons(self):
        layout = QGridLayout()

        self.leftbtn = QPushButton('<')
        layout.addWidget(self.leftbtn, 0, 0)
        
        self.rightbtn = QPushButton('>')
        layout.addWidget(self.rightbtn, 0, 1)

        self.generalLayout.addLayout(layout)

    def _createGraphicsView(self):
        self.scene = QGraphicsScene()
        self.graphicsview = QGraphicsView(self.scene)
        self.generalLayout.addWidget(self.graphicsview)
    
    def setCycleLabel(self, cycle):
        self.cyclelabel.setText("Current cycle: {:5d}".format(cycle))

# ===[ Controller Class ]==================================
class SweRVisualCtrl():
    def __init__(self, view, vcdhandler):
        self._view = view
        self._vcdhandler = vcdhandler
        self._view.setCycleLabel(0)
        self.connectSignals()
        
        # arrow key controls
        QShortcut(QKeySequence(Qt.Key_Left),  self._view, activated=self.leftbtn_click)
        QShortcut(QKeySequence(Qt.Key_Right), self._view, activated=self.rightbtn_click)
    
    def leftbtn_click(self):
        if (self._vcdhandler.cycle - self._vcdhandler.step_size < 5):
            self._vcdhandler.cycle = 5
        else:
            self._vcdhandler.cycle = self._vcdhandler.cycle - self._vcdhandler.step_size
        self._view.setCycleLabel(self._vcdhandler.cycle)
        self._view.progressbar.setValue(int(100 * (self._vcdhandler.cycle / self._vcdhandler.final_time)))
        self.updateView()

    def rightbtn_click(self):
        if (self._vcdhandler.cycle + self._vcdhandler.step_size > self._vcdhandler.final_time):
            self._vcdhandler.cycle = self._vcdhandler.final_time
        else:
            self._vcdhandler.cycle = self._vcdhandler.cycle + self._vcdhandler.step_size
        self._view.setCycleLabel(self._vcdhandler.cycle)
        self._view.progressbar.setValue(int(100 * (self._vcdhandler.cycle / self._vcdhandler.final_time)))
        self.updateView()

    def connectSignals(self):
        self._view.leftbtn.clicked.connect(self.leftbtn_click)
        self._view.rightbtn.clicked.connect(self.rightbtn_click)

    # get correct data from VCD file
    def updateView(self):
        # signals we want to parse from the VCD file
        signals = {
            #IB
            "ib0"         : SWERV_DEC_IB + "ib0[31:0]",
            "ib1"         : SWERV_DEC_IB + "ib1[31:0]",
            "ib2"         : SWERV_DEC_IB + "ib2[31:0]",
            "ib3"         : SWERV_DEC_IB + "ib3[31:0]",
            "shift0"      : SWERV_DEC_IB + "shift0",
            "shift1"      : SWERV_DEC_IB + "shift1",
            "shift2"      : SWERV_DEC_IB + "shift2",
            "ibval"       : SWERV_DEC_IB + "ibval[3:0]",
            "dec_i0_pc_d" : SWERV_DEC_IB + "dec_i0_pc_d[31:1]",
            "dec_i1_pc_d" : SWERV_DEC_IB + "dec_i1_pc_d[31:1]",
            "pc2"         : SWERV_DEC_IB + "pc2[36:0]",
            "pc3"         : SWERV_DEC_IB + "pc3[36:0]",

            # Decode Ctrl
            "dec_i0_decode_d" : SWERV_DEC_DECODE + "dec_i0_decode_d",
            "dec_i1_decode_d" : SWERV_DEC_DECODE + "dec_i1_decode_d",
            "freeze"          : SWERV_DEC_DECODE + "freeze",
            "flush_final_e3"  : SWERV_DEC_DECODE + "flush_final_e3",
            "flush_lower_wb"  : SWERV_DEC_DECODE + "flush_lower_wb",

            "i0_inst_e1" : SWERV_DEC_DECODE + "i0_inst_e1[31:0]",
            "i0_inst_e2" : SWERV_DEC_DECODE + "i0_inst_e2[31:0]",
            "i0_inst_e3" : SWERV_DEC_DECODE + "i0_inst_e3[31:0]",
            "i0_inst_e4" : SWERV_DEC_DECODE + "i0_inst_e4[31:0]",
            "i0_inst_wb" : SWERV_DEC_DECODE + "i0_inst_wb[31:0]",
            "i0_inst_wb1" : SWERV_DEC_DECODE + "i0_inst_wb1[31:0]",
            
            "i1_inst_e1" : SWERV_DEC_DECODE + "i1_inst_e1[31:0]",
            "i1_inst_e2" : SWERV_DEC_DECODE + "i1_inst_e2[31:0]",
            "i1_inst_e3" : SWERV_DEC_DECODE + "i1_inst_e3[31:0]",
            "i1_inst_e4" : SWERV_DEC_DECODE + "i1_inst_e4[31:0]",
            "i1_inst_wb" : SWERV_DEC_DECODE + "i1_inst_wb[31:0]",
            "i1_inst_wb1" : SWERV_DEC_DECODE + "i1_inst_wb1[31:0]",
            
            "i0_pc_e1" : SWERV_DEC_DECODE + "i0_pc_e1[31:1]",
            "i0_pc_e2" : SWERV_DEC_DECODE + "i0_pc_e2[31:1]",
            "i0_pc_e3" : SWERV_DEC_DECODE + "i0_pc_e3[31:1]",
            "i0_pc_e4" : SWERV_DEC_DECODE + "i0_pc_e4[31:1]",
            "i0_pc_wb" : SWERV_DEC_DECODE + "i0_pc_wb[31:1]",
            "i0_pc_wb1" : SWERV_DEC_DECODE + "i0_pc_wb1[31:1]",

            "i1_pc_e1" : SWERV_DEC_DECODE + "i1_pc_e1[31:1]",
            "i1_pc_e2" : SWERV_DEC_DECODE + "i1_pc_e2[31:1]",
            "i1_pc_e3" : SWERV_DEC_DECODE + "i1_pc_e3[31:1]",
            "i1_pc_e4" : SWERV_DEC_DECODE + "i1_pc_e4[31:1]",
            "i1_pc_wb" : SWERV_DEC_DECODE + "i1_pc_wb[31:1]",
            "i1_pc_wb1" : SWERV_DEC_DECODE + "i1_pc_wb1[31:1]",

            "i0_dc.alu" : SWERV_DEC_DECODE + "i0_dc.alu",
            "i0_dc.load" : SWERV_DEC_DECODE + "i0_dc.load",
            "i0_dc.mul" : SWERV_DEC_DECODE + "i0_dc.mul",
            "i0_dc.sec" : SWERV_DEC_DECODE + "i0_dc.sec",

            "i0_e1c.alu" : SWERV_DEC_DECODE + "i0_e1c.alu",
            "i0_e1c.load" : SWERV_DEC_DECODE + "i0_e1c.load",
            "i0_e1c.mul" : SWERV_DEC_DECODE + "i0_e1c.mul",
            "i0_e1c.sec" : SWERV_DEC_DECODE + "i0_e1c.sec",
            
            "i0_e2c.alu" : SWERV_DEC_DECODE + "i0_e2c.alu",
            "i0_e2c.load" : SWERV_DEC_DECODE + "i0_e2c.load",
            "i0_e2c.mul" : SWERV_DEC_DECODE + "i0_e2c.mul",
            "i0_e2c.sec" : SWERV_DEC_DECODE + "i0_e2c.sec",
            
            "i0_e3c.alu" : SWERV_DEC_DECODE + "i0_e3c.alu",
            "i0_e3c.load" : SWERV_DEC_DECODE + "i0_e3c.load",
            "i0_e3c.mul" : SWERV_DEC_DECODE + "i0_e3c.mul",
            "i0_e3c.sec" : SWERV_DEC_DECODE + "i0_e3c.sec",
            
            "i0_e4c.alu" : SWERV_DEC_DECODE + "i0_e4c.alu",
            "i0_e4c.load" : SWERV_DEC_DECODE + "i0_e4c.load",
            "i0_e4c.mul" : SWERV_DEC_DECODE + "i0_e4c.mul",
            "i0_e4c.sec" : SWERV_DEC_DECODE + "i0_e4c.sec",
            
            "i0_wbc.alu" : SWERV_DEC_DECODE + "i0_wbc.alu",
            "i0_wbc.load" : SWERV_DEC_DECODE + "i0_wbc.load",
            "i0_wbc.mul" : SWERV_DEC_DECODE + "i0_wbc.mul",
            "i0_wbc.sec" : SWERV_DEC_DECODE + "i0_wbc.sec",

            "i1_dc.alu" : SWERV_DEC_DECODE + "i1_dc.alu",
            "i1_dc.load" : SWERV_DEC_DECODE + "i1_dc.load",
            "i1_dc.mul" : SWERV_DEC_DECODE + "i1_dc.mul",
            "i1_dc.sec" : SWERV_DEC_DECODE + "i1_dc.sec",

            "i1_e1c.alu" : SWERV_DEC_DECODE + "i1_e1c.alu",
            "i1_e1c.load" : SWERV_DEC_DECODE + "i1_e1c.load",
            "i1_e1c.mul" : SWERV_DEC_DECODE + "i1_e1c.mul",
            "i1_e1c.sec" : SWERV_DEC_DECODE + "i1_e1c.sec",
            
            "i1_e2c.alu" : SWERV_DEC_DECODE + "i1_e2c.alu",
            "i1_e2c.load" : SWERV_DEC_DECODE + "i1_e2c.load",
            "i1_e2c.mul" : SWERV_DEC_DECODE + "i1_e2c.mul",
            "i1_e2c.sec" : SWERV_DEC_DECODE + "i1_e2c.sec",
            
            "i1_e3c.alu" : SWERV_DEC_DECODE + "i1_e3c.alu",
            "i1_e3c.load" : SWERV_DEC_DECODE + "i1_e3c.load",
            "i1_e3c.mul" : SWERV_DEC_DECODE + "i1_e3c.mul",
            "i1_e3c.sec" : SWERV_DEC_DECODE + "i1_e3c.sec",
            
            "i1_e4c.alu" : SWERV_DEC_DECODE + "i1_e4c.alu",
            "i1_e4c.load" : SWERV_DEC_DECODE + "i1_e4c.load",
            "i1_e4c.mul" : SWERV_DEC_DECODE + "i1_e4c.mul",
            "i1_e4c.sec" : SWERV_DEC_DECODE + "i1_e4c.sec",
            
            "i1_wbc.alu" : SWERV_DEC_DECODE + "i1_wbc.alu",
            "i1_wbc.load" : SWERV_DEC_DECODE + "i1_wbc.load",
            "i1_wbc.mul" : SWERV_DEC_DECODE + "i1_wbc.mul",
            "i1_wbc.sec" : SWERV_DEC_DECODE + "i1_wbc.sec",

            "e1d.i0valid" : SWERV_DEC_DECODE + "e1d.i0valid",
            "e2d.i0valid" : SWERV_DEC_DECODE + "e2d.i0valid",
            "e3d.i0valid" : SWERV_DEC_DECODE + "e3d.i0valid",
            "e4d.i0valid" : SWERV_DEC_DECODE + "e4d.i0valid",
            "wbd.i0valid" : SWERV_DEC_DECODE + "wbd.i0valid",
            
            "e1d.i1valid" : SWERV_DEC_DECODE + "e1d.i1valid",
            "e2d.i1valid" : SWERV_DEC_DECODE + "e2d.i1valid",
            "e3d.i1valid" : SWERV_DEC_DECODE + "e3d.i1valid",
            "e4d.i1valid" : SWERV_DEC_DECODE + "e4d.i1valid",
            "wbd.i1valid" : SWERV_DEC_DECODE + "wbd.i1valid",

            "i0_rs1bypass" : SWERV_DEC_DECODE + "i0_rs1bypass[9:0]",
            "i0_rs2bypass" : SWERV_DEC_DECODE + "i0_rs2bypass[9:0]",
            "i1_rs1bypass" : SWERV_DEC_DECODE + "i1_rs1bypass[9:0]",
            "i1_rs2bypass" : SWERV_DEC_DECODE + "i1_rs2bypass[9:0]",
        }
        values = {}
        for key in signals:
            values[key] = self._vcdhandler.getSignalValue(signals[key], self._vcdhandler.cycle)

        self._view._updateView(values)

# ===[ VCD Handler Class ]=================================
class VCDHandler():
    def __init__(self, file):
        self.step_size = 10
        self.cycle = 5
        self.vcd_file = VCDVCD(file)
        self.clk_signal = self.vcd_file[SWERV_TOP + "clk"]
        self.final_time = self.clk_signal.tv[-1][0]

    def getSignalValue(self, signal_name, time):
        return self.vcd_file[signal_name][time]


# ===[ Main Function ]=====================================
if __name__ == '__main__':
    if (len(sys.argv) <= 1 or os.path.exists(sys.argv[1]) != True):
        print("Usage: swervisual.py <vcd file path>")
        exit(-1)
   
    vcdhandler = VCDHandler(sys.argv[1])
    swervisual = QApplication(sys.argv)
    view = SweRVisual()
    view.show()
    ctrl = SweRVisualCtrl(view=view, vcdhandler=vcdhandler)
    sys.exit(swervisual.exec_())
