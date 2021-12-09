import chess
import GUI
import Calculator

class Game:
    def make_move(self, board, move):
        board.push(move)

    def undo_move(self, board):
        board.pop()

    def turn(self):
        if self.game_board.turn == chess.WHITE:
            return 1
        return 0

    def send_move(self, move):
        engine_move = self.calculator.respond(move)
        #engine_move = self.calculator.calculate_MCTS()
        if engine_move != None:
            self.game_board.push(engine_move)
        self.gui.update_board()
        new_legals = list(self.game_board.legal_moves)
        if len(new_legals) == 0:
            if self.game_board.outcome().winner == chess.WHITE:
                print("White is victorious!")
            elif self.game_board.outcome().winner == chess.BLACK:
                print("Black is victorious!")
            else:
                print("Drawed!")
            self.calculator.NeuralNet.save_progress('./specter_net.pth')
        else:
            self.send_move(None)
            #return

    def __init__(self):
        self.game_board = chess.Board()
        self.calculator = Calculator.Calculator(self, chess.Board(self.game_board.fen()), True, 5)
        self.gui = GUI.GUI(self)
        self.gui.initiate()