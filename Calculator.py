import NeuralNet
import random
import Utility
import math
import chess

class Position:
    def __init__(self, move, children, shared_board):
        self.move = move
        self.children = children
        self.shared_board = shared_board
        self.evaluation = 0
        self.true_evaluation = 0
        self.priors = []
        self.true_priors = []
        self.visit_count = 0
        self.tot_evaluation = 0
        self.UCT = 0

class Calculator:
    def __init__(self, game, board, learning_mode = False, max_depth = 25):
        self.calculated_head = Position(None, None, board)
        self.learning_mode = learning_mode
        self.max_depth = max_depth
        self.game = game
        self.exploration_factor = 2
        self.NeuralNet = NeuralNet.NeuralNet()
            
    def is_confident(val, interval):
        val = Utility.sigmoid(val)
        if val > 1.0 - interval or val < interval or (val < 0.5 + (interval / 2) and val > 0.5 - (interval / 2)):
            return True
        return False
        
    def minimax(self, pos, alpha, beta, is_maximizer, depth, moves):
        if pos.children == None or len(pos.children) == 0:
            pos.children = []
            for move in moves:
                pos.children.append(Position(move[1], None, pos.shared_board))
        if is_maximizer:
            curr_max = -99999999
            for child in pos.children:
                self.game.make_move(pos.shared_board, child.move)
                analysis = self.NeuralNet.analyze(pos.shared_board)
                child.evaluation = analysis["evaluation"]
                child_true_evaluation = child.evaluation
                if not (Calculator.is_confident(child.evaluation, 0.2) or depth >= self.max_depth):
                    child_priors = analysis["priors"]
                    child_true_evaluation = self.minimax(child, alpha, beta, not is_maximizer, depth + 1, child_priors)
                self.game.undo_move(pos.shared_board)
                curr_max = max(curr_max, child_true_evaluation)
                alpha = max(alpha, child_true_evaluation)
                if beta <= alpha:
                    break
            pos.true_evaluation = curr_max
        else:
            curr_min = 99999999
            for child in pos.children:
                self.game.make_move(pos.shared_board, child.move)
                analysis = self.NeuralNet.analyze(pos.shared_board)
                child.evaluation = analysis["evaluation"]
                child_true_evaluation = child.evaluation
                if not (Calculator.is_confident(child.evaluation, 0.2) or depth >= self.max_depth):
                    child_priors = analysis["priors"]
                    child_true_evaluation = self.minimax(child, alpha, beta, not is_maximizer, depth + 1, child_priors)
                self.game.undo_move(pos.shared_board)
                curr_min = min(curr_min, child_true_evaluation)
                beta = min(beta, child_true_evaluation)
                if beta <= alpha:
                    break
            pos.true_evaluation = curr_min
        if self.learning_mode and Calculator.is_confident(pos.true_evaluation, 0.2):
            self.NeuralNet.learn_evaluation(pos.shared_board, pos.evaluation, pos.true_evaluation)
        return pos.true_evaluation
            
    def calculate_minimax(self, pos):
        analysis = self.NeuralNet.analyze(pos.shared_board)
        pos.evaluation = analysis["evaluation"]
        is_maximizer = False
        if self.game.turn() == 1:
            is_maximizer = True
        self.minimax(pos, -99999999, 99999999, is_maximizer, 0, analysis["priors"])
        self.calculated_head = pos

    def make_move(self):
        if self.calculated_head.shared_board.is_fivefold_repetition() or self.calculated_head.shared_board.is_seventyfive_moves():
            return None
        if self.game.drawn:
            return None

        best_child = None
        if self.calculated_head == None:
            return None
        if self.calculated_head.children == None or len(self.calculated_head.children) == 0:
            self.calculate_minimax(self.calculated_head)
        for child in self.calculated_head.children:
            if self.game.turn() == 1:
                if best_child == None or (child.true_evaluation > best_child.true_evaluation):
                    best_child = child
            else:
                if best_child == None or (child.true_evaluation < best_child.true_evaluation):
                    best_child = child
        if best_child == None:
            return None

        side = ""
        if self.calculated_head.shared_board.turn == chess.WHITE:
            side = "White"
        else:
            side = "Black"
        if (side == "Black" and best_child.true_evaluation > 0) or (side == "White" and best_child.true_evaluation < 0):
            if self.calculated_head.shared_board.can_claim_fifty_moves():
                print(side + " claims draw by fifty moves!")
                self.game.drawn = True
                return
            if self.calculated_head.shared_board.can_claim_threefold_repetition():
                print(side + " claims draw by threefold repetition!")
                self.game.drawn = True
                return

        self.game.make_move(self.calculated_head.shared_board, best_child.move)
        best_child.shared_board = self.calculated_head.shared_board
        self.calculated_head = best_child
        self.calculate_minimax(self.calculated_head)
        return best_child.move

    def respond(self, opponent_move):
        found = False
        if self.calculated_head.children != None and opponent_move != None:
            for child in self.calculated_head.children:
                if child.move.uci() == opponent_move.uci():
                    self.game.make_move(self.calculated_head.shared_board, child.move)
                    child.shared_board = self.calculated_head.shared_board
                    self.calculated_head = child
                    found = True

        if not found:
            if opponent_move != None:
                self.game.make_move(self.calculated_head.shared_board, opponent_move)
                self.calculated_head = Position(None, None, self.calculated_head.shared_board)
        
        return self.make_move()

    def normalize(arr):
        tot_sum = 0
        for val in arr:
            tot_sum += val[0]
        for i in range(len(arr)):
            arr[i][0] = arr[i][0] / tot_sum
        return arr

    def discrete_select(arr):
        picker = random.rand()
        curr_sum = 0
        for i in range(len(arr)):
            curr_sum += arr[i][0]
            if picker < curr_sum:
                return i
        return None

    def rollout(self, pos):
        analysis = self.NeuralNet.analyze(pos.shared_board)
        evaluation = analysis["evaluation"]
        if evaluation == 1 or evaluation == -1 or evaluation == 0:
            return evaluation
        self.game.make_move(pos.shared_board, pos.move)
        moves = analysis["priors"]
        normalize(moves)
        best_move = moves[discrete_select(moves)]
        evaluation = rollout(Position(best_move[1], None, pos.shared_board))
        self.game.undo_move(pos.shared_board)
        return evaluation

    def UCB1(self, parent, pos):
        if pos.visit_count == 0:
            return math.inf
        return pos.tot_evaluation / pos.visit_count + self.exploration_factor * math.sqrt(math.log(parent.visit_count) / pos.visit_count)

    def PUCT(self, parent, pos):
        if pos.visit_count == 0:
            return math.inf
        curr_prob = 0
        for prior in parent.priors:
            if prior[1].uci() == pos.move.uci():
                curr_prob = prior[0]
        return pos.tot_evaluation / pos.visit_count + self.exploration_factor * math.sqrt(parent.visit_count) / (1 + pos.visit_count)
    
    def MCTS(self, pos, num_simulations):
        for i in range(num_simulations):
            self.MCTS_subroutine(pos)
    
    def MCTS_subroutine(self, pos):
        if pos.children == None:
            true_eval = 0
            terminal = self.NeuralNet.terminal_evaluation(pos.shared_board)
            if terminal != None:
                true_eval = terminal
            else:
                analysis = self.NeuralNet.analyze(pos.shared_board)
                true_eval = analysis["evaluation"]#rollout(pos.children[0])

                true_moves = []
                terminal_priors = self.NeuralNet.generate_terminal_priors(pos.shared_board)
                pos.priors = analysis["priors"]
                if len(terminal_priors) == 0:
                    true_moves = pos.priors  
                else:
                    true_moves.append(terminal_priors[0])

                pos.children = []
                for move in true_moves:
                    pos.children.append(Position(move[1], None, pos.shared_board))
            pos.tot_evaluation += true_eval
            pos.visit_count += 1
        else:
            best_child = None
            for child in pos.children:
                child.UCT = self.PUCT(pos, child)
                if best_child == None or (child.UCT > best_child.UCT):
                    best_child = child
            self.game.make_move(pos.shared_board, best_child.move)
            true_eval = self.MCTS_subroutine(best_child)
            self.game.undo_move(pos.shared_board)
            pos.tot_evaluation += true_eval
            pos.visit_count += 1
        return true_eval

    def calculate_MCTS(self):
        if self.calculated_head.shared_board.is_fivefold_repetition() or self.calculated_head.shared_board.is_seventyfive_moves():
            return None
        if self.game.drawn:
            return None
            
        self.MCTS(self.calculated_head, 300)
        self.calculated_head.true_evaluation = self.calculated_head.tot_evaluation / self.calculated_head.visit_count
        self.calculated_head.true_priors = []
        curr_sum = 0
        factor = 1
        if self.game.turn() == 1:
            for child in self.calculated_head.children:
                child.true_evaluation = child.tot_evaluation / child.visit_count
                curr_sum += math.exp(child.true_evaluation)
        else:
            for child in self.calculated_head.children:
                child.true_evaluation = child.tot_evaluation / child.visit_count
                curr_sum += math.exp(-1 * child.true_evaluation)
            factor = -1
        best_index = 0
        curr_index = 0
        best_prob = 0
        for child in self.calculated_head.children:
            if curr_sum == 0:
                curr_prob = 0
            else:
                curr_prob = math.exp(factor * child.true_evaluation) / curr_sum
            self.calculated_head.true_priors.append([curr_prob, child.move])
            if curr_prob > best_prob:
                best_prob = curr_prob
                best_index = curr_index
            curr_index += 1

        self.NeuralNet.learn_evaluation(self.calculated_head.shared_board, self.calculated_head.evaluation, self.calculated_head.true_evaluation)
        self.NeuralNet.learn_policies(self.calculated_head.shared_board, self.calculated_head.priors, self.calculated_head.true_priors)
        response = self.calculated_head.true_priors[best_index][1]

        side = ""
        if self.calculated_head.shared_board.turn == chess.WHITE:
            side = "White"
        else:
            side = "Black"
        if (side == "Black" and self.calculated_head.children[best_index].true_evaluation > 0) or (side == "White" and self.calculated_head.children[best_index].true_evaluation < 0):
            if self.calculated_head.shared_board.can_claim_fifty_moves():
                print(side + " claims draw by fifty moves!")
                self.game.drawn = True
                return
            if self.calculated_head.shared_board.can_claim_threefold_repetition():
                print(side + " claims draw by threefold repetition!")
                self.game.drawn = True
                return

        self.game.make_move(self.calculated_head.shared_board, self.calculated_head.true_priors[best_index][1])
        self.calculated_head = Position(None, None, self.calculated_head.shared_board)
        return response