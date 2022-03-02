#! /usr/bin/env python

"""
This module is the execution point of the chess GUI application.
"""

import sys

import chess
import threading

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget
import Game

class MainWindow(QWidget):
    """
    Create a surface for the chessboard.
    """
    def __init__(self, game):
        """
        Initialize the chessboard.
        """
        super().__init__()

        self.setWindowTitle("Chess GUI")
        self.setGeometry(300, 300, 800, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 600, 600)

        self.boardSize = min(self.widgetSvg.width(),
                             self.widgetSvg.height())
        self.coordinates = True
        self.margin = 0.05 * self.boardSize if self.coordinates else 0
        self.squareSize = (self.boardSize - 2 * self.margin) / 8.0
        self.pieceToMove = [None, None]

        self.game = game
        self.board = game.game_board

        self.promotion_piece = "q"
        
        self.drawBoard()

    @pyqtSlot(QWidget)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.promotion_piece = "q"
            print("Promotion piece has been set to Queen")
        elif event.key() == Qt.Key_N:
            self.promotion_piece = "n"
            print("Promotion piece has been set to Knight")
        elif event.key() == Qt.Key_B:
            self.promotion_piece = "b"
            print("Promotion piece has been set to Bishop")
        elif event.key() == Qt.Key_R:
            self.promotion_piece = "r"
            print("Promotion piece has been set to Rook")


    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        """
        Handle left mouse clicks and enable moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        if event.x() <= self.boardSize and event.y() <= self.boardSize:
            if event.buttons() == Qt.LeftButton:
                if self.margin < event.x() < self.boardSize - self.margin and self.margin < event.y() < self.boardSize - self.margin:
                    fil = int((event.x() - self.margin) / self.squareSize)
                    rank = 7 - int((event.y() - self.margin) / self.squareSize)
                    square = chess.square(fil, rank)
                    piece = self.board.piece_at(square)
                    coordinates = "{}{}".format(chr(fil + 97), str(rank + 1))
                    if self.pieceToMove[0] is not None:
                        if coordinates != self.pieceToMove[1]:
                            curr_str = "{}{}".format(self.pieceToMove[1], coordinates)
                            if self.pieceToMove[0].piece_type == 1 and (coordinates[1:] == "8" or coordinates[1:] == "1"):
                                curr_str += self.promotion_piece
                            move = chess.Move.from_uci(curr_str)
                            if move in self.board.legal_moves:
                                self.board.push(move)
                                self.drawBoard()
                                self.game.send_move(move)
                        piece = None
                        coordinates = None
                    self.pieceToMove = [piece, coordinates]

    def drawBoard(self):
        """
        Draw a chessboard with the starting position and then redraw
        it for every new move.
        """
        self.boardSvg = self.board._repr_svg_().encode("UTF-8")
        self.drawBoardSvg = self.widgetSvg.load(self.boardSvg)

        return self.drawBoardSvg

class GUI():
    def __init__(self, game):
        self.game = game
    
    def initiate(self):
        #th = threading.Thread(target = self.game.send_move, args = (None,))
        self.chessGui = QApplication(sys.argv)
        self.window = MainWindow(self.game)
        self.window.show()
        #th.start()
        sys.exit(self.chessGui.exec_())

    def update_board(self):
        self.window.drawBoard()