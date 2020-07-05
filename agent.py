import numpy as np
from pokernet import PokerNet
from sl_memory import SLMemory
from rl_memory import RLMemory
import random
import torch

class Agent():
    def __init__(self, name, db_name_sl, table_name_sl, db_name_rl, table_name_rl, filters = 32,
                 agent_path = None, sl_agent_path = None, epsilon = 0.25, anticipatory = 0.14, learning_rate_rl = 0.0035,
                 learning_rate_sl = 0.01, device = 'cuda'):

        self.name = name
        self.num_filters = filters
        self.agent_path = agent_path
        self.sl_memory = SLMemory(table_name_sl)
        self.rl_memory = RLMemory(table_name_rl)
        self.epsilon = epsilon
        self.anticipatory = anticipatory

        self.device =torch.device('cuda')

        if device == 'cpu':
            self.device = torch.device('cpu')

        self.best_response = True
        self.model = PokerNet(filters).to(self.device)
        self.learning_rate_rl = learning_rate_rl
        self.learning_rate_sl = learning_rate_sl
        self.target_net = PokerNet(filters).to(self.device)
        self.sl_model = PokerNet(filters).to(self.device)
        self.optimizer_rl = torch.optim.SGD(self.model.parameters(), self.learning_rate_rl)
        self.optimizer_sl = torch.optim.SGD(self.sl_model.parameters(), self.learning_rate_sl)

        if agent_path is not None:
            self.model.load_state_dict(torch.load(agent_path))


        if sl_agent_path is not None:
            self.sl_model.load_state_dict(torch.load(sl_agent_path))

        self.active_net = self.model
        self.set_target_net()

    def set_target_net(self):
        print('hey')
        self.target_net.load_state_dict(self.model.state_dict())

    def save_net(self,rl_path,sl_path):
        torch.save(self.model.state_dict(), rl_path)
        torch.save(self.model.state_dict(), sl_path)

    def reset(self):
        self.set_active_net()
        self.best_response = True
        self.set_active_net()

    def save_sl_transition(self, state, move):
        state_action_dict = {'state': state, 'action': move}
        self.sl_memory.push(state_action_dict)

    def set_active_net(self):
        self.active_net = self.model
        anticipatory_rand = random.random()

        if anticipatory_rand <= self.anticipatory:
            self.active_net = self.sl_model
            self.best_response = False

    def save_rl_transition(self,state_action_dict):
        self.rl_memory.push(state_action_dict)

    def get_move(self,history,blocking,player_number,street,game_state,legals,abstraction):
        with torch.no_grad():
            legals = torch.from_numpy(legals).long().to(self.device)
            torch_state = torch.from_numpy(game_state).float().to(self.device)
            torch_state = torch_state.unsqueeze(0)
            predict = self.active_net(torch_state).flatten()
            moves = np.zeros(52)

            e_greedy = random.random()
            move = None

            if e_greedy <= self.epsilon and self.best_response == True:
                size = np.prod(legals.shape) -1
                rand_index = random.randint(0,size)
                move = legals[rand_index].item()
                game_state_dict = {'state': torch_state.tolist(), 'action' :move}

            else:
                a = torch.argmax(predict[legals])
                move = legals[torch.argmax(predict[legals])]
                move = move.item()
                game_state_dict = {'state': torch_state.tolist(), 'action': move}

                if self.best_response == True:
                    self.save_sl_transition(torch_state.tolist(), move)

            moves[move] = 1

        return moves,game_state_dict
