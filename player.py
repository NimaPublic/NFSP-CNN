import numpy as np
from game_static import Game_Helpers

class Player():
    def __init__(self, name, chips,agent):
        self.agent = agent
        self.name = name
        self.cards = None
        self.hand = np.zeros(shape = (1,13,4))
        self.chips_preflop = np.zeros(shape = (1,13,4))
        self.chips_flop = np.zeros(shape = (1,13,4))
        self.chips_turn = np.zeros(shape = (1,13,4))
        self.chips_river = np.zeros(shape = (1,13,4))
        self.chips_dict = {'PREFLOP': self.chips_preflop,'FLOP':self.chips_flop,'TURN':self.chips_turn
            ,'RIVER':self.chips_river}
        self.is_bb = np.zeros(shape = (1,13,4))
        self.chips = chips
        self.id = id
        self.has_acted = False
        self.active =  True
        self.is_allin = False
        self.has_folded = False
        self.is_blocking = False
        self.next_player = None
        self.position = None
        self.current_stack = None
        self.game_helpers = Game_Helpers()
        self.game_state = None
        self.chips_dict['PREFLOP'] = self.game_helpers.chips_bitmask_plane(chips)
        self.state_memory = []


    def reset(self,chips):
        self.cards = None
        self.hand = np.zeros(shape = (1,13,4))
        self.chips_preflop = np.zeros(shape = (1,13,4))
        self.chips_flop = np.zeros(shape = (1,13,4))
        self.chips_turn = np.zeros(shape = (1,13,4))
        self.chips_river = np.zeros(shape = (1,13,4))
        self.chips_dict = {'PREFLOP': self.chips_preflop, 'FLOP': self.chips_flop, 'TURN': self.chips_turn
            , 'RIVER': self.chips_river}
        self.is_bb = np.zeros(shape = (1,13,4))
        self.chips = chips
        self.id = id
        self.has_acted = False
        self.active = True
        self.is_allin = False
        self.has_folded = False
        self.is_blocking = False
        self.next_player = None
        self.position = None
        self.current_stack = None
        self.game_helpers = Game_Helpers()
        self.game_state = None
        self.chips_dict['PREFLOP'] = self.game_helpers.chips_bitmask_plane(chips)
        self.agent.reset()
        self.state_memory = []

    def set_hand(self,cardA,cardB):
        self.hand = self.hand.flatten()
        self.hand[cardA] = 1
        self.hand[cardB] = 1
        self.hand = self.hand.reshape(1, 13, 4)

    def build_player_game_state(self,public_state):
        self.game_state = public_state
        self.game_state = np.concatenate((self.game_state, self.is_bb))
        self.game_state = np.concatenate((self.game_state, self.hand))

    def set_street_stacks(self,history,street,player_number):
        current_stack = self.game_helpers.get_stack(history, self.chips, self.position, player_number, street)
        self.chips_dict[street] = self.game_helpers.chips_bitmask_plane(current_stack)

    def set_reward(self,reward):
        for i in range(0,len(self.state_memory)):
            rl_state = None
            if i <= len(self.state_memory) -2:
                rl_state = {'state0': self.state_memory[i]['state'],'action0':self.state_memory[i]['action'],
                            'state1':self.state_memory[i+1]['state'],'reward':0}
            elif i == len(self.state_memory) -1:
                rl_state = {'state0': self.state_memory[i]['state'], 'action0': self.state_memory[i]['action'],
                            'state1': 'Terminal', 'reward': reward}

            self.agent.save_rl_transition(rl_state)

    def get_move(self,history,blocking,player_number,street,public_state):

        self.set_street_stacks(history, street, player_number)
        current_history = history[street]
        current_stack = self.game_helpers.get_stack(history,self.chips,self.position,player_number,street)
        bitmask_stack = self.game_helpers.chips_bitmask(current_stack)
        legals = self.game_helpers.legal_moves(bitmask_stack, current_history , blocking, street)
        legals = np.argwhere(legals == 1)
        self.build_player_game_state(public_state)

        moves,game_state_dict = self.agent.get_move(history,blocking,player_number,street,self.game_state,legals,None)
        self.state_memory.append(game_state_dict)

        return moves,bitmask_stack
