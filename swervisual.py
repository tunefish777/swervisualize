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
import re

# constants
SWERV_TOP        = "TOP.tb_top.rvtop.swerv."
SWERV_DEC_DECODE = SWERV_TOP + "dec.decode."
SWERV_DEC_IB     = SWERV_TOP + "dec.instbuff."
SWERV_GPR        = SWERV_TOP + "dec.arf.gpr_banks[0]."
SWERV_EXU        = SWERV_TOP + "exu."
SWERV_TLU        = SWERV_TOP + "dec.tlu."

# ===[ GUI Class ]=========================================
class SweRVisual(QMainWindow):
    def __init__(self):
        super().__init__()
        self.width   = 120
        self.height  = 100
        self.spacing = 20
        self.offset  = 10
        self.setWindowTitle("SweRVisualize")
        self.setGeometry(200, 200, 1400, 800)
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
        self._addGPRArrows()
        self._hideAllArrows()
        self._positionObjects()

    # define brushes etc.
    def _setupDrawing(self):
        self.brush_neutral = QBrush()

        self.brush_stage_valid = QBrush(QColor(0x71, 0xff, 0x7d))
        self.brush_stage_valid_i1 = QBrush(QColor(0x10, 0xbf, 0x7d))
        self.brush_stage_invalid = QBrush(QColor(0xff, 0x5b, 0x62))

        self.brush_copy = QBrush(Qt.yellow)

        self.brush_gpr_rs1 = QBrush(QColor(Qt.cyan))
        self.brush_gpr_rs2 = QBrush(QColor(Qt.magenta))

        self.pen_wb_i0 = QPen(QColor(0x71, 0xff, 0x7d), 3, Qt.DotLine)
        self.pen_wb_i1 = QPen(QColor(0x10, 0xbf, 0x7d), 3, Qt.DotLine)
        self.pen_arrow_wb_i0 = QPen(QColor(0x71, 0xff, 0x7d), Qt.SolidLine)
        self.pen_arrow_wb_i1 = QPen(QColor(0x10, 0xbf, 0x7d), Qt.SolidLine)

        self.brush_freeze = QBrush(QColor(0x25, 0xb4, 0xda))
        self.brush_flush = QBrush(Qt.black)

        self.pen_line_rs1 = QPen(Qt.cyan, 3, Qt.DotLine)
        self.pen_arrow_rs1 = QPen(Qt.cyan, 1, Qt.SolidLine)
        self.brush_arrow_head_rs1 = QBrush(Qt.cyan)

        self.pen_line_rs2 = QPen(Qt.magenta, 3, Qt.DotLine)
        self.pen_arrow_rs2 = QPen(Qt.magenta, 1, Qt.SolidLine)
        self.brush_arrow_head_rs2 = QBrush(Qt.magenta)
        
        self.pen_line_commit = QPen(QColor(0x71, 0xff, 0x7d), 2, Qt.SolidLine)
        self.brush_line_commit = QBrush(QColor(0x71, 0xff, 0x7d))

        self.pen_dotted_outline = QPen(Qt.black, 1, Qt.DotLine)

    # center object within its parents bounding rect
    def _centerObjectWithinParent(self, obj):
        x_offset = (obj.parentItem().boundingRect().width() - obj.boundingRect().width()) / 2
        y_offset = (obj.parentItem().boundingRect().height() - obj.boundingRect().height()) / 2
        obj.setPos(x_offset, y_offset)

    def _leftAlignObjectWithinParent(self, obj):
        x_offset = self.offset
        y_offset = (obj.parentItem().boundingRect().height() - obj.boundingRect().height()) / 2
        obj.setPos(x_offset, y_offset)

    def _addGPRArrows(self):
        width = self.width
        height = self.height
        offset = self.offset
        spacing = self.spacing

        i0_rs1_height = (offset+height/2)-offset
        i0_rs2_height = (offset+height/2)+offset

        i1_rs1_height = (offset+1.5*height+2*spacing)-offset
        i1_rs2_height = (offset+1.5*height+2*spacing)+offset

        # GPR -> I0 RS1
        self.I0_RS1_GPR = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=25, angle=180)
        arrow.setPos(0, i0_rs1_height)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)
        line = QGraphicsLineItem(-45, i0_rs1_height, -45, 350+offset+spacing*4, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(-45, 350+offset+spacing*4, 0, 350+offset+spacing*4, parent=self.exe_bounding_rect)
        line.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        self.I0_RS1_GPR.addToGroup(line)
        self.I0_RS1_GPR.addToGroup(line2)
        self.I0_RS1_GPR.addToGroup(arrow)
        
        # GPR -> I0 RS2
        self.I0_RS2_GPR = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=20, angle=180)
        arrow.setPos(0, i0_rs2_height)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)
        line = QGraphicsLineItem(-40, i0_rs2_height, -40, 350+offset+spacing*3, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(-40, 350+offset+spacing*3, 0, 350+offset+spacing*3, parent=self.exe_bounding_rect)
        line.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        self.I0_RS2_GPR.addToGroup(line)
        self.I0_RS2_GPR.addToGroup(line2)
        self.I0_RS2_GPR.addToGroup(arrow)
        
        # GPR -> I1 RS1
        self.I1_RS1_GPR = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=10, angle=180)
        arrow.setPos(0, i1_rs1_height)
        arrow.setPen(self.pen_arrow_rs1)
        arrow.setBrush(self.brush_arrow_head_rs1)
        line = QGraphicsLineItem(-30, i1_rs1_height, -30, 350+offset+spacing*2, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(-30, 350+offset+spacing*2, 0, 350+offset+spacing*2, parent=self.exe_bounding_rect)
        line.setPen(self.pen_line_rs1)
        line2.setPen(self.pen_line_rs1)
        self.I1_RS1_GPR.addToGroup(line)
        self.I1_RS1_GPR.addToGroup(line2)
        self.I1_RS1_GPR.addToGroup(arrow)
        
        # GPR -> I1 RS2
        self.I1_RS2_GPR = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=5, angle=180)
        arrow.setPos(0, i1_rs2_height)
        arrow.setPen(self.pen_arrow_rs2)
        arrow.setBrush(self.brush_arrow_head_rs2)
        line = QGraphicsLineItem(-25, i1_rs2_height, -25, 350+offset+spacing*1, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(-25, 350+offset+spacing*1, 0, 350+offset+spacing*1, parent=self.exe_bounding_rect)
        line.setPen(self.pen_line_rs2)
        line2.setPen(self.pen_line_rs2)
        self.I1_RS2_GPR.addToGroup(line)
        self.I1_RS2_GPR.addToGroup(line2)
        self.I1_RS2_GPR.addToGroup(arrow)

        # I0 WB -> GPR
        self.I0_WB_GPR = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=0, angle=0)
        arrow.setPos(self.exe_bounding_rect.boundingRect().width()-width-spacing, self.exe_bounding_rect.boundingRect().height()+height+2*spacing)
        arrow.setPen(self.pen_arrow_wb_i0)
        arrow.setBrush(self.brush_stage_valid)
        line  = QGraphicsLineItem(self.exe_bounding_rect.boundingRect().width(), offset+height/2, self.exe_bounding_rect.boundingRect().width()+spacing, offset+height/2, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(self.exe_bounding_rect.boundingRect().width()+spacing, offset+height/2, self.exe_bounding_rect.boundingRect().width()+spacing, self.exe_bounding_rect.boundingRect().height()+height+2*spacing, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(self.exe_bounding_rect.boundingRect().width()+spacing, self.exe_bounding_rect.boundingRect().height()+height+2*spacing, self.exe_bounding_rect.boundingRect().width()-width, self.exe_bounding_rect.boundingRect().height()+height+2*spacing, parent=self.exe_bounding_rect)
        line.setPen(self.pen_wb_i0)
        line2.setPen(self.pen_wb_i0)
        line3.setPen(self.pen_wb_i0)
        self.I0_WB_GPR.addToGroup(line)
        self.I0_WB_GPR.addToGroup(line2)
        self.I0_WB_GPR.addToGroup(line3)
        self.I0_WB_GPR.addToGroup(arrow)
        
        # I1 WB -> GPR
        self.I1_WB_GPR = QGraphicsItemGroup(parent=self.exe_bounding_rect)
        arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=20, tailLen=0, angle=0)
        arrow.setPos(self.exe_bounding_rect.boundingRect().width()-width-spacing, self.exe_bounding_rect.boundingRect().height()+height+1*spacing)
        arrow.setPen(self.pen_arrow_wb_i1)
        arrow.setBrush(self.brush_stage_valid_i1)
        line  = QGraphicsLineItem(self.exe_bounding_rect.boundingRect().width(), offset+2*spacing+1.5*height, self.exe_bounding_rect.boundingRect().width()+offset, offset+2*spacing+1.5*height, parent=self.exe_bounding_rect)
        line2 = QGraphicsLineItem(self.exe_bounding_rect.boundingRect().width()+offset, offset+2*spacing+1.5*height, self.exe_bounding_rect.boundingRect().width()+offset, self.exe_bounding_rect.boundingRect().height()+height+spacing, parent=self.exe_bounding_rect)
        line3 = QGraphicsLineItem(self.exe_bounding_rect.boundingRect().width()+offset, self.exe_bounding_rect.boundingRect().height()+height+spacing, self.exe_bounding_rect.boundingRect().width()-width, self.exe_bounding_rect.boundingRect().height()+height+spacing, parent=self.exe_bounding_rect)
        line.setPen(self.pen_wb_i1)
        line2.setPen(self.pen_wb_i1)
        line3.setPen(self.pen_wb_i1)
        self.I1_WB_GPR.addToGroup(line)
        self.I1_WB_GPR.addToGroup(line2)
        self.I1_WB_GPR.addToGroup(line3)
        self.I1_WB_GPR.addToGroup(arrow)


    def _addForwardingArrows(self):
        width   = self.width
        height  = self.height
        spacing = self.spacing
        offset  = self.offset

        i0_rs1_height = (offset+height/2)-offset
        i0_rs2_height = (offset+height/2)+offset

        i1_rs1_height = (offset+1.5*height+2*spacing)-offset
        i1_rs2_height = (offset+1.5*height+2*spacing)+offset

        # i0 stages -> i0 RS1
        self.I0_RS1_From_I0 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=offset, angle=180)
            arrow.setPos(0, i0_rs1_height)
            arrow.setPen(self.pen_arrow_rs1)
            arrow.setBrush(self.brush_arrow_head_rs1)
            line1 = QGraphicsLineItem(           start_x, (offset+height/2) - spacing, start_x + offset/2, (offset+height/2) - spacing, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(start_x + offset/2, (offset+height/2) - spacing, start_x + offset/2,                     -offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(start_x + offset/2,                     -offset,  -spacing - offset,                     -offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem( -spacing - offset,                     -offset,  -spacing - offset,               i0_rs1_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs1)
            line2.setPen(self.pen_line_rs1)
            line3.setPen(self.pen_line_rs1)
            line4.setPen(self.pen_line_rs1)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I0_RS1_From_I0.append(group)
        
        # i0 stages -> i0 RS2
        self.I0_RS2_From_I0 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=1.5*offset, angle=180)
            arrow.setPos(0, i0_rs2_height)
            arrow.setPen(self.pen_arrow_rs2)
            arrow.setBrush(self.brush_arrow_head_rs2)
            line1 = QGraphicsLineItem(              start_x, (offset+height/2) - offset,    start_x + offset, (offset+height/2) - offset, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(     start_x + offset, (offset+height/2) - offset,    start_x + offset,                -1.5*offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(     start_x + offset,                -1.5*offset, -spacing-1.5*offset,                -1.5*offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem(-spacing - 1.5*offset,                -1.5*offset, -spacing-1.5*offset,              i0_rs2_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs2)
            line2.setPen(self.pen_line_rs2)
            line3.setPen(self.pen_line_rs2)
            line4.setPen(self.pen_line_rs2)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I0_RS2_From_I0.append(group)

        # i0 stages -> i1 RS1
        self.I1_RS1_From_I0 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=offset, angle=180)
            arrow.setPos(0, i1_rs1_height)
            arrow.setPen(self.pen_arrow_rs1)
            arrow.setBrush(self.brush_arrow_head_rs1)
            line1 = QGraphicsLineItem(         start_x, (offset+height/2) + offset, start_x + offset, (offset+height/2) + offset, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(start_x + offset, (offset+height/2) + offset, start_x + offset,   (offset+height) + offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(start_x + offset,   (offset+height) + offset,  -spacing-offset,   (offset+height) + offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem( -spacing-offset,   (offset+height) + offset,  -spacing-offset,              i1_rs1_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs1)
            line2.setPen(self.pen_line_rs1)
            line3.setPen(self.pen_line_rs1)
            line4.setPen(self.pen_line_rs1)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I1_RS1_From_I0.append(group)
        
        # i0 stages -> i1 RS2
        self.I1_RS2_From_I0 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=1.5*offset, angle=180)
            arrow.setPos(0, i1_rs2_height)
            arrow.setPen(self.pen_arrow_rs2)
            arrow.setBrush(self.brush_arrow_head_rs2)
            line1 = QGraphicsLineItem(            start_x,  (offset+height/2) + spacing,  start_x + offset/2,  (offset+height/2) + spacing, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem( start_x + offset/2,  (offset+height/2) + spacing,  start_x + offset/2, (offset+height) + 0.5*offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem( start_x + offset/2, (offset+height) + 0.5*offset, -spacing-1.5*offset, (offset+height) + 0.5*offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem(-spacing-1.5*offset, (offset+height) + 0.5*offset, -spacing-1.5*offset,                i1_rs2_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs2)
            line2.setPen(self.pen_line_rs2)
            line3.setPen(self.pen_line_rs2)
            line4.setPen(self.pen_line_rs2)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I1_RS2_From_I0.append(group)

        #----------------------------------------------
        # i1 stages -> i1 RS1
        self.I1_RS1_From_I1 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            middle_y = offset + height + 2*spacing + height/2
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=offset, angle=180)
            arrow.setPos(0, i1_rs1_height)
            arrow.setPen(self.pen_arrow_rs1)
            arrow.setBrush(self.brush_arrow_head_rs1)
            line1 = QGraphicsLineItem(            start_x,                middle_y + offset,    start_x + offset,                middle_y + offset, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(   start_x + offset,                middle_y + offset,    start_x + offset, middle_y + height/2 + 2.5*offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(   start_x + offset, middle_y + height/2 + 2.5*offset, -spacing-1.5*offset, middle_y + height/2 + 2.5*offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem(-spacing-1.5*offset, middle_y + height/2 + 2.5*offset, -spacing-1.5*offset,                    i1_rs1_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs1)
            line2.setPen(self.pen_line_rs1)
            line3.setPen(self.pen_line_rs1)
            line4.setPen(self.pen_line_rs1)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I1_RS1_From_I1.append(group)
        
        # i1 stages -> i1 RS2
        self.I1_RS2_From_I1 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            middle_y = offset + height + 2*spacing + height/2
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=offset, angle=180)
            arrow.setPos(0, i1_rs2_height)
            arrow.setPen(self.pen_arrow_rs2)
            arrow.setBrush(self.brush_arrow_head_rs2)
            line1 = QGraphicsLineItem(           start_x,             middle_y + spacing, start_x + offset/2,             middle_y + spacing, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(start_x + offset/2,             middle_y + spacing, start_x + offset/2, middle_y + height/2 + 2*offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(start_x + offset/2, middle_y + height/2 + 2*offset,    -spacing-offset, middle_y + height/2 + 2*offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem(   -spacing-offset, middle_y + height/2 + 2*offset,    -spacing-offset,                  i1_rs2_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs2)
            line2.setPen(self.pen_line_rs2)
            line3.setPen(self.pen_line_rs2)
            line4.setPen(self.pen_line_rs2)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I1_RS2_From_I1.append(group)
        
        # i1 stages -> i0 RS1
        self.I0_RS1_From_I1 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            middle_y = offset + height + 2*spacing + height/2
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=1.5*offset, angle=180)
            arrow.setPos(0, i0_rs1_height)
            arrow.setPen(self.pen_arrow_rs1)
            arrow.setBrush(self.brush_arrow_head_rs1)
            line1 = QGraphicsLineItem(start_x, middle_y - spacing, start_x + offset/2, middle_y - spacing, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(start_x + offset/2, middle_y - spacing, start_x + offset/2, middle_y - height/2 - 0.5*offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(start_x + offset/2, middle_y - height/2 - 0.5*offset, -spacing-1.5*offset, middle_y - height/2 - 0.5*offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem(-spacing-1.5*offset, middle_y - height/2 - 0.5*offset, -spacing-1.5*offset, i0_rs1_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs1)
            line2.setPen(self.pen_line_rs1)
            line3.setPen(self.pen_line_rs1)
            line4.setPen(self.pen_line_rs1)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I0_RS1_From_I1.append(group)
        
        # i1 stages -> i0 RS2
        self.I0_RS2_From_I1 = []
        for i in range(5):
            start_x = (width+offset) + i*(width+spacing)
            middle_y = offset + height + 2*spacing + height/2
            group = QGraphicsItemGroup(parent=self.exe_bounding_rect)
            arrow = ArrowItem(parent=self.exe_bounding_rect, headLen=spacing, tailLen=offset, angle=180)
            arrow.setPos(0, i0_rs2_height)
            arrow.setPen(self.pen_arrow_rs2)
            arrow.setBrush(self.brush_arrow_head_rs2)
            line1 = QGraphicsLineItem(start_x, middle_y - offset, start_x + offset, middle_y - offset, parent=self.exe_bounding_rect)
            line2 = QGraphicsLineItem(start_x + offset, middle_y - offset, start_x + offset, middle_y - height/2 - offset, parent=self.exe_bounding_rect)
            line3 = QGraphicsLineItem(start_x + offset, middle_y - height/2 - offset, -spacing-offset, middle_y - height/2 - offset, parent=self.exe_bounding_rect)
            line4 = QGraphicsLineItem(-spacing-offset, middle_y - height/2 - offset, -spacing-offset, i0_rs2_height, parent=self.exe_bounding_rect)
            line1.setPen(self.pen_line_rs2)
            line2.setPen(self.pen_line_rs2)
            line3.setPen(self.pen_line_rs2)
            line4.setPen(self.pen_line_rs2)
            group.addToGroup(line1)
            group.addToGroup(line2)
            group.addToGroup(line3)
            group.addToGroup(line4)
            group.addToGroup(arrow)
            self.I0_RS2_From_I1.append(group)

    def _hideAllArrows(self):
        # hide all arrows by default
        self.I0_RS1_GPR.hide()
        self.I0_RS2_GPR.hide()
        self.I1_RS1_GPR.hide()
        self.I1_RS2_GPR.hide()
        self.I0_WB_GPR.hide()
        self.I1_WB_GPR.hide()

        for i in range(5):
            self.I0_RS1_From_I0[i].hide() 
            self.I0_RS2_From_I0[i].hide() 
            self.I0_RS1_From_I1[i].hide()
            self.I0_RS2_From_I1[i].hide()
            self.I1_RS1_From_I0[i].hide() 
            self.I1_RS2_From_I0[i].hide() 
            self.I1_RS1_From_I1[i].hide()
            self.I1_RS2_From_I1[i].hide()

    # adding all objects to the scene without positioning (Order matters! newest object has biggest z val)
    def _addObjectsToScene(self):
        
        width = self.width
        height = self.height
        spacing = self.spacing
        offset = self.offset

        # IB 
        self.IB_bounding_rect = self.scene.addRect(0, 0, 3.5*width, height)
        
        self.bypassdebugI0RS1 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)
        self.bypassdebugI0RS2 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)
        self.bypassdebugI1RS1 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)
        self.bypassdebugI1RS2 = QGraphicsSimpleTextItem("", parent=self.IB_bounding_rect)

        self.IB_valid_box = []
        self.IB_PC_box = []
        self.IB_instr_box = []
        self.IB_PC_text = []
        self.IB_instr_text = []
        self.IB_copy_box = []
        self.IB_copy_text = []
        for i in range(4):
            self.IB_valid_box.append(QGraphicsRectItem(0, 0, 30, height/4, parent=self.IB_bounding_rect))
            self._centerObjectWithinParent(QGraphicsSimpleTextItem("IB{}".format(i), parent=self.IB_valid_box[i]))
            self.IB_copy_box.append(QGraphicsRectItem(0, 0, 30, height/4, parent=self.IB_bounding_rect))
            self._centerObjectWithinParent(QGraphicsSimpleTextItem("C", parent=self.IB_copy_box[i]))
            self.IB_PC_box.append(QGraphicsRectItem(0, 0, width, height/4, parent=self.IB_bounding_rect))
            self.IB_instr_box.append(QGraphicsRectItem(0, 0, 2*width, height/4, parent=self.IB_bounding_rect))
            self.IB_PC_text.append(QGraphicsSimpleTextItem("PC: 00000000", parent=self.IB_PC_box[i]))
            self.IB_instr_text.append(QGraphicsSimpleTextItem("???", parent=self.IB_instr_box[i]))

        self.CSR_rect = self.scene.addRect(0, 0, width, height)
        self.CSRs = {}
        self.CSRs["faultless"] = QGraphicsRectItem(0, 0, width, height/4, parent=self.CSR_rect)
        self._centerObjectWithinParent(QGraphicsSimpleTextItem("faultless", parent=self.CSRs["faultless"]))

        # stalling lines
        self.stall_i0 = self.scene.addLine(550, offset, 550, offset+height, QPen(Qt.red, 3, Qt.DotLine))
        self.stall_i1 = self.scene.addLine(550, offset+height+2*spacing, 550, offset+2*height+2*spacing, QPen(Qt.red, 3, Qt.DotLine))
        self.stall_i0.hide()
        self.stall_i1.hide()

        # pipeline stages
        self.exe_bounding_rect = self.scene.addRect(0, 0, 5*(width+spacing), 2*(height+spacing)+spacing)

        self.freezable_stages = QGraphicsRectItem(0, 0, 2*offset+3*width+2*spacing, 2*offset+2*height+2*spacing, parent=self.exe_bounding_rect)
        self.flushable_stages = QGraphicsRectItem(0, 0, 2*offset+2*width+spacing, 2*offset+2*height+2*spacing, parent=self.exe_bounding_rect)
        self.freezable_stages.setPen(self.pen_dotted_outline)
        self.flushable_stages.setPen(self.pen_dotted_outline)

        self.I0_stages = []
        self.I0_class = []
        self.I0_info = []
        self.I0_class_text = []
        self.I0_info_text = []
        self.I0_copy = []
        self.I0_copy_text = []
        for i in range(5):
            self.I0_stages.append(QGraphicsRectItem(0, 0, width, height, parent=self.exe_bounding_rect))
            self.I0_class.append(QGraphicsRectItem(0, 0, width, 20, parent=self.I0_stages[i]))
            self.I0_info.append(QGraphicsRectItem(0, 0, width, 60, parent=self.I0_stages[i]))
            self.I0_copy.append(QGraphicsRectItem(0, 0, width, 20, parent=self.I0_stages[i]))
            self.I0_copy_text.append(QGraphicsSimpleTextItem("Copy", parent=self.I0_copy[i]))
            self.I0_class_text.append(QGraphicsSimpleTextItem("I0 class", parent=self.I0_class[i]))
            self.I0_info_text.append(QGraphicsSimpleTextItem("Instr: ???\nPC: ???\nRD:  x00", parent=self.I0_info[i]))

        self.I1_stages = []
        self.I1_class = []
        self.I1_info = []
        self.I1_class_text = []
        self.I1_info_text = []
        self.I1_copy = []
        self.I1_copy_text = []
        for i in range(5):
            self.I1_stages.append(QGraphicsRectItem(0, 0, width, height, parent=self.exe_bounding_rect))
            self.I1_class.append(QGraphicsRectItem(0, 0, width, 20, parent=self.I1_stages[i]))
            self.I1_info.append(QGraphicsRectItem(0, 0, width, 60, parent=self.I1_stages[i]))
            self.I1_copy.append(QGraphicsRectItem(0, 0, width, 20, parent=self.I1_stages[i]))
            self.I1_copy_text.append(QGraphicsSimpleTextItem("Copy", parent=self.I1_copy[i]))
            self.I1_class_text.append(QGraphicsSimpleTextItem("I0 class", parent=self.I1_class[i]))
            self.I1_info_text.append(QGraphicsSimpleTextItem("Instr: ???\nPC: ???\nRD:  x00", parent=self.I1_info[i]))

        # regfile
        regwidth = 110
        regnamewidth = 30
        regheight = 25
        self.regfile = self.scene.addRect(0, 0, 560, 200)

        # regs
        self.regs = []
        self.regs_text = []
        self.reg_names = []
        self.reg_name_text = []
        for i in range(32):
            self.regs.append(QGraphicsRectItem(0, 0, regwidth, regheight, parent=self.regfile))
            self.regs_text.append(QGraphicsSimpleTextItem("0x00000000", parent=self.regs[i] ))
            self.reg_names.append(QGraphicsRectItem(0, 0, regnamewidth, regheight, parent=self.regfile))
            self.reg_name_text.append(QGraphicsSimpleTextItem("x{}".format(i),  parent=self.reg_names[i]))

        # nonblocking load commit
        self.nonblock_load_commit = QGraphicsItemGroup(parent=self.regfile)
        nbl_commit_rect = QGraphicsRectItem(0, 0, regwidth, regheight)
        nbl_commit_rect.setBrush(self.brush_stage_valid)
        self.nonblock_load_commit.addToGroup(nbl_commit_rect)
        arrow = ArrowItem(parent=self.nonblock_load_commit, headLen=20, tailLen=10, angle=0)
        arrow.setPos(-30, regheight/2)
        arrow.setPen(self.pen_line_commit)
        arrow.setBrush(self.brush_line_commit)
        self.nonblock_load_commit.addToGroup(arrow)
        self.nonblock_load_commit_text = QGraphicsSimpleTextItem("NBL Commit", parent=nbl_commit_rect)
        self._centerObjectWithinParent(self.nonblock_load_commit_text)

    # position objects relative to their parent objects 
    def _positionObjects(self):
        width = self.width
        height = self.height
        spacing = self.spacing
        offset = self.offset

        # IB relative to parent
        for i in range(4):
            self.IB_valid_box[i].setPos(0, i*(height/4))
            self.IB_copy_box[i].setPos(30, i*(height/4))
            self.IB_PC_box[i].setPos(60, i*(height/4))
            self.IB_instr_box[i].setPos(60+width, i*(height/4))
            self._centerObjectWithinParent(self.IB_PC_text[i])
            self._leftAlignObjectWithinParent(self.IB_instr_text[i])

        self.bypassdebugI0RS1.setPos(0, -80)
        self.bypassdebugI0RS2.setPos(0, -60)
        self.bypassdebugI1RS1.setPos(0, -40)
        self.bypassdebugI1RS2.setPos(0, -20)

        # pipeline relative to parent
        self.flushable_stages.setPos(2*offset+3*width+2*spacing, 0)
        #self.flush_lower.setPos(offset+width+spacing, 2*width+3*spacing)
        #self.flush_upper.setPos(offset+3*(width+spacing)+width/2, 2*width+3*spacing)

        for i in range(5):
            self.I0_stages[i].setPos(offset+i*(width+spacing), offset)
            self._centerObjectWithinParent(self.I0_class_text[i])
            self.I0_info[i].setPos(0, 20)
            self._leftAlignObjectWithinParent(self.I0_info_text[i])
            self.I0_copy[i].setPos(0, 80)
            self._centerObjectWithinParent(self.I0_copy_text[i])

        for i in range(5):
            self.I1_stages[i].setPos(offset+i*(width+spacing), offset+height+2*spacing)
            self._centerObjectWithinParent(self.I1_class_text[i])
            self.I1_info[i].setPos(0, 20)
            self._leftAlignObjectWithinParent(self.I1_info_text[i])
            self.I1_copy[i].setPos(0, 80)
            self._centerObjectWithinParent(self.I1_copy_text[i])

        # refile
        regwidth = 110
        regheight = 25
        namewidth = 30

        for i in range(8):
            for j in range(4):
                self.reg_names[4*i+j].setPos(j*namewidth+j*regwidth, i*regheight)
                self.regs[4*i+j].setPos((j+1)*namewidth+j*regwidth, i*regheight)
                self._centerObjectWithinParent(self.regs_text[4*i+j])
                self._centerObjectWithinParent(self.reg_name_text[4*i+j])

        self.nonblock_load_commit.setPos(self.regfile.boundingRect().width() + 30, self.regfile.boundingRect().height()/2 - regheight/2)
        
        # positioning of modules
        self.IB_bounding_rect.setPos(0, 0)#(width+spacing)/2)
        self.CSR_rect.setPos(0, 2*height)
        self.exe_bounding_rect.setPos(4*(width + spacing), 0) 
        self.regfile.setPos(4*(width+spacing), 350)

    def _getStageClassText(self, values, stage, pipe):
        text = "Other"
        valid_name = stage + "d." + pipe + "valid"

        alu_name   = "{}_{}c.alu".format(pipe, stage)
        load_name  = "{}_{}c.load".format(pipe, stage) 
        mul_name   = "{}_{}c.mul".format(pipe, stage)
        sec_name   = "{}_{}c.sec".format(pipe, stage)
        if (int(values[valid_name])):
            if int(values[alu_name]) or int(values[sec_name]):
                if (stage == "e5"):
                    if int(values[alu_name]):
                        text = "ALU" 
                    else:
                        text = "SEC"
                elif int(values["{}_{}_beq".format(pipe, stage)]):
                    text = "BEQ"
                elif int(values["{}_{}_bge".format(pipe, stage)]):
                    text = "BGE"
                elif int(values["{}_{}_blt".format(pipe, stage)]):
                    text = "BLT"
                elif int(values["{}_{}_bne".format(pipe, stage)]):
                    text = "BNE"
                elif int(values["{}_{}_jal".format(pipe, stage)]):
                    text = "JAL"
                else:
                    if int(values[alu_name]):
                        text = "ALU" 
                    else:
                        text = "SEC"
            elif int(values[load_name]):
                text = "LOAD"
            elif int(values[mul_name]):
                text = "MUL"
        return text

    def _toggleArrowVisibilityI0_RS1(self, val):
        for i in range(10):
            if ((val >> (9-i)) & 1):
                if (i % 2): 
                    self.I0_RS1_From_I0[int(i/2)].show()
                else:
                    self.I0_RS1_From_I1[int(i/2)].show()

    def _toggleArrowVisibilityI0_RS2(self, val):
        for i in range(10):
            if ((val >> (9-i)) & 1):
                if (i % 2): 
                    self.I0_RS2_From_I0[int(i/2)].show()
                else:
                    self.I0_RS2_From_I1[int(i/2)].show()

    def _toggleArrowVisibilityI1_RS1(self, val):
        for i in range(10):
            if ((val >> (9-i)) & 1):
                if (i % 2): 
                    self.I1_RS1_From_I0[int(i/2)].show()
                else:
                    self.I1_RS1_From_I1[int(i/2)].show()

    def _toggleArrowVisibilityI1_RS2(self, val):
        for i in range(10):
            if ((val >> (9-i)) & 1):
                if (i % 2): 
                    self.I1_RS2_From_I0[int(i/2)].show()
                else:
                    self.I1_RS2_From_I1[int(i/2)].show()


    def _colorRegs(self, values):
        for i in range(1,32):
            self.regs[i].setBrush(self.brush_neutral) 
            if (int(values["dec_i0_decode_d"])):
                # I0 RS1
                if not int(values["i0_rs1_bypass_en"]) and int(values["i0_rs1_en_d"]):
                    if (int(values["i0_rs1"], 2) == i):
                        self.regs[i].setBrush(self.brush_gpr_rs1)
                        self.I0_RS1_GPR.show()
                # I0 RS2
                elif not int(values["i0_rs2_bypass_en"]) and int(values["i0_rs2_en_d"]):
                    if (int(values["i0_rs2"], 2) == i):
                        self.regs[i].setBrush(self.brush_gpr_rs2)
                        self.I0_RS2_GPR.show()
            if (int(values["dec_i1_decode_d"])):
                # I1 RS1
                if not int(values["i1_rs1_bypass_en"]) and int(values["i1_rs1_en_d"]):
                    if (int(values["i1_rs1"], 2) == i):
                        self.regs[i].setBrush(self.brush_gpr_rs1)
                        self.I1_RS1_GPR.show()
                # I1 RS2
                elif not int(values["i1_rs2_bypass_en"]) and int(values["i1_rs2_en_d"]):
                    if (int(values["i1_rs2"], 2) == i):
                        self.regs[i].setBrush(self.brush_gpr_rs2)
                        self.I1_RS2_GPR.show()
            # WB
            if int(values["x{}_en".format(i)]):
                if (int(values["i0_wen_wb"]) and int(values["e5_i0_rd"], 2) == i):
                    self.regs[i].setBrush(self.brush_stage_valid)
                    self.I0_WB_GPR.show()
                elif (int(values["i1_wen_wb"]) and int(values["e5_i1_rd"], 2) == i):
                    self.regs[i].setBrush(self.brush_stage_valid_i1)
                    self.I1_WB_GPR.show()

    def _truncateInstructionText(self, text, max_len):
        if (len(text) > max_len):
            return text[0:max_len] + "..."
        else:
            return text

    # update all object colors, text etc.
    def _updateView(self, values, instructions):

        # paint valid instructions green and invalid ones red
        for i in range(4):
            self.IB_valid_box[i].setBrush(self.brush_stage_valid) if ((int(values["ibval"], 2) >> i) & 1) else self.IB_valid_box[i].setBrush(self.brush_stage_invalid)
            self.IB_copy_box[i].setBrush(self.brush_copy) if (int(values["ic{}".format(i)])) else self.IB_copy_box[i].setBrush(self.brush_neutral)

        # valid stages are green, invalid stages are red
        for i in range(5):
            self.I0_stages[i].setBrush(self.brush_stage_valid) if (int(values["e{}d.i0valid".format(i+1)])) else self.I0_stages[i].setBrush(self.brush_stage_invalid)
            self.I1_stages[i].setBrush(self.brush_stage_valid_i1) if (int(values["e{}d.i1valid".format(i+1)])) else self.I1_stages[i].setBrush(self.brush_stage_invalid)

        # stalling lines
        self.stall_i0.hide()
        self.stall_i1.hide()
        if (int(values["dec_i0_decode_d"]) == 0): self.stall_i0.show()
        if (int(values["dec_i1_decode_d"]) == 0): self.stall_i1.show()

        # color E1-E3 in a light blue if they are frozen
        if (int(values["flush_final_e3"])):
            self.freezable_stages.setBrush(self.brush_flush)
        elif (int(values["freeze"])):
            self.freezable_stages.setBrush(self.brush_freeze)
        else:
            self.freezable_stages.setBrush(self.brush_neutral)

        if (int(values["flush_lower_wb"])):
            self.flushable_stages.setBrush(self.brush_flush)
        else:
            self.flushable_stages.setBrush(self.brush_neutral)

        # set instruction and PC in IB
        self.IB_PC_text[0].setText("PC: "+ "{:08X}".format(int(values["dec_i0_pc_d"]+"0", 2)))
        self.IB_PC_text[1].setText("PC: "+ "{:08X}".format(int(values["dec_i1_pc_d"]+"0", 2)))
        self.IB_PC_text[2].setText("PC: "+ "{:08X}".format(int(values["pc2"]+"0", 2)))
        self.IB_PC_text[3].setText("PC: "+ "{:08X}".format(int(values["pc3"]+"0", 2)))
        
        self.IB_instr_text[0].setText(self._truncateInstructionText(assembly._getInstruction("{:08x}".format(int(values["dec_i0_pc_d"]+"0", 2))), 25))
        self.IB_instr_text[1].setText(self._truncateInstructionText(assembly._getInstruction("{:08x}".format(int(values["dec_i1_pc_d"]+"0", 2))), 25))
        self.IB_instr_text[2].setText(self._truncateInstructionText(assembly._getInstruction("{:08x}".format(int(values["pc2"]+"0", 2))), 25))
        self.IB_instr_text[3].setText(self._truncateInstructionText(assembly._getInstruction("{:08x}".format(int(values["pc3"]+"0", 2))), 25))

        # set class text of all stages

        for i in range(5):
            self.I0_class_text[i].setText(self._getStageClassText(values, "e{}".format(i+1), "i0"))
            self.I1_class_text[i].setText(self._getStageClassText(values, "e{}".format(i+1), "i1"))
            self.I0_info_text[i].setText("Instr: {}\nPC: {:08X}\nRD: x{}".format(assembly._getInstruction("{:08x}".format(int(values["i0_pc_e{}".format(i+1)]+"0", 2))).split(' ')[0], int(values["i0_pc_e{}".format(i+1)]+"0", 2), int(values["e{}_i0_rd".format(i+1)], 2)))
            self.I1_info_text[i].setText("Instr: {}\nPC: {:08X}\nRD: x{}".format(assembly._getInstruction("{:08x}".format(int(values["i1_pc_e{}".format(i+1)]+"0", 2))).split(' ')[0], int(values["i1_pc_e{}".format(i+1)]+"0", 2), int(values["e{}_i1_rd".format(i+1)], 2)))
            self.I0_copy_text[i].hide()
            self.I0_copy[i].setBrush(self.brush_copy) if (int(values["i0_e{}_copy".format(i+1)])) else self.I0_copy[i].setBrush(self.brush_neutral)
            self.I1_copy_text[i].hide()
            self.I1_copy[i].setBrush(self.brush_copy) if (int(values["i1_e{}_copy".format(i+1)])) else self.I1_copy[i].setBrush(self.brush_neutral)

        self.nonblock_load_commit.hide()
        if (int(values["nonblock_load_wen"])): self.nonblock_load_commit.show()

        self.CSRs["faultless"].setBrush(self.brush_copy) if (int(values["faultless"])) else self.CSRs["faultless"].setBrush(self.brush_neutral)

        self._hideAllArrows()
        if (int(values["dec_i0_decode_d"])): self._toggleArrowVisibilityI0_RS1(int(values["i0_rs1bypass"], 2))
        if (int(values["dec_i0_decode_d"])): self._toggleArrowVisibilityI0_RS2(int(values["i0_rs2bypass"], 2))
        if (int(values["dec_i1_decode_d"])): self._toggleArrowVisibilityI1_RS1(int(values["i1_rs1bypass"], 2))
        if (int(values["dec_i1_decode_d"])): self._toggleArrowVisibilityI1_RS2(int(values["i1_rs2bypass"], 2))

        # GPR values
        for i in range(1,32):
            self.regs_text[i].setText("0x{:08X}".format(int(values["x{}".format(i)], 2)))

        self._colorRegs(values)

        #self.bypassdebugI0RS1.setText(values["i0_rs1bypass"])
        #self.bypassdebugI0RS2.setText(values["i0_rs2bypass"])
        #self.bypassdebugI1RS1.setText(values["i1_rs1bypass"])
        #self.bypassdebugI1RS2.setText(values["i1_rs2bypass"])

    def _createCycleLabel(self):
        layout = QHBoxLayout()
        self.cyclelabel = QLabel("Current cycle: ")
        self.generalLayout.addWidget(self.cyclelabel)
        self.progressbar = QProgressBar()
        self.generalLayout.addWidget(self.progressbar)
        layout.addWidget(self.cyclelabel)
        layout.addWidget(self.progressbar)
        self.generalLayout.addLayout(layout)

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
    def __init__(self, view, vcdhandler, disas_handler):
        self._view = view
        self._vcdhandler = vcdhandler
        self._disas_handler = disas_handler
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
            "ic0"         : SWERV_DEC_IB + "ic0",
            "ic1"         : SWERV_DEC_IB + "ic1",
            "ic2"         : SWERV_DEC_IB + "ic2",
            "ic3"         : SWERV_DEC_IB + "ic3",

            # GPRs
            "i0_rs1_en_d" : SWERV_DEC_DECODE + "dec_i0_rs1_en_d", 
            "i0_rs2_en_d" : SWERV_DEC_DECODE + "dec_i0_rs2_en_d", 
            "i1_rs1_en_d" : SWERV_DEC_DECODE + "dec_i1_rs1_en_d", 
            "i1_rs2_en_d" : SWERV_DEC_DECODE + "dec_i1_rs2_en_d", 

            "i0_rs1"      : SWERV_DEC_DECODE + "i0r.rs1[4:0]",
            "i0_rs2"      : SWERV_DEC_DECODE + "i0r.rs2[4:0]",
            "i1_rs1"      : SWERV_DEC_DECODE + "i1r.rs1[4:0]",
            "i1_rs2"      : SWERV_DEC_DECODE + "i1r.rs2[4:0]",

            "x1"          : SWERV_GPR + "gpr[1].gprff.dout[31:0]",
            "x2"          : SWERV_GPR + "gpr[2].gprff.dout[31:0]",
            "x3"          : SWERV_GPR + "gpr[3].gprff.dout[31:0]",
            "x4"          : SWERV_GPR + "gpr[4].gprff.dout[31:0]",
            "x5"          : SWERV_GPR + "gpr[5].gprff.dout[31:0]",
            "x6"          : SWERV_GPR + "gpr[6].gprff.dout[31:0]",
            "x7"          : SWERV_GPR + "gpr[7].gprff.dout[31:0]",
            "x8"          : SWERV_GPR + "gpr[8].gprff.dout[31:0]",
            "x9"          : SWERV_GPR + "gpr[9].gprff.dout[31:0]",
            "x10"         : SWERV_GPR + "gpr[10].gprff.dout[31:0]",
            "x11"         : SWERV_GPR + "gpr[11].gprff.dout[31:0]",
            "x12"         : SWERV_GPR + "gpr[12].gprff.dout[31:0]",
            "x13"         : SWERV_GPR + "gpr[13].gprff.dout[31:0]",
            "x14"         : SWERV_GPR + "gpr[14].gprff.dout[31:0]",
            "x15"         : SWERV_GPR + "gpr[15].gprff.dout[31:0]",
            "x16"         : SWERV_GPR + "gpr[16].gprff.dout[31:0]",
            "x17"         : SWERV_GPR + "gpr[17].gprff.dout[31:0]",
            "x18"         : SWERV_GPR + "gpr[18].gprff.dout[31:0]",
            "x19"         : SWERV_GPR + "gpr[19].gprff.dout[31:0]",
            "x20"         : SWERV_GPR + "gpr[20].gprff.dout[31:0]",
            "x21"         : SWERV_GPR + "gpr[21].gprff.dout[31:0]",
            "x22"         : SWERV_GPR + "gpr[22].gprff.dout[31:0]",
            "x23"         : SWERV_GPR + "gpr[23].gprff.dout[31:0]",
            "x24"         : SWERV_GPR + "gpr[24].gprff.dout[31:0]",
            "x25"         : SWERV_GPR + "gpr[25].gprff.dout[31:0]",
            "x26"         : SWERV_GPR + "gpr[26].gprff.dout[31:0]",
            "x27"         : SWERV_GPR + "gpr[27].gprff.dout[31:0]",
            "x28"         : SWERV_GPR + "gpr[28].gprff.dout[31:0]",
            "x29"         : SWERV_GPR + "gpr[29].gprff.dout[31:0]",
            "x30"         : SWERV_GPR + "gpr[30].gprff.dout[31:0]",
            "x31"         : SWERV_GPR + "gpr[31].gprff.dout[31:0]",

            "x1_en"          : SWERV_GPR + "gpr[1].gprff.en",
            "x2_en"          : SWERV_GPR + "gpr[2].gprff.en",
            "x3_en"          : SWERV_GPR + "gpr[3].gprff.en",
            "x4_en"          : SWERV_GPR + "gpr[4].gprff.en",
            "x5_en"          : SWERV_GPR + "gpr[5].gprff.en",
            "x6_en"          : SWERV_GPR + "gpr[6].gprff.en",
            "x7_en"          : SWERV_GPR + "gpr[7].gprff.en",
            "x8_en"          : SWERV_GPR + "gpr[8].gprff.en",
            "x9_en"          : SWERV_GPR + "gpr[9].gprff.en",
            "x10_en"         : SWERV_GPR + "gpr[10].gprff.en",
            "x11_en"         : SWERV_GPR + "gpr[11].gprff.en",
            "x12_en"         : SWERV_GPR + "gpr[12].gprff.en",
            "x13_en"         : SWERV_GPR + "gpr[13].gprff.en",
            "x14_en"         : SWERV_GPR + "gpr[14].gprff.en",
            "x15_en"         : SWERV_GPR + "gpr[15].gprff.en",
            "x16_en"         : SWERV_GPR + "gpr[16].gprff.en",
            "x17_en"         : SWERV_GPR + "gpr[17].gprff.en",
            "x18_en"         : SWERV_GPR + "gpr[18].gprff.en",
            "x19_en"         : SWERV_GPR + "gpr[19].gprff.en",
            "x20_en"         : SWERV_GPR + "gpr[20].gprff.en",
            "x21_en"         : SWERV_GPR + "gpr[21].gprff.en",
            "x22_en"         : SWERV_GPR + "gpr[22].gprff.en",
            "x23_en"         : SWERV_GPR + "gpr[23].gprff.en",
            "x24_en"         : SWERV_GPR + "gpr[24].gprff.en",
            "x25_en"         : SWERV_GPR + "gpr[25].gprff.en",
            "x26_en"         : SWERV_GPR + "gpr[26].gprff.en",
            "x27_en"         : SWERV_GPR + "gpr[27].gprff.en",
            "x28_en"         : SWERV_GPR + "gpr[28].gprff.en",
            "x29_en"         : SWERV_GPR + "gpr[29].gprff.en",
            "x30_en"         : SWERV_GPR + "gpr[30].gprff.en",
            "x31_en"         : SWERV_GPR + "gpr[31].gprff.en",

            # Decode Ctrl
            "dec_i0_decode_d" : SWERV_DEC_DECODE + "dec_i0_decode_d",
            "dec_i1_decode_d" : SWERV_DEC_DECODE + "dec_i1_decode_d",
            "freeze"          : SWERV_DEC_DECODE + "freeze",
            "flush_final_e3"  : SWERV_DEC_DECODE + "flush_final_e3",
            "flush_lower_wb"  : SWERV_DEC_DECODE + "flush_lower_wb",
            "nonblock_load_wen" : SWERV_DEC_DECODE + "dec_nonblock_load_wen",
            "i0_rs1_bypass_en"  : SWERV_DEC_DECODE + "dec_i0_rs1_bypass_en_d",
            "i0_rs2_bypass_en"  : SWERV_DEC_DECODE + "dec_i0_rs2_bypass_en_d",
            "i1_rs1_bypass_en"  : SWERV_DEC_DECODE + "dec_i1_rs1_bypass_en_d",
            "i1_rs2_bypass_en"  : SWERV_DEC_DECODE + "dec_i1_rs2_bypass_en_d",
            "i0_dp.imm20"       : SWERV_DEC_DECODE + "i0_dp.imm20",
            "i0_dp.imm12"       : SWERV_DEC_DECODE + "i0_dp.imm12",
            "i1_dp.imm20"       : SWERV_DEC_DECODE + "i1_dp.imm20",
            "i1_dp.imm12"       : SWERV_DEC_DECODE + "i1_dp.imm12",
            "i0_select_pc_d" : SWERV_DEC_DECODE + "dec_i0_select_pc_d",
            "i1_select_pc_d" : SWERV_DEC_DECODE + "dec_i1_select_pc_d",
            "i0_alu_decode_d" : SWERV_DEC_DECODE + "dec_i0_alu_decode_d",
            "i1_alu_decode_d" : SWERV_DEC_DECODE + "dec_i1_alu_decode_d",
            "i0_mul_d"    : SWERV_DEC_DECODE + "dec_i0_mul_d",
            "i1_mul_d"    : SWERV_DEC_DECODE + "dec_i1_mul_d",
            "i0_lsu_d"    : SWERV_DEC_DECODE + "dec_i0_mul_d",
            "i1_lsu_d"    : SWERV_DEC_DECODE + "dec_i1_mul_d",
            "i0_div_d"    : SWERV_DEC_DECODE + "dec_i0_div_d",
            "i1_div_d"    : SWERV_DEC_DECODE + "dec_i1_div_d",
            "load_mul_rs1_bypass_e1" : SWERV_DEC_DECODE + "load_mul_rs1_bypass_e1",
            "load_mul_rs2_bypass_e1" : SWERV_DEC_DECODE + "load_mul_rs2_bypass_e1",
            "i0_wen_wb" : SWERV_DEC_DECODE + "i0_wen_wb",
            "i1_wen_wb" : SWERV_DEC_DECODE + "i1_wen_wb",

            "i0_inst_e1" : SWERV_DEC_DECODE + "i0_inst_e1[31:0]",
            "i0_inst_e2" : SWERV_DEC_DECODE + "i0_inst_e2[31:0]",
            "i0_inst_e3" : SWERV_DEC_DECODE + "i0_inst_e3[31:0]",
            "i0_inst_e4" : SWERV_DEC_DECODE + "i0_inst_e4[31:0]",
            "i0_inst_e5" : SWERV_DEC_DECODE + "i0_inst_wb[31:0]",
            "i0_inst_wb1" : SWERV_DEC_DECODE + "i0_inst_wb1[31:0]",
            
            "i1_inst_e1" : SWERV_DEC_DECODE + "i1_inst_e1[31:0]",
            "i1_inst_e2" : SWERV_DEC_DECODE + "i1_inst_e2[31:0]",
            "i1_inst_e3" : SWERV_DEC_DECODE + "i1_inst_e3[31:0]",
            "i1_inst_e4" : SWERV_DEC_DECODE + "i1_inst_e4[31:0]",
            "i1_inst_e5" : SWERV_DEC_DECODE + "i1_inst_wb[31:0]",
            "i1_inst_wb1" : SWERV_DEC_DECODE + "i1_inst_wb1[31:0]",
            
            "i0_pc_e1" : SWERV_DEC_DECODE + "i0_pc_e1[31:1]",
            "i0_pc_e2" : SWERV_DEC_DECODE + "i0_pc_e2[31:1]",
            "i0_pc_e3" : SWERV_DEC_DECODE + "i0_pc_e3[31:1]",
            "i0_pc_e4" : SWERV_DEC_DECODE + "i0_pc_e4[31:1]",
            "i0_pc_e5" : SWERV_DEC_DECODE + "i0_pc_wb[31:1]",

            "i1_pc_e1" : SWERV_DEC_DECODE + "i1_pc_e1[31:1]",
            "i1_pc_e2" : SWERV_DEC_DECODE + "i1_pc_e2[31:1]",
            "i1_pc_e3" : SWERV_DEC_DECODE + "i1_pc_e3[31:1]",
            "i1_pc_e4" : SWERV_DEC_DECODE + "i1_pc_e4[31:1]",
            "i1_pc_e5" : SWERV_DEC_DECODE + "i1_pc_wb[31:1]",

            "i0_e1_copy" : SWERV_DEC_DECODE + "i0_e1_copy",
            "i0_e2_copy" : SWERV_DEC_DECODE + "i0_e2_copy",
            "i0_e3_copy" : SWERV_DEC_DECODE + "i0_e3_copy",
            "i0_e4_copy" : SWERV_DEC_DECODE + "i0_e4_copy",
            "i0_e5_copy" : SWERV_DEC_DECODE + "i0_wb_copy",
            
            "i1_e1_copy" : SWERV_DEC_DECODE + "i1_e1_copy",
            "i1_e2_copy" : SWERV_DEC_DECODE + "i1_e2_copy",
            "i1_e3_copy" : SWERV_DEC_DECODE + "i1_e3_copy",
            "i1_e4_copy" : SWERV_DEC_DECODE + "i1_e4_copy",
            "i1_e5_copy" : SWERV_DEC_DECODE + "i1_wb_copy",

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
            
            "i0_e5c.alu" : SWERV_DEC_DECODE + "i0_wbc.alu",
            "i0_e5c.load" : SWERV_DEC_DECODE + "i0_wbc.load",
            "i0_e5c.mul" : SWERV_DEC_DECODE + "i0_wbc.mul",
            "i0_e5c.sec" : SWERV_DEC_DECODE + "i0_wbc.sec",

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
            
            "i1_e5c.alu" : SWERV_DEC_DECODE + "i1_wbc.alu",
            "i1_e5c.load" : SWERV_DEC_DECODE + "i1_wbc.load",
            "i1_e5c.mul" : SWERV_DEC_DECODE + "i1_wbc.mul",
            "i1_e5c.sec" : SWERV_DEC_DECODE + "i1_wbc.sec",

            "e1d.i0valid" : SWERV_DEC_DECODE + "e1d.i0valid",
            "e2d.i0valid" : SWERV_DEC_DECODE + "e2d.i0valid",
            "e3d.i0valid" : SWERV_DEC_DECODE + "e3d.i0valid",
            "e4d.i0valid" : SWERV_DEC_DECODE + "e4d.i0valid",
            "e5d.i0valid" : SWERV_DEC_DECODE + "wbd.i0valid",
            
            "e1d.i1valid" : SWERV_DEC_DECODE + "e1d.i1valid",
            "e2d.i1valid" : SWERV_DEC_DECODE + "e2d.i1valid",
            "e3d.i1valid" : SWERV_DEC_DECODE + "e3d.i1valid",
            "e4d.i1valid" : SWERV_DEC_DECODE + "e4d.i1valid",
            "e5d.i1valid" : SWERV_DEC_DECODE + "wbd.i1valid",

            "i0_rs1bypass" : SWERV_DEC_DECODE + "i0_rs1bypass[9:0]",
            "i0_rs2bypass" : SWERV_DEC_DECODE + "i0_rs2bypass[9:0]",
            "i1_rs1bypass" : SWERV_DEC_DECODE + "i1_rs1bypass[9:0]",
            "i1_rs2bypass" : SWERV_DEC_DECODE + "i1_rs2bypass[9:0]",

            "e1_i0_rd"     : SWERV_DEC_DECODE + "e1d.i0rd[4:0]",
            "e2_i0_rd"     : SWERV_DEC_DECODE + "e2d.i0rd[4:0]",
            "e3_i0_rd"     : SWERV_DEC_DECODE + "e3d.i0rd[4:0]",
            "e4_i0_rd"     : SWERV_DEC_DECODE + "e4d.i0rd[4:0]",
            "e5_i0_rd"     : SWERV_DEC_DECODE + "wbd.i0rd[4:0]",
        
            "e1_i1_rd"     : SWERV_DEC_DECODE + "e1d.i1rd[4:0]",
            "e2_i1_rd"     : SWERV_DEC_DECODE + "e2d.i1rd[4:0]",
            "e3_i1_rd"     : SWERV_DEC_DECODE + "e3d.i1rd[4:0]",
            "e4_i1_rd"     : SWERV_DEC_DECODE + "e4d.i1rd[4:0]",
            "e5_i1_rd"     : SWERV_DEC_DECODE + "wbd.i1rd[4:0]",
            
            # EXU

            # alu types
            "i0_e1_beq"     : SWERV_EXU + "i0_ap_e1.beq",
            "i0_e1_bge"     : SWERV_EXU + "i0_ap_e1.bge",
            "i0_e1_blt"     : SWERV_EXU + "i0_ap_e1.blt",
            "i0_e1_bne"     : SWERV_EXU + "i0_ap_e1.bne",
            "i0_e1_jal"     : SWERV_EXU + "i0_ap_e1.jal",

            "i0_e2_beq"     : SWERV_EXU + "i0_ap_e2.beq",
            "i0_e2_bge"     : SWERV_EXU + "i0_ap_e2.bge",
            "i0_e2_blt"     : SWERV_EXU + "i0_ap_e2.blt",
            "i0_e2_bne"     : SWERV_EXU + "i0_ap_e2.bne",
            "i0_e2_jal"     : SWERV_EXU + "i0_ap_e2.jal",

            "i0_e3_beq"     : SWERV_EXU + "i0_ap_e3.beq",
            "i0_e3_bge"     : SWERV_EXU + "i0_ap_e3.bge",
            "i0_e3_blt"     : SWERV_EXU + "i0_ap_e3.blt",
            "i0_e3_bne"     : SWERV_EXU + "i0_ap_e3.bne",
            "i0_e3_jal"     : SWERV_EXU + "i0_ap_e3.jal",

            "i0_e4_beq"     : SWERV_EXU + "i0_ap_e4.beq",
            "i0_e4_bge"     : SWERV_EXU + "i0_ap_e4.bge",
            "i0_e4_blt"     : SWERV_EXU + "i0_ap_e4.blt",
            "i0_e4_bne"     : SWERV_EXU + "i0_ap_e4.bne",
            "i0_e4_jal"     : SWERV_EXU + "i0_ap_e4.jal",

            "i1_e1_beq"     : SWERV_EXU + "i1_ap_e1.beq",
            "i1_e1_bge"     : SWERV_EXU + "i1_ap_e1.bge",
            "i1_e1_blt"     : SWERV_EXU + "i1_ap_e1.blt",
            "i1_e1_bne"     : SWERV_EXU + "i1_ap_e1.bne",
            "i1_e1_jal"     : SWERV_EXU + "i1_ap_e1.jal",

            "i1_e2_beq"     : SWERV_EXU + "i1_ap_e2.beq",
            "i1_e2_bge"     : SWERV_EXU + "i1_ap_e2.bge",
            "i1_e2_blt"     : SWERV_EXU + "i1_ap_e2.blt",
            "i1_e2_bne"     : SWERV_EXU + "i1_ap_e2.bne",
            "i1_e2_jal"     : SWERV_EXU + "i1_ap_e2.jal",

            "i1_e3_beq"     : SWERV_EXU + "i1_ap_e3.beq",
            "i1_e3_bge"     : SWERV_EXU + "i1_ap_e3.bge",
            "i1_e3_blt"     : SWERV_EXU + "i1_ap_e3.blt",
            "i1_e3_bne"     : SWERV_EXU + "i1_ap_e3.bne",
            "i1_e3_jal"     : SWERV_EXU + "i1_ap_e3.jal",

            "i1_e4_beq"     : SWERV_EXU + "i1_ap_e4.beq",
            "i1_e4_bge"     : SWERV_EXU + "i1_ap_e4.bge",
            "i1_e4_blt"     : SWERV_EXU + "i1_ap_e4.blt",
            "i1_e4_bne"     : SWERV_EXU + "i1_ap_e4.bne",
            "i1_e4_jal"     : SWERV_EXU + "i1_ap_e4.jal",

            # TLU
            "faultless"     : SWERV_TLU + "faultless[1:0]",
        }
        values = {}
        for key in signals:
            values[key] = self._vcdhandler.getSignalValue(signals[key], self._vcdhandler.cycle)

        self._view._updateView(values, self._disas_handler)

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

# ===[ Disassembly parser ]================================
class DisassemblyHandler():
    def __init__(self, file):
        self.instructions = self._parseFile(file)

    def _parseFile(self, file):
        fd = open(file, "r")
        instructions = {}
        for line in fd:
            if re.match("\s*[0-9a-fA-F]+:\s+[0-9a-fA-f]+\s+\w+", line):
                pc = re.sub("\s|:", "", re.match("\s*[0-9a-fA-F]+:", line).group())
                pc = (8-len(pc))*'0' + pc #padding
                #insn = re.sub("\s", "", re.search("\s*[0-9a-fA-F]{8}\s+", line).group())
                text = re.sub("\s+", " ", re.sub("^\s+", "", re.search("\s+[a-zA-Z]+\s+.*", line).group()))
                instructions[pc] = text
        fd.close()
        return instructions
        
    def _getInstruction(self, pc):
        if pc in self.instructions:
            return self.instructions[pc]
        else:
            return "invalid"

# ===[ Main Function ]=====================================
if __name__ == '__main__':
    if (len(sys.argv) <= 2 or os.path.exists(sys.argv[1]) != True or os.path.exists(sys.argv[2]) != True):
        print("Usage: swervisual.py <vcd file path> <disassembly file path>")
        exit(-1)
   
    vcdhandler = VCDHandler(sys.argv[1])
    assembly = DisassemblyHandler(sys.argv[2])
    swervisual = QApplication(sys.argv)
    view = SweRVisual()
    view.show()
    ctrl = SweRVisualCtrl(view=view, vcdhandler=vcdhandler, disas_handler=assembly)
    sys.exit(swervisual.exec_())
