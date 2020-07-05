import unittest
import numpy as np

from game_static import Game_Helpers


class Legal_Moves_Test(unittest.TestCase):
    #Only Blinds are posted
    def test_just_blinds(self):
        logic = Game_Helpers()
        preflop_history = np.zeros(1300)
        preflop_history = preflop_history.reshape(25, 13, 4)
        flop_history = np.zeros(1300).reshape(25,13,4)
        turn_history = np.zeros(1300).reshape(25, 13, 4)
        river_history = np.zeros(1300).reshape(25, 13, 4)

        history_dict = {'PREFLOP': preflop_history,
                        'FLOP': flop_history,
                        'TURN': turn_history,
                        'RIVER': river_history}
        # Small Blind
        preflop_history[0, 0, 0:1] = 1
        # Big Blind
        preflop_history[1, 0, 0:2] = 1
        street = 'RIVER'
        stacks = logic.get_stack(history_dict,500,2,2,street)
        stacks2 = logic.get_stack(history_dict, 500, 1, 2,street)

        self.assertEqual(480, stacks)
        self.assertEqual(490, stacks2)

    def test_blinds_raise(self):
        logic = Game_Helpers()
        preflop_history = np.zeros(1300)
        preflop_history = preflop_history.reshape(25, 13, 4)
        flop_history = np.zeros(1300).reshape(25,13,4)
        turn_history = np.zeros(1300).reshape(25, 13, 4)
        river_history = np.zeros(1300).reshape(25, 13, 4)
        history_dict = {'PREFLOP':preflop_history,
                        'FLOP':flop_history,
                        'TURN':turn_history,
                        'RIVER':river_history}
        # Small Blind
        preflop_history[0, 0, 0:1] = 1
        # Big Blind
        preflop_history[1, 0, 0:2] = 1
        preflop_history[2, 0:12, :] = 1
        preflop_history[2,12,0:2] =1
        street = 'RIVER'
        stacks = logic.get_stack(history_dict,500,1,2,street)
        stacks2 = logic.get_stack(history_dict, 500, 2, 2,street)

        self.assertEqual(0, stacks)
        self.assertEqual(480, stacks2)

    def test_multiple_actions(self):
        logic = Game_Helpers()
        preflop_history = np.zeros(1300)
        preflop_history = preflop_history.reshape(25, 13, 4)
        flop_history = np.zeros(1300).reshape(25,13,4)
        turn_history = np.zeros(1300).reshape(25, 13, 4)
        river_history = np.zeros(1300).reshape(25, 13, 4)
        history_dict = {'PREFLOP': preflop_history,
                        'FLOP': flop_history,
                        'TURN': turn_history,
                        'RIVER': river_history}
        # Small Blind
        preflop_history[0, 0, 0:1] = 1
        # Big Blind
        preflop_history[1, 0, 0:2] = 1
        preflop_history[2, 0:2,:] = 1

        preflop_history[4, 0:6, :] = 1
        street = 'RIVER'
        stacks = logic.get_stack(history_dict,500,1,2,street)
        preflop_history[3, 0:6, :] = 1
        stacks2 = logic.get_stack(history_dict, 500, 2, 2,street)

        self.assertEqual(260, stacks, street)
        self.assertEqual(260, stacks2, street)