import numpy as np
from random import shuffle
from game_static import Game_Helpers
from decoder import decoder
import time

#Currently only laid out for headsup play, requires changes for more players
#Like for the checking pattern in the BB the number of players must be known
class Game():

    preflop_order = {1: "SB", 2: "SB", 3: "SB", 4: "SB", 5: "SB", 6: "SB"}
    postflop_order = {1: 1, 2: 2, 3: 1, 4: 1, 5: 1, 6: 1}
    streets = {"PREFLOP": "FLOP", "FLOP": "TURN", "TURN": "RIVER", "RIVER": "REWARDS","REWARDS" :"REWARDS"}

    card_dict = {0: '2s', 1: '3s', 2: '4s', 3: '5s', 4: '6s', 5: '7s', 6: '8s', 7: '9s', 8: 'Ts', 9: 'Js',
                  10: 'Qs', 11: 'Ks', 12: 'As', 13: '2d', 14: '3d', 15: '4d', 16: '5d', 17: '6d', 18: '7d',
                  19: '8d', 20: '9d', 21: 'Td', 22: 'Jd', 23: 'Qd', 24: 'Kd', 25: 'Ad', 26: '2h', 27: '3h',
                  28: '4h', 29: '5h', 30: '6h', 31: '7h', 32: '8h', 33: '9h', 34: 'Th', 35: 'Jh', 36: 'Qh',
                  37: 'Kh', 38: 'Ah', 39: '2c', 40: '3c', 41: '4c', 42: '5c', 43: '6c', 44: '7c', 45: '8c',
                  46: '9c', 47: 'Tc', 48: 'Jc', 49: 'Qc', 50: 'Kc', 51: 'Ac'}

    def __init__(self, street = "PREFLOP"):
        self.i = 0
        self.pool = []
        self.positions = {}
        self.current_player = None
        self.action_no = 0
        self.street = street
        self.preflop_history = np.zeros( shape = (25, 13, 4), dtype=np.int_)
        self.flop_history = np.zeros( shape = (25, 13, 4), dtype=np.int_)
        self.turn_history = np.zeros( shape = (25, 13, 4), dtype=np.int_)
        self.river_history = np.zeros( shape = (25, 13, 4), dtype=np.int_)
        self.flop = None
        self.turn = None
        self.river = None
        self.flop_bitmask =  np.zeros(shape = (1,13,4), dtype=np.int_)
        self.turn_bitmask =  np.zeros(shape = (1,13,4), dtype=np.int_)
        self.river_bitmask =  np.zeros(shape = (1,13,4), dtype=np.int_)
        self.history_dict = {'PREFLOP': self.preflop_history,
                             'FLOP': self.flop_history,
                             'TURN': self.turn_history,
                             'RIVER': self.river_history}
        self.community_cards_dict = {'FLOP' : self.flop_bitmask,
                                'TURN' : self.turn_bitmask,
                                'RIVER': self.river_bitmask}
        self.histories= [self.preflop_history,
                         self.flop_history,
                         self.turn_history,
                         self.river_history]

        self.deck = list(range(52))
        self.dealt = False
        shuffle(self.deck)
        self.num_players = 0
        self.game_state = None
        self.move_number = 2
        self.blocking = np.zeros(50,dtype=np.int_)
        self.statics = Game_Helpers()
        self.active_hand = True
        self.next_street = False
        self.hand_history_str = ""
        self.timer = 0

    def update_dicts(self):
        self.history_dict = {'PREFLOP': self.preflop_history,
                             'FLOP': self.flop_history,
                             'TURN': self.turn_history,
                             'RIVER': self.river_history}

        self.community_cards_dict = {'FLOP': self.flop_bitmask,
                                     'TURN': self.turn_bitmask,
                                     'RIVER': self.river_bitmask}
        self.game_state = None

    def add(self, player):
        self.pool.append(player)
        self.update_pool()
        self.num_players = self.num_players +1
        # updates next_Player pointers after adding or shuffling players

    def update_pool(self):
        i = 0
        for i in range(0, len(self.pool)):
            self.positions[i] = self.pool[i]
            self.positions[i].position = i +1
            if i < (len(self.pool) - 1):
                self.positions[i].next_player = self.pool[i + 1]
            else:
                self.positions[i].next_player = self.pool[0]
        self.current_player = self.pool[0]

        # Shuffles the player list and puts them on different positions, so we get a random position in training

    def update_own_flags(self,move, allin):
        if move == 'FOLD':
            self.current_player.has_folded = True
            self.current_player.active = False
        if allin:
            self.current_player.is_allin = True
            self.current_player.active = False
        if move == 'CALL':
            self.current_player.has_acted = True
        if move == 'CHECK':
            self.current_player.has_acted =  True
        if move == 'RAISE':
            self.update_all_flags()
            self.current_player.has_acted = True
        self.is_next_street()

    def shuffle_players(self):
        shuffle(self.pool)
        self.update_pool()

    def set_blinds_and_deal(self):

        self.preflop_history[0, 0, 0] = 1
        self.preflop_history[1, 0, 0:2] = 1

        for player in self.pool:
            if (player.position == 2):
                player.is_bb = np.ones(52).reshape(1, 13, 4)

            cardA = self.deck.pop()
            cardB = self.deck.pop()

            player.set_hand(cardA,cardB)
            player.cards = [cardA,cardB]

    def deal(self):
        if self.street == 'FLOP':
            self.flop = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
            self.hand_history_str += "*** FLOP *** [" + self.card_dict[self.flop[0]] \
                                     +" " + self.card_dict[self.flop[1]]  +" "+ self.card_dict[self.flop[2]]  + "]"\
                                     +"\n"
            self.flop_bitmask = self.flop_bitmask.flatten()
            self.flop_bitmask[self.flop] = 1
            self.flop_bitmask = self.flop_bitmask.reshape(1, 13, 4)

        elif self.street == 'TURN' :
            self.turn = [self.deck.pop()]
            self.hand_history_str += "*** TURN *** [" + self.card_dict[self.turn[0]]  + "]" + "\n"
            self.turn_bitmask = self.turn_bitmask.flatten()
            self.turn_bitmask[self.turn] = 1
            self.turn_bitmask = self.turn_bitmask.reshape(1, 13, 4)
        elif self.street == 'RIVER':
            self.river = [self.deck.pop()]
            self.hand_history_str += "*** RIVER *** [" + self.card_dict[self.river[0]]  + "]" + "\n"
            self.river_bitmask = self.river_bitmask.flatten()
            self.river_bitmask[self.river] = 1
            self.river_bitmask = self.river_bitmask.reshape(1, 13, 4)

        self.update_all_flags()

        for player in self.pool:
            if (player.position == self.postflop_order[self.num_players]):
                self.current_player = player
        self.is_next_street()

    def update_all_flags(self):
        for player in self.pool:
            if (player.is_allin == True or player.has_folded == True):
                player.has_acted = 1
            else:
                player.has_acted = 0

    def is_active_hand(self):
        count = 0

        for player in self.pool:
            if(player.has_folded == True):
                count = count + 1

        if (count +1  == self.num_players):
            return False
        count = 0

        for player in self.pool:
            if (player.active == False):
                count = count + 1

        if (count == self.num_players):
            return False

        return True

    def is_next_street(self):
        for player in self.pool:
            if(player.has_acted == False):
                self.next_street = False
                return

        self.next_street = True

    def build_game_state(self):
        self.game_state = None
        self.update_dicts()
        for player in self.pool:
            for key in player.chips_dict:
                if (self.game_state is not None):
                    self.game_state = np.concatenate((self.game_state,player.chips_dict[key]))
                else:
                    self.game_state = player.chips_dict[key]
        for key in self.history_dict:
            self.game_state = np.concatenate((self.game_state,self.history_dict[key]))
        for key in self.community_cards_dict:
            self.game_state = np.concatenate((self.game_state, self.community_cards_dict[key]))

    def game_start(self):
        if (self.dealt == False):
            self.set_blinds_and_deal()
            self.dealt = True

        while self.street != 'REWARDS':
            while(self.next_street == False) :
                if (self.street == 'REWARDS'):
                    break

                self.update_dicts()
                self.build_game_state()
                move,current_stack = self.current_player.get_move(self.history_dict,self.blocking,self.num_players,self.street,self.game_state)
                move_class,allin = self.statics.move_class(self.history_dict[self.street]
                                                           ,self.street,move,current_stack)

                self.make_move(move)
                self.update_own_flags(move_class,allin)
                #print(self.current_player.name, current_stack.sum()*10, self.current_player.active,np.argmax(move),
                #      move_class,allin,self.street)
                self.move_number = self.move_number +1
                self.current_player = self.current_player.next_player
                self.active_hand = self.is_active_hand()

                if (self.active_hand == False):
                    break

            self.move_number = 0
            self.street = self.streets[self.street]

            if(self.pool[0].has_folded == False and self.pool[1].has_folded ==False and self.street != 'REWARDS'):
                self.deal()
            else:
                self.street = self.streets['REWARDS']

        self.build_game_state()
        self.pool[0].build_player_game_state(self.game_state)
        self.pool[1].build_player_game_state(self.game_state)
        x = time.time()
        decoders = decoder(self.pool[0].game_state, self.pool, self.pool[0].name)
        decoders.prints()
        winners = self.statics.winner(self.pool[0].game_state,decoders.seat_1_hand,decoders.seat_2_hand)
        y = time.time()
        self.timer += (y-x)
        time.sleep(5)
        print(decoders.winner,winners)
        winner = decoders.winner
        reward_p1 = 0
        reward_p2 = 0

        if winner == 1:
            reward_p1 = (decoders.total) / 100
            reward_p2 = (decoders.total) / 100 * -1
        elif winner == 2:
            reward_p1 = (decoders.total) / 100 * -1
            reward_p2 = (decoders.total) / 100

        self.pool[0].set_reward(reward_p1)
        self.pool[1].set_reward(reward_p2)

    def make_move(self,move):
        chips = np.argmax(move)
        chips_bitmask = Game_Helpers.chips_bitmask((chips + 1) * 10)
        history = self.history_dict[self.street]
        check_fold = np.zeros(2)
        chips_bitmask = np.hstack((chips_bitmask, check_fold))
        chips_bitmask = chips_bitmask.reshape(1, 13, 4)

        if (chips == 50):
            history[self.move_number, 12, 2] = 1

        elif (chips == 51):
            history[self.move_number, 12, 3] = 1
            #print(history[self.move_number, 12, 3] == 1,self.move_number,self.street)
            #print(self.preflop_history[self.move_number,:,:])
        else:
            history[self.move_number, :, :] = chips_bitmask




