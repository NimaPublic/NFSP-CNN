import unittest
import numpy as np

from game_static import Game_Helpers
from Game_Test import Game_Test

class Make_Move_Test(unittest.TestCase):

    #Deal Blinds, raise to 6SB then call 6SB. Check the turn

    def test_make_move_standard(self):
        game = Game_Test()
        move = np.zeros(52)
        move[5] = 1
        street = 'PREFLOP'
        move_number = 2
        game.set_blinds()
        game.make_move(move,move_number,street)

        history_flop_expected = np.zeros(1300, dtype=int).reshape(25, 13, 4)
        history_pre_expected = np.zeros(1300, dtype=int).reshape(25, 13, 4)
        history_pre_expected[0, 0, 0] = 1
        history_pre_expected[1, 0, 0:2] = 1
        history_pre_expected[2,0,:] = 1
        history_pre_expected[2,1, 0:2] = 1

        self.assertEqual(history_pre_expected.tolist(), game.preflop_history.tolist())

        move_number = 3
        game.make_move(move, move_number, street)

        history_pre_expected[3, 0, :] = 1
        history_pre_expected[3, 1, 0:2] = 1

        self.assertEqual(history_pre_expected.tolist(), game.preflop_history.tolist())

        street = 'FLOP'
        move_number = 0
        move = np.zeros(52)
        move[50] = 1
        game.make_move(move, move_number, street)
        history_flop_expected[0, 12, 2] = 1

        self.assertEqual(history_flop_expected.tolist(), game.flop_history.tolist())

        street = 'FLOP'
        move_number = 1
        move = np.zeros(52)
        move[10] = 1
        game.make_move(move, move_number, street)
        history_flop_expected[1,0:2, :] = 1
        history_flop_expected[1, 2, 0:3] = 1

        self.assertEqual(history_flop_expected.tolist(), game.flop_history.tolist())



    def test_40sb_raise(self):
        game = Game_Test()
        street = 'PREFLOP'
        move_number = 2
        move = np.zeros(52)
        move[40] = 1
        game.make_move(move, move_number, street)
        game.set_blinds()
        history_pre_expected = np.zeros(1300, dtype=int).reshape(25, 13, 4)
        history_pre_expected[0, 0, 0] = 1
        history_pre_expected[1, 0, 0:2] = 1
        history_pre_expected[2, 0:10, :] = 1
        history_pre_expected[2, 10, 0:1] = 1
        #self.maxDiff = None
        #np.testing.assert_array_equal(history_pre_expected,game.preflop_history)
        self.assertEqual(history_pre_expected.tolist(), game.preflop_history.tolist())

if __name__ == '__main__':
    unittest.main()
