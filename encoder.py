from game_static import card_dict
import numpy as np
import re
import pandas as pd
from datetime import datetime
import random
from game_static import Game_Helpers
from player import Player
from game import Game
from decoder import decoder

class encoder:
    def __init__(self,path):
        self.path = path
        self.game_state = np.zeros([113,13,4])
        self.game_state_list = []
        self.hand_history_list = []
        self.current_hand_history = ''
        self.statics = Game_Helpers()

    def get_hand_histories(self):
        file = open(self.path, 'r')
        hand_history = ''
        for line in file:
            if line != '\n':
                hand_history += line
            else:
                self.hand_history_list.append(hand_history)
                hand_history = ''

        for hand in self.hand_history_list:
            self.current_hand_history = hand
            self.get_chips()
            self.game_state_list.append(self.game_state)
            self.game_state = np.zeros([113, 13, 4])


    def get_chips(self):
            seat_1_chips = re.sub("[^\\d]",'',re.findall('([0-9]* in chips)',self.current_hand_history)[0])
            seat_2_chips = re.sub("[^\\d]",'',re.findall('([0-9]* in chips)',self.current_hand_history)[1])

            sb_name = re.findall('.*: posts small blind',self.current_hand_history)[0]
            bb_name = re.findall('.*: posts big blind',self.current_hand_history)[0]
            index_sb = sb_name.find(':')
            index_bb = bb_name.find(':')
            sb_name = sb_name[:index_sb]
            bb_name = bb_name[:index_bb]
            own_name =  re.findall('Dealt to .*\n',self.current_hand_history)[0]
            is_bb = 0

            if bb_name in own_name:
                is_bb = 1

            hole_cards =  re.search('\[.*\]',own_name)[0].strip('[]').split()
            hole_cards_idx = []

            keys = list(card_dict.keys())
            values = list(card_dict.values())
            layer = np.zeros(52)
            for card in hole_cards:
                idx = keys[values.index(card)]
                hole_cards_idx.append(idx)
                layer[idx] = 1

            self.game_state[112, :, :] = layer.reshape(1, 13, 4)

            splits = self.current_hand_history.split('\n')
            current_street = 'PREFLOP'
            preflop_actions =[]
            flop_actions = []
            turn_actions = []
            river_actions = []
            rewards = []
            action_dict = {'PREFLOP':preflop_actions, 'FLOP':flop_actions, 'TURN': turn_actions,
                           'RIVER': river_actions, 'REWARDS' : rewards}

            for action in splits:
                if action.startswith('*** FLOP ***'):
                    current_street = 'FLOP'
                elif action.startswith('*** TURN ***'):
                    current_street = 'TURN'
                elif action.startswith('*** RIVER ***'):
                    current_street = 'RIVER'

                if (action.startswith(sb_name + ":") or action.startswith(bb_name + ":")) and not (action.startswith(sb_name + ": shows") \
                        or action.startswith(bb_name + ": shows")):
                    action_dict[current_street].append(action)
                    test = sb_name + ": shows"

            self.set_action_history(preflop_actions, 'PREFLOP')
            self.set_action_history(flop_actions, 'FLOP')
            self.set_action_history(turn_actions, 'TURN')
            self.set_action_history(river_actions, 'RIVER')

            if is_bb == 1:
                self.game_state[111,:,:] = 1

            #seat_1_player = Player(sb_name,int(seat_1_chips),None)
            #seat_2_player = Player(bb_name, int(seat_2_chips), None)
            #pool = [seat_1_player,seat_2_player]
            #seat_1_player.set_hand(hole_cards_idx[0],hole_cards_idx[1])
            #seat_2_player.set_hand(2, 3)
            self.get_board()
            self.set_stacks(int(seat_1_chips))

            #decoders = decoder(self.game_state,pool,'hero')
            #decoders.prints()
    def set_action_history(self, actions, street):
        id = -1
        i = 0

        if street == 'PREFLOP':
            #Blinds
            self.game_state[8, 0, 0] = 1
            self.game_state[9, 0, 0:2] = 1
            del actions[0:2]
            id = 8
            i = 2

        elif street == 'FLOP':
            id = 33

        elif street == 'TURN':
            id = 58

        elif street == 'RIVER':
            id = 83

        for action in actions:
            if action.find('raises') != -1 or action.find('bets') != -1:
                size = re.sub('([^\d \s])','', action).split()
                size = np.max(list(map(int, size)))
                layer = self.statics.chips_bitmask_plane(int(size))
                self.game_state[id+i,:,:] = layer

            if action.find('folds') != -1:
                self.game_state[id + i, 12, 3] = 1

            if action.find('checks') != -1:
                self.game_state[id + i, 12, 2] = 1

            if action.find('calls') != -1:
                size = int(re.sub('([^\d])', '', action))
                previous_paid = (self.game_state[id+i-2, 0:12, 0:4].sum(-1).sum(-1) + self.game_state[id+i-2, 12, 0:2].sum(-1))*10
                layer = self.statics.chips_bitmask_plane(int(size) + previous_paid)
                self.game_state[id + i, :, :] = layer

            i += 1

    def get_board(self):
        keys = list(card_dict.keys())
        values = list(card_dict.values())

        if re.findall('\*\*\* FLOP \*\*\* \[.*\]',self.current_hand_history) != []:
            flop = re.sub('\*\*\* FLOP \*\*\* ','',re.findall('\*\*\* FLOP \*\*\* \[.*\]',self.current_hand_history)[0])
            flop = re.search('\[.*\]',flop)[0].strip('[]').split()

            layer = np.zeros(52)
            for card in flop:
                idx = keys[values.index(card)]
                layer[idx] = 1
            self.game_state[108, :, :] = layer.reshape(1, 13, 4)

        if re.findall('\*\*\* TURN \*\*\* \[.*\] \[..\]', self.current_hand_history) != []:
            layer = np.zeros(52)
            turn = re.sub('\*\*\* TURN \*\*\* ','',re.findall('\*\*\* TURN \*\*\* \[.*\] \[..\]',self.current_hand_history)[0])
            turn = re.search('\[..\]',turn)[0].strip('[]').split()

            for card in turn:
                idx = keys[values.index(card)]
                layer[idx] = 1
            self.game_state[109, :, :] = layer.reshape(1, 13, 4)

        if re.findall('\*\*\* RIVER \*\*\* \[.*\] \[..\]', self.current_hand_history) != []:
            layer = np.zeros(52)
            river = re.sub('\*\*\* RIVER \*\*\* ', '', re.findall('\*\*\* RIVER \*\*\* \[.*\] \[..\]', self.current_hand_history)[0])
            river = re.search('\[..\]', river)[0].strip('[]').split()

            for card in river:
                idx = keys[values.index(card)]
                layer[idx] = 1

            self.game_state[110, :, :] = layer.reshape(1, 13, 4)

    def set_stacks(self,stack):
        preflop_history  =self.game_state[8:33,:,:]
        flop_history =self.game_state[33:58,:,:]
        turn_history = self.game_state[58:83, :, :]
        river_history = self.game_state[83:108, :, :]

        history = {'PREFLOP': preflop_history,
                             'FLOP': flop_history,
                             'TURN':turn_history,
                             'RIVER': river_history}



        layer = self.statics.chips_bitmask_plane(int(stack))
        self.game_state[0, :, :] = layer
        layer = self.statics.chips_bitmask_plane(int(stack))
        self.game_state[4, :, :] = layer
        self.game_state[1,:,:] = self.statics.chips_bitmask_plane(self.statics.get_stack(history, stack, 1, 2, 'FLOP'))
        self.game_state[2, :, :] = self.statics.chips_bitmask_plane(self.statics.get_stack(history, stack, 1, 2, 'TURN'))
        self.game_state[3, :, :] = self.statics.chips_bitmask_plane(self.statics.get_stack(history, stack, 1, 2, 'RIVER'))
        self.game_state[5, :, :] = self.statics.chips_bitmask_plane(self.statics.get_stack(history, stack, 1, 2, 'FLOP'))
        self.game_state[6, :, :] = self.statics.chips_bitmask_plane(self.statics.get_stack(history, stack, 1, 2, 'TURN'))
        self.game_state[7, :, :] = self.statics.chips_bitmask_plane(self.statics.get_stack(history, stack, 1, 2, 'RIVER'))
