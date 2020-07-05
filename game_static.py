import numpy as np
import math
from numpy import array
from treys import Evaluator
from treys import Card


evaluator = Evaluator()
preflop_order = {1: "SB", 2: "SB", 3: "SB", 4: "SB", 5: "SB", 6: "SB"}
postflop_order = {1: 1, 2: 2, 3: 1, 4: 1, 5: 1, 6: 1}
streets = {"PREFLOP": "FLOP", "FLOP": "TURN", "TURN": "RIVER", "RIVER": "REWARDS", "REWARDS": "REWARDS"}

card_dict = {0: '2c', 1: '2d', 2: '2h', 3: '2s',
            4: '3c', 5: '3d', 6: '3h', 7: '3s',
            8: '4c', 9: '4d', 10: '4h', 11: '4s',
            12: '5c', 13: '5d', 14: '5h', 15: '5s',
            16: '6c', 17: '6d', 18: '6h', 19: '6s',
            20: '7c', 21: '7d', 22: '7h', 23: '7s',
            24: '8c', 25: '8d', 26: '8h', 27: '8s',
            28: '9c', 29: '9d', 30: '9h', 31: '9s',
            32: 'Tc', 33: 'Td', 34: 'Th', 35: 'Ts',
            36: 'Jc', 37: 'Jd', 38: 'Jh', 39: 'Js',
            40: 'Qc', 41: 'Qd', 42: 'Qh', 43: 'Qs',
            44: 'Kc', 45: 'Kd', 46: 'Kh', 47: 'Ks',
            48: 'Ac', 49: 'Ad', 50: 'Ah', 51: 'As'}


class Game_Helpers():

    @staticmethod
    def get_stack(histories, starting_stack, position, player_number,street):
        #Bits 50,51 are checks and Fold or if both are 1 then player is allin, if both are -1 player has folded
        #should as such not be counted
        stack = starting_stack

        for key in histories:
            if(key == street):
                break
            history = histories[key]
            used = 0
            max_raise = np.argmax(history [position - 1::player_number, :, :].sum(-1).sum(-1))
            own_used = history[position - 1::player_number, :, :]
            used = own_used[max_raise, 0:12, 0:4].sum(-1).sum(-1) + own_used[max_raise, 12, 0:2].sum(-1)
            used = used * 10

            stack = stack - used

        return stack


    @staticmethod
    def chips_bitmask_plane(chips):
        layer = np.zeros(52, dtype=np.int_)
        bits = math.ceil(chips / 10)
        bits = int(bits)
        bits = (50 if bits > 50 else bits)
        layer[0:bits] = 1
        layer = layer.reshape(1,13,4)
        return layer


    @staticmethod
    def chips_bitmask(chips):
        layer = np.zeros(50, dtype=np.int_)
        bits = math.ceil(chips / 10)
        bits = int(bits)
        bits = (50 if bits > 50 else bits)
        layer[0:bits] = 1
    
        return layer


    @staticmethod
    def get_current_raise(history,street):
        history = array(history, dtype=np.int_)
        # currently in BB should be in SB so x2
        # sums all elements of each plane and then takes the max
        check = False
        unopened = True
    
        #planes_sum = history.sum(-1).sum(-1)
        planes_sum = history[:,0:12,0:4].sum(-1).sum(-1) + history[:,12,0:2].sum(-1)
    
        if (planes_sum.sum() > 0):
            unopened = False
    
        sb_fills = history[2,0:12,0:4].sum(-1).sum(-1) +history[2,12,0:2].sum(-1)
    
        if (street == 'PREFLOP' and sb_fills.sum() == 2 and history[3,:,:].sum(-1).sum(-1) == 0):
            unopened = True
    
        raise_size = np.max(planes_sum)
    
        # we also need the index for the minraise calculation.Normal case is: raise_size = 2xhighest raise - second highest raise
        # some edge cases like blocking raise, an allin of a shorter stack player that was higher than the previous raise, but less
        # than a minraise
        # Edge case 2: Unopened pot
        # Edge case 3: preflop when blinds are posted
    
        raise_index = np.argmax(planes_sum)
    
        if raise_index != 0:
            prior_raise = np.max(history[0:raise_index, :, :
                                 ].sum(-1).sum(-1))
        else:
            prior_raise = 0
    
        minraise = 2 * raise_size - prior_raise
    
        # min call still missing e.g. somebody goes allin with 0.5bb then mincall = 1
        # open allin by a less than 1 bb Stack
    
        if prior_raise == 0 and raise_size > 0 and raise_size < 2:
            minraise = 4
    
        # unopened
    
        if prior_raise == 0 and raise_size == 0:
            minraise = 2
    
        # blind
    
        if prior_raise == 1 and raise_size == 2:
            minraise = 4
    
        # if is_blocking_raise == 1:
        # ....minraise = raise_size
    
        minraise_arr = np.zeros(50, dtype=np.int_)
        raise_size_arr = np.zeros(50, dtype=np.int_)
    
        # might have a bug when raise = 0.5 bb which is a single 1 or 1 SB
    
        minraise_arr[int(minraise - 1):] = 1
    
        if (unopened == False):
            raise_size_arr[int(raise_size) - 1] = 1
    
        #checks are allowed in two cases:
        #a) when there was no opening bet e.g. first to act on the flop or second to act after first checks
        #b) when we are in the BB and people only called the Blinds
    
        if (unopened == True):
            check = True
    
        return (minraise_arr, raise_size_arr, check)


    @staticmethod
    def legal_moves( stack, history, blocking, street):
        history = array(history, dtype=np.int_)
        (minraise, call_amount, check) = Game_Helpers.get_current_raise(history, street)

        stack = stack.flatten()
        allin_arr = np.zeros(50, dtype=np.int_)
        allin = len(allin_arr) - np.argmax(stack[::-1]) - 1
        check_fold = np.zeros(2, dtype = int)
        check_fold[1] = 1

        if (check == True):
            check_fold[0] = 1

        # Allin = max raise so highest index

        allin_arr[allin] = 1

        # We can only raise when our stack has the amount

        legals = stack & minraise

        # Set Call bit, but only if we have chips

        call_size = stack & call_amount

        # Add Call to legals

        legals = legals | call_size

        # Add Allin to legals

        legals = legals | allin_arr

        if np.sum(blocking) > 0:
            legals[:] = 0
            legals = stack & blocking

            if np.argmax(allin_arr) < np.argmax(blocking):
                legals = legals | allin_arr

        legals = np.hstack((legals,check_fold))
        return legals


    @staticmethod
    def move_class(history,street, move_arr, stack):
        move_arr = array(move_arr, dtype=np.int_)
        minraise_arr, call_arr, check = Game_Helpers.get_current_raise(history, street)

        action = None
        allin = False

        allin_index = np.argmax(np.where(stack == np.max(stack)))
        if move_arr.sum() > 1:
            print("Too many moves")
            raise ValueError

        if (np.array_equal((move_arr[0:50] & minraise_arr), move_arr[0:50])):
            action = 'RAISE'
        if(np.array_equal((move_arr[0:50] & call_arr), move_arr[0:50])):
            action = 'CALL'
        if(move_arr[50] == 1):
            action = 'CHECK'
        if(move_arr[51] == 1):
            action = 'FOLD'
        if ((np.argmax(move_arr) < np.argmax(minraise_arr)) and (np.argmax(move_arr) > np.argmax(call_arr))):
            action = 'RAISE'
        if (np.argmax(move_arr) < np.argmax(call_arr)):
            action = 'CALL'
        if (np.argmax(move_arr) == allin_index):
            allin = True
        if (action == None ):
            action = 'RAISE'

        return action,allin

    @staticmethod
    def blocking_raise(move,move_arr,call_arr, minraise_arr):
        blocking = np.zeros(50)

        if (move == 'ALLIN'
                and (np.argmax(move_arr) < np.argmax(minraise_arr))
                and (np.argmax(move_arr) > np.argmax(call_arr))):
            blocking  = move_arr

        return blocking

    @staticmethod
    def get_player_invested(state):
        invested_chips_seat_1 = 0
        invested_chips_seat_2 = 0

        preflop_planes = state[8:33, :, :]
        flop_planes = state[33:58, :, :]
        turn_planes = state[58:83, :, :]
        river_planes = state[83:108, :, :]
        postflop_planes = [flop_planes, turn_planes, river_planes]

        invested_chips_seat_1 += np.max(
            preflop_planes[0::2, 0:12, 0:4].sum(-1).sum(-1) + preflop_planes[0::2, 12, 0:2].sum(-1))
        invested_chips_seat_2 += np.max(
            preflop_planes[1::2, 0:12, 0:4].sum(-1).sum(-1) + preflop_planes[1::2, 12, 0:2].sum(-1))

        for planes in postflop_planes:
            invested_chips_seat_2 += np.max(
                planes[0::2, 0:12, 0:4].sum(-1).sum(-1) + planes[0::2, 12, 0:2].sum(-1))
            invested_chips_seat_1 += np.max(
                planes[1::2, 0:12, 0:4].sum(-1).sum(-1) + planes[1::2, 12, 0:2].sum(-1))

        invested_chips_seat_1 = int(invested_chips_seat_1 * 10)
        invested_chips_seat_2 = int(invested_chips_seat_2 * 10)

        return invested_chips_seat_1, invested_chips_seat_2

    @staticmethod
    def winner(state, hand_1, hand_2):
        winner = -1
        player_1,player_2 = Game_Helpers.get_player_invested(state)

        history_planes = state[8:108, :, :]
        planes_with_actions = history_planes.sum(-1).sum(-1)
        last_action = np.max(np.argwhere(planes_with_actions > 0))
        print("last_action : ",last_action)
        board = None
        if history_planes[last_action, 12, 3] != 1:
            hand_1_score = evaluator.evaluate(hand_1,board)
            hand_2_score = evaluator.evaluate(hand_2, board)

            if hand_1_score > hand_2_score:
                winner = 1
            elif hand_1_score < hand_2_score:
                winner = 2
            else:
                winner = 0
        else:
            if last_action % 2 == 0:
                winner = 2
            else:
                winner = 1
        return winner