import random
import math
import chess
import chess.engine
from chess.engine import Cp, Mate, MateGiven
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import Utility

class NeuralNet(nn.Module):
    def terminal_evaluation(self, board):
        legals = list(board.legal_moves)
        if len(legals) == 0:
            if board.outcome().winner == chess.WHITE:
                return 10
            elif board.outcome().winner == chess.BLACK:
                return -10
            return 0
        return None

    def generate_terminal_priors(self, board):
        result = []
        legals = list(board.legal_moves)
        for legal in legals:
            board.push(legal)
            new_legals = list(board.legal_moves)
            if len(new_legals) == 0:
                if board.turn == chess.WHITE:
                    if board.outcome().winner == chess.WHITE:
                        result.append([1, legal])
                    elif board.outcome().winner == chess.BLACK:
                        result.append([0, legal])
                else:
                    if board.outcome().winner == chess.WHITE:
                        result.append([0, legal])
                    elif board.outcome().winner == chess.BLACK:
                        result.append([1, legal])
            board.pop()
        return result

    def analyze(self, board):
        info = self.engine.analyse(board, chess.engine.Limit(depth=0))

        white_evaluation = info["score"].white()#random.random() * 20 - 10
        evaluation = 0
        if white_evaluation.is_mate():
            if white_evaluation == MateGiven:
                evaluation = 99999999
            elif white_evaluation == Mate(0):
                evaluation = -99999999
            elif white_evaluation.mate() > 0:
                evaluation = 99999999
            else:
                evaluation = -99999999
        else:
            evaluation = white_evaluation.score() - info["score"].black().score()
        result = {
            "evaluation": evaluation,
            "priors": []
        }
        legals = list(board.legal_moves)
        if len(legals) == 0:
            return result
        for legal in legals:
            board.push(legal)
            info = self.engine.analyse(board, chess.engine.Limit(depth=0))
            white_evaluation = info["score"].white()
            probability = 0
            if white_evaluation.is_mate():
                if white_evaluation == MateGiven:
                    probability = 1.0
                elif white_evaluation == Mate(0):
                    probability = -1.0
                elif white_evaluation.mate() > 0:
                    probability = 1.0
                else:
                    probability = -1.0
            else:
                probability = Utility.sigmoid(white_evaluation.score() - info["score"].black().score())
            board.pop()
            if board.turn == chess.BLACK:
                probability = 1 - probability
            result["priors"].append([probability, legal])
        Utility.quicksort(result["priors"], 0, len(result["priors"]) - 1)
        result["priors"] = result["priors"][:3]
        #curr_sum = 0.0
        #for i in range(len(result["priors"])):
            #curr_sum += math.exp(result["priors"][i][0])
        #for i in range(len(result["priors"])):
            #result["priors"][i][0] = math.exp(result["priors"][i][0]) / curr_sum
        #print(board.turn)
        #print(result)
        #for i in range(3):
            #result["priors"].append([random.random(), legals[random.randint(0, len(legals) - 1)]])
        #Utility.quicksort(result["priors"], 0, len(result["priors"]) - 1)
        return result

    def learn_evaluation(self, board, evaluation, true_evaluation):
        return

    def learn_policies(self, board, priors, true_priors):
        return

    def save_progress(self, path):
        #torch.save(net.state_dict(), path)
        return

    def __init__(self, path = None):
        #super().__init__()
        #self.conv1 = nn.Conv2d(1, 32, 4)
        #self.pool = nn.MaxPool2d(2, 2)
        #self.conv2 = nn.Conv2d(32, 64, 4)
        #self.pool = nn.MaxPool2d(2, 2)
        #self.fc1 = nn.Linear(64 * 2 * 2, 1024)
        #self.fc2 = nn.Linear(1024, 2048)
        #self.fc3 = nn.Linear(2048, 4032)
        #self.criterion = nn.CrossEntropyLoss()
        #self.optimizer = optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        #self.classes = ('pos_winning')
        #for i in range(1, 9):
        #    for j in range(1, 9):
        #        for a in range(1, 9):
        #            for b in range(1, 9):
        #                self.classes += ('move_' + chr(96 + i) + str(j) + chr(96 + a) + str(b) + '_winning')
        #if path != None:
            #self.load_state_dict(torch.load(path))
        self.engine = chess.engine.SimpleEngine.popen_uci("/usr/local/Cellar/stockfish/14.1/bin/stockfish")
        return


    def forward(self, x):
        #x = self.pool(F.relu(self.conv1(x)))
        #x = self.pool(F.relu(self.conv2(x)))
        #x = torch.flatten(x, 1) # flatten all dimensions except batch
        #x = F.relu(self.fc1(x))
        #x = F.relu(self.fc2(x))
        #x = self.fc3(x)
        return x