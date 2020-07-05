#!/usr/bin/python
# -*- coding: utf-8 -*-
from game_static import card_dict
import numpy as np
from treys import Evaluator
from treys import Card
import re
import pandas as pd
from datetime import datetime
import random

class decoder:

    def __init__(self,state,pool,hero):
        self.state = state
        self.dealt_to_str = 'Dealt to '
        self.hand_str = ''
        self.hole_cards_str = '*** HOLE CARDS ***\n'
        self.time = datetime.today().strftime('%Y/%m/%d/%H:%M:%S')
        self.header = 'PokerStars Hand #' + str(random.randint(0,100000000)) \
            + ': Tournament #40000000000, ' \
            + ' $10 + $0 USD Hold\'em  No Limit - Level I (10/20) - ' \
            + self.time + ' CET ' + '[' + self.time + ' ET]' + '\n' \
            + 'Table \'300000000 1\' 2-max ' \
            + 'Seat #1 is the button \n'
        self.small_blind_str = ': posts small blind 10 \n'
        self.big_blind_str = ': posts big blind 20 \n'
        self.total = 0
        self.preflop_history_str = ''
        self.flop_history_str = ''
        self.turn_history_str = ''
        self.river_history_str = ''
        self.flop_str = ''
        self.turn_str = ''
        self.river_str = ''
        self.flop_board_str = ''
        self.turn_board_str = ''
        self.flop_and_turn_board_str = ''
        self.river_board_str = ''
        self.final_board_str = ''
        self.showdown_str = ''
        self.summary = ''
        self.seat_1_str = 'Seat 1: '
        self.seat_2_str = 'Seat 2: '
        self.seat_1_hand = ''
        self.seat_2_hand = ''
        self.return_bet = 0
        self.seat_1_score_name = ''
        self.seat_2_score_name = ''
        self.invested_chips_seat_1 = 0
        self.invested_chips_seat_2 = 0
        self.showdown = False
        self.winner = None
        self.pool = pool
        self.hero = hero
        self.evaluator = Evaluator()
        self.hand_ranks = pd.read_csv('files//hand_rank_names.csv',skiprows=0,delimiter =':')

    def get_seats(self):
        player_1_pre_stack = np.sum(self.state[0, :, :].flatten()) * 10
        player_2_pre_stack = np.sum(self.state[4, :, :].flatten()) * 10
        self.seat_1_str += self.pool[0].name + ' (' \
            + str(int(player_1_pre_stack.item())) + ' in chips)' + '\n'
        self.seat_2_str += self.pool[1].name + ' (' \
            + str(int(player_2_pre_stack.item())) + ' in chips)' + '\n'
        self.small_blind_str = self.pool[0].name + self.small_blind_str
        self.big_blind_str = self.pool[1].name + self.big_blind_str

    def get_hand(self):
        hand = self.state[112, :, :].flatten()
        idx = np.argwhere(hand == 1)
        self.dealt_to_str += self.hero
        self.hand_str += ' ['

        for index in idx:
            self.hand_str += card_dict[index.item()]
            self.hand_str += ' '
        self.hand_str = self.hand_str.strip()
        self.hand_str += ']'
        self.dealt_to_str += ' ' + self.hand_str

    def get_seat_hands(self, hand_plane):
        hand = hand_plane.flatten()
        idx = np.argwhere(hand == 1)
        hand_str = ' ['

        for index in idx:
            hand_str += card_dict[index.item()]
            hand_str += ' '
        hand_str = hand_str.strip()
        hand_str += ']'

        return hand_str

    def get_preflop_history(self):
        preflop_history = self.state[8:33, :, :]

        # post SB and BB

        planes_sum_fold = preflop_history[:, 0:13, 0:4].sum(-1).sum(-1)
        planes_sum = preflop_history[:, 0:12, 0:4].sum(-1).sum(-1) \
            + preflop_history[:, 12, 0:2].sum(-1)
        i = 2

        player_1_chips = self.state[0, :, :].sum(-1).sum(-1).item()
        player_2_chips = self.state[4, :, :].sum(-1).sum(-1).item()

        while planes_sum_fold[i] != 0.0 and i < planes_sum_fold.size:
            allin_str = ''
            player_str = ''
            move_str = ''
            return_bet = ''
            opp_player_str = ''
            if i % 2 == 0:
                player_str = self.pool[0].name + ': '
                opp_player_str = self.pool[1].name
            else:
                player_str = self.pool[1].name + ': '
                opp_player_str = self.pool[0].name
            if planes_sum[i] == planes_sum[i - 1]:
                move_str = 'calls ' + str(int(planes_sum[i].item()
                                              * 10) - int(planes_sum[i - 2].item()
                                                          * 10))

            if planes_sum[i] > planes_sum[i - 1]:
                move_str = 'raises ' + str(int(planes_sum[i].item()
                        * 10 - planes_sum[i - 1].item() * 10)) + ' to ' \
                    + str(int(planes_sum[i].item() * 10))

            if preflop_history[i, 12, 2] == 1:
                move_str = 'checks'

            if preflop_history[i, 12, 3] == 1:
                move_str = 'folds'

                if i % 2 == 0:
                    self.winner = 2
                else:
                    self.winner = 1

                if planes_sum[i - 1] > planes_sum[i - 2]:
                    return_bet = 'Uncalled bet (' + str(
                        int(planes_sum[i - 1].item() * 10 - planes_sum[i - 2].item() * 10)) \
                                 + ') returned to '
                    self.return_bet = int(planes_sum[i - 1].item() * 10 - planes_sum[i - 2].item() * 10)

            if i % 2 == 0 and planes_sum[i] == player_1_chips:
                allin_str = ' and is all-in'

            if i % 2 != 0 and planes_sum[i] == player_2_chips:
                allin_str = ' and is all-in'

            if move_str and player_str != '':
                self.preflop_history_str += player_str + move_str \
                    + allin_str + '\n'
                if return_bet != '':
                    self.preflop_history_str += return_bet + opp_player_str + '\n'

            i += 1

    def get_postflop_history(self, street):
        player_1_chips = None
        player_2_chips = None

        postflop_history = None
        if street == 'FLOP':
            postflop_history = self.state[33:58, :, :]
        elif street == 'TURN':
            postflop_history = self.state[58:83, :, :]
        elif street == 'RIVER':
            postflop_history = self.state[83:108, :, :]


        planes_sum_fold = postflop_history[:, 0:13, 0:4].sum(-1).sum(-1)
        planes_sum = postflop_history[:, 0:12, 0:4].sum(-1).sum(-1) + postflop_history[:, 12, 0:2].sum(-1)
        i = 0

        #to do stacks

        if street == 'FLOP':
            player_1_chips = self.state[1, :, :].sum(-1).sum(-1).item()
            player_2_chips = self.state[5, :, :].sum(-1).sum(-1).item()

        elif street == 'TURN':
            player_1_chips = self.state[2, :, :].sum(-1).sum(-1).item()
            player_2_chips = self.state[6, :, :].sum(-1).sum(-1).item()

        elif street == 'RIVER':
            player_1_chips = self.state[3, :, :].sum(-1).sum(-1).item()
            player_2_chips = self.state[7, :, :].sum(-1).sum(-1).item()

        while planes_sum_fold[i] != 0.0 and i < planes_sum_fold.size:
            allin_str = ''
            player_str = ''
            opp_player_str = ''
            move_str = ''
            return_bet = ''
            if i % 2 == 0:
                player_str = self.pool[1].name + ': '
                opp_player_str = self.pool[0].name
            else:
                player_str = self.pool[0].name + ': '
                opp_player_str = self.pool[1].name
            if i == 0 and planes_sum[0] > 0:
                move_str = 'bets ' + str(int(planes_sum[i].item()
                                              * 10))

            if i == 1 and planes_sum[1] > 0 and postflop_history[0, 12, 2] == 1:
                move_str = 'bets ' + str(int(planes_sum[i].item()
                                             * 10))

            if planes_sum[i] == planes_sum[i - 1] and planes_sum[i] != 0:
                move_str = 'calls ' + str(int(planes_sum[i].item()
                        * 10) - int(planes_sum[i-2].item()
                        * 10))

            if planes_sum[i] > planes_sum[i - 1] and move_str == '':
                move_str = 'raises ' + str(int(planes_sum[i].item() * 10 - planes_sum[i - 1].item() * 10)) + ' to ' \
                          + str(int(planes_sum[i].item() * 10))

            if postflop_history[i, 12, 2] == 1:
                move_str = 'checks'

            if postflop_history[i, 12, 3] == 1:
                move_str = 'folds'
                if i % 2 == 0:
                    self.winner = 1
                else:
                    self.winner = 2
                if planes_sum[i-1] > planes_sum[i - 2]:
                    return_bet = 'Uncalled bet (' + str(int(planes_sum[i-1].item() * 10 - planes_sum[i - 2].item() * 10)) \
                                 +') returned to '
                    self.return_bet = int(planes_sum[i-1].item() * 10 - planes_sum[i - 2].item() * 10)

            if i % 2 == 0 and planes_sum[i] == player_2_chips:
                allin_str = ' and is all-in'

            if i % 2 != 0 and planes_sum[i] == player_1_chips:
                allin_str = ' and is all-in'

            if move_str and player_str != '' and street == 'FLOP':
                self.flop_history_str +=  player_str + move_str \
                    + allin_str  + '\n'

                if return_bet != '':
                    self.flop_history_str += return_bet + opp_player_str + '\n'

            elif move_str and player_str != '' and street == 'TURN':
                self.turn_history_str +=  player_str + move_str \
                    + allin_str + '\n'
                if return_bet != '':
                    self.turn_history_str += return_bet + opp_player_str + '\n'

            elif move_str and player_str != '' and street == 'RIVER':
                self.river_history_str +=  player_str + move_str \
                                         + allin_str  + '\n'
                if return_bet != '':
                    self.river_history_str += return_bet + opp_player_str + '\n'
            i += 1


    def get_flop_board(self):
        flop = self.state[108, :, :].flatten()

        if flop.sum(-1).sum(-1) == 0:
            return

        self.flop_str = '*** FLOP *** '

        idx = np.argwhere(flop == 1)

        if idx.size > 3:
            raise ValueError('Too many Flop Cards')

        i = 0

        for index in idx:

            if i == 0:
                self.flop_board_str += '['

            i += 1
            self.flop_board_str += card_dict[index.item()]

            if i != 3:
                self.flop_board_str += ' '

            if i == 3:
                self.flop_board_str += ']\n'

    def get_turn_board(self):
        turn = self.state[109, :, :].flatten()
        if turn.sum(-1).sum(-1) == 0:
            return

        self.turn_str = '*** TURN *** '

        idx = np.argwhere(turn == 1)

        if idx.size > 1:
            raise ValueError('Too many Turn Cards')

        for index in idx:
            self.turn_board_str += ' '
            self.turn_board_str += '['
            self.turn_board_str += card_dict[index.item()]
            self.turn_board_str += ']'

        self.turn_board_str = self.flop_board_str.strip() + self.turn_board_str + '\n'

    def get_flop_and_turn_board(self):

        flop = self.state[108, :, :].flatten()
        flop_idx = np.argwhere(flop == 1)
        turn = self.state[109, :, :].flatten()
        turn_idx = np.argwhere(turn == 1)
        river = self.state[110, :, :].flatten()

        if river.sum(-1).sum(-1) == 0:
            return

        if flop_idx.size > 3:
            raise ValueError('Too many Flop Cards')

        if turn_idx.size > 1:
            raise ValueError('Too many Turn Cards')

        i = 0

        for index in flop_idx:

            if i == 0:
                self.flop_and_turn_board_str += '['

            i += 1
            self.flop_and_turn_board_str += card_dict[index.item()]
            self.flop_and_turn_board_str += ' '

        for index in turn_idx:
            self.flop_and_turn_board_str += card_dict[index.item()]
            self.flop_and_turn_board_str += ']'

    def get_river_board(self):
        river = self.state[110, :, :].flatten()
        idx = np.argwhere(river == 1)

        if river.sum(-1).sum(-1) == 0:
            return

        self.river_str = '*** RIVER *** '

        if idx.size > 1:
            raise ValueError('Too many River Cards')

        for index in idx:
            self.river_board_str += ' ['
            self.river_board_str += card_dict[index.item()]
            self.river_board_str += ']'

    # On the river the flop and turn are together inside Brackets

    def get_final_board(self):
        flop = self.state[108, :, :].flatten()
        turn = self.state[109, :, :].flatten()
        river = self.state[110, :, :].flatten()
        idx = np.argwhere(flop == 1)

        if flop.sum(-1).sum(-1) == 0:
            return

        idx = np.append(idx,np.argwhere(turn == 1))
        idx = np.append(idx,np.argwhere(river == 1))

        self.final_board_str = 'Board ['

        for index in idx :

            self.final_board_str += card_dict[index.item()]
            self.final_board_str += ' '

        self.final_board_str = self.final_board_str.strip()
        self.final_board_str += ']'


    #get the last plane of each player that isn't a fold/check for every street and sum them up
    def get_player_invested(self):
        preflop_planes = self.state[8:33, :, :]
        flop_planes = self.state[33:58, :, :]
        turn_planes = self.state[58:83, :, :]
        river_planes = self.state[83:108, :, :]
        postflop_planes = [flop_planes,turn_planes,river_planes]

        self.invested_chips_seat_1 += np.max(preflop_planes[0::2, 0:12, 0:4].sum(-1).sum(-1) + preflop_planes[0::2, 12, 0:2].sum(-1))
        self.invested_chips_seat_2 += np.max(preflop_planes[1::2, 0:12, 0:4].sum(-1).sum(-1) + preflop_planes[1::2, 12, 0:2].sum(-1))

        for planes in postflop_planes:
            self.invested_chips_seat_2+= np.max(planes[0::2, 0:12, 0:4].sum(-1).sum(-1) + planes[0::2, 12, 0:2].sum(-1))
            self.invested_chips_seat_1 += np.max(planes[1::2, 0:12, 0:4].sum(-1).sum(-1) + planes[1::2, 12, 0:2].sum(-1))

        self.invested_chips_seat_1 = int(self.invested_chips_seat_1 * 10)
        self.invested_chips_seat_2 = int(self.invested_chips_seat_2 * 10)
        self.total = self.invested_chips_seat_1 + self.invested_chips_seat_2 - self.return_bet

        #If the last action taken was not a fold, then there is a showdown. Only applicable to headsup.
    def get_showdown(self):

        history_planes = self.state[8:108, :, :]
        planes_with_actions = history_planes.sum(-1).sum(-1)
        last_action = np.max(np.argwhere(planes_with_actions > 0))

        if history_planes[last_action,12, 3] != 1:
            self.showdown = True

        if self.showdown == True:

            # for loop instead, for Omaha, change to seats
            seat_1_hand =  re.sub('[\[\]]', '', self.seat_1_hand)
            seat_1_hand = seat_1_hand.split()
            seat_1_hand = [Card.new(seat_1_hand[0]), Card.new(seat_1_hand[1])]

            seat_2_hand =  re.sub('[\[\]]','',self.seat_2_hand)
            seat_2_hand = seat_2_hand.split()
            seat_2_hand = [Card.new(seat_2_hand[0]),Card.new(seat_2_hand[1])]

            board = re.sub('[\[\]]','',self.flop_and_turn_board_str +' ' + self.river_board_str )
            board = board.split()
            board_treys = []

            for cards in board:
                board_treys.append(Card.new(cards))


            seat_1_score = self.evaluator.evaluate(board_treys, seat_1_hand)
            seat_2_score = self.evaluator.evaluate(board_treys, seat_2_hand)

            seat_2_score_name = self.hand_ranks.loc[self.hand_ranks['ID'] == seat_2_score]
            self.seat_2_score_name = ' (' + seat_2_score_name.iloc[0]['Name'].strip() + ')'
            seat_1_score_name = self.hand_ranks.loc[self.hand_ranks['ID'] == seat_1_score]
            self.seat_1_score_name = ' (' + seat_1_score_name.iloc[0]['Name'].strip() + ')'

            self.showdown_str = '*** SHOW DOWN ***\n'
            self.showdown_str += self.pool[0].name + ': shows ' + self.seat_1_hand   +  self.seat_1_score_name + '\n'
            self.showdown_str += self.pool[1].name + ': shows ' + self.seat_2_hand  +  self.seat_2_score_name + '\n'

            half_pot = int(self.total / 2)


            if seat_1_score < seat_2_score:
                self.showdown_str += self.pool[0].name + ' collected ' + str(self.total) + ' from pot\n'
                self.winner = 1
            elif seat_1_score == seat_2_score:
                self.showdown_str += self.pool[0].name + ' collected ' + str(half_pot) + ' from pot\n'
                self.showdown_str += self.pool[1].name + ' collected ' + str(half_pot) + ' from pot\n'
                self.winner = 0
            else:
                self.showdown_str += self.pool[1].name + ' collected ' + str(self.total) + ' from pot\n'
                self.winner = 2

        if self.showdown == False:
            if self.winner == 1:
                self.showdown_str += self.pool[0].name + ' collected ' + str(self.total) +' from pot\n'
                self.showdown_str += self.pool[0].name + ': ' + 'shows ' + self.seat_1_hand + '\n'
            else:
                self.showdown_str += self.pool[1].name + ' collected ' + str(self.total) + ' from pot\n'
                self.showdown_str += self.pool[1].name + ': ' + 'doesn\'t show hand\n'


    def get_summary(self):
        self.summary = '*** SUMMARY ***\nTotal pot ' + str(self.total) + '| Rake 0\n'
        if self.final_board_str !='':
            self.summary += self.final_board_str
            self.summary += '\n'

        folded_pre = ' folded before the Flop'
        folded_flop = ' folded on the Flop'
        folded_turn = ' folded on the Turn'
        folded_river = 'folded on the River'
        seat_1 = 'Seat 1: ' + self.pool[0].name + ' (button) (small blind)'
        seat_2 = 'Seat 2: ' + self.pool[1].name + ' (big blind)'
        preflop_planes_folds = self.state[8:33, 12, 3]
        fold_ids = np.argwhere(preflop_planes_folds == 1)

        if fold_ids.size != 0:
            if fold_ids.item() % 2 == 0:
                seat_1 += folded_pre
                seat_2 += ' collected ' + str(self.total)
            else:
                seat_2 += folded_pre
                seat_1 += ' collected ' + '(' + str(self.total) + ')'

        flop_planes = self.state[33:58, 12, 3]
        turn_planes = self.state[58:83, 12, 3]
        river_planes = self.state[83:108, 12, 3]

        postflop_planes = [flop_planes,turn_planes,river_planes]
        fold_dict = {1:folded_flop,2:folded_turn,3:folded_river}
        i = 1

        for plane in postflop_planes:
            fold_ids = np.argwhere(plane == 1)

            if fold_ids.size != 0:
                if fold_ids.item() % 2 == 0:
                    seat_2 += fold_dict[i]
                    seat_1 += ' collected ' + '(' + str(self.total) + ')'

                else:
                    seat_1 += fold_dict[i]
                    seat_2 += ' collected ' + '(' + str(self.total) + ')'
            i += 1

        if self.showdown == True:
            seat_1 += ' showed ' + self.seat_1_hand
            seat_2 += ' showed ' + self.seat_2_hand

            if self.winner == 1:
                seat_1 += ' and won (' + str(self.total) + ')' + ' with ' +re.sub('[()]', '', self.seat_1_score_name).strip()
                seat_2 += ' and lost with ' +re.sub('[()]', '', self.seat_2_score_name).strip()

            elif self.winner == 2:
                seat_2 += ' and won (' + str(self.total) + ')' + ' with ' +re.sub('[()]', '', self.seat_2_score_name).strip()
                seat_1 += ' and lost with ' +re.sub('[()]', '', self.seat_1_score_name).strip()

            elif self.winner == 0:
                seat_1 += ' and won (' + str(self.total/2) + ')' + ' with' +re.sub('[()]', '', self.seat_1_score_name).strip()
                seat_2 += ' and won (' + str(self.total/2) + ')' + ' with' +re.sub('[()]', '', self.seat_2_score_name).strip()

        seat_1 += '\n'
        seat_2 += '\n'

        self.summary += seat_1
        self.summary += seat_2

    def set_straights(self):
        self.flop_str += self.flop_board_str
        self.turn_str += self.turn_board_str
        self.river_str += self.flop_and_turn_board_str
        self.river_str += self.river_board_str
        if self.river_str != '':
            self.river_str += '\n'
        # print(self.flop_str)

    def prints(self):

        self.seat_1_hand = self.get_seat_hands(self.pool[0].hand)
        self.seat_2_hand = self.get_seat_hands(self.pool[1].hand)
        self.get_hand()
        self.get_seats()
        self.get_flop_board()
        self.get_turn_board()
        self.get_river_board()
        self.get_flop_and_turn_board()
        self.set_straights()
        self.get_preflop_history()
        self.get_postflop_history('FLOP')
        self.get_postflop_history('TURN')
        self.get_postflop_history('RIVER')
        self.get_player_invested()
        self.get_showdown()
        self.get_final_board()
        self.get_summary()
        total = self.header + self.seat_1_str + self.seat_2_str \
            + self.small_blind_str + self.big_blind_str \
            + self.hole_cards_str + self.dealt_to_str +'\n' \
            + self.preflop_history_str + self.flop_str \
            + self.flop_history_str + self.turn_str \
            + self.turn_history_str\
            + self.river_str \
            + self.river_history_str + self.showdown_str
        total = total.strip()
        # I just can't understand the reason there is a space before summary
        total += '\n' + self.summary
        #with open("best_network.txt", "a") as myfile:
          #myfile.write(total +'\n')

        #print(total)