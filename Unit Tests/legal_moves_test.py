import unittest
import numpy as np

from game_static import Game_Helpers


class Legal_Moves_Test(unittest.TestCase):
    #Only Blinds are posted
    def test_just_blinds_covered(self):
        logic = Game_Helpers()
        blocking = np.zeros(50,dtype = int)
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        # Small Blind
        history[0, 0, 0:1] = 1
        # Big Blind
        history[1, 0, 0:2] = 1
        stack = logic.chips_bitmask(500)
        legal_moves_arr = logic.legal_moves(stack,history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[1] = 1
        legal_moves_expected[3:50] =1
        legal_moves_expected[51] = 1
        
        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

    # SB and BB posted and one call of 1 BB
    def test_blinds_and_call_covered(self):
        logic = Game_Helpers()
        blocking = np.zeros(52)
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:2] = 1
        stack = logic.chips_bitmask(500)
        legal_moves_arr = logic.legal_moves(stack, history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[3:] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

    # 1 SB -> 2SB -> 6SB -> minraise = 10 SB
    def test_normal_raise_covered(self):
        logic = Game_Helpers()
        blocking = np.zeros(52)
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        history[2, 1, 0:2] = 1
        stack = logic.chips_bitmask(500)
        legal_moves_arr = logic.legal_moves(stack, history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[5] = 1
        legal_moves_expected[9:50] = 1
        legal_moves_expected[51] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

    #seemed to be buggy for this size
    def test_37sb_raise(self):
        logic = Game_Helpers()
        blocking = np.zeros(52)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0:9, 0:4] = 1
        history[2, 9, 0:3] = 1
        stack = logic.chips_bitmask(500)
        legal_moves_arr = logic.legal_moves(stack, history, blocking, 'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[38] = 1
        legal_moves_expected[49] = 1
        legal_moves_expected[51] = 1

        self.assertEqual(legal_moves_expected.tolist(), legal_moves_arr.tolist())

    def test_normal_raise_uncovered_call_covered(self):
        # 1 SB -> 2SB -> 16SB -> minraise = 28 SB but we only have a stack of 19 SB
        logic = Game_Helpers()
        blocking = np.zeros(52)
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0:4, 0:4] = 1
        stack = logic.chips_bitmask(190)
        legal_moves_arr = logic.legal_moves(stack, history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[15] = 1
        legal_moves_expected[18] = 1
        legal_moves_expected[51] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())


    def test_blinds_underraise(self):
        # 1 SB -> 2SB -> 3 SB
        logic = Game_Helpers()
        blocking = np.zeros(50,dtype=int)
        blocking[2] = 1
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:3] = 1
        stack = logic.chips_bitmask(500)
        legal_moves_arr = logic.legal_moves(stack, history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[2] = 1
        legal_moves_expected[51] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

    def test_blinds_underraise_uncovered(self):
        # 1 SB -> 2SB -> 6 SB -> 9SB
        logic = Game_Helpers()
        blocking = np.zeros(50,dtype=int)
        blocking[8] = 1
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        history[2, 1, 0:2] = 1
        history[3, 0:2, 0:4] = 1
        history[3, 2, 0] = 1
        stack = logic.chips_bitmask(80)
        legal_moves_arr = logic.legal_moves(stack, history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[7] = 1
        legal_moves_expected[51] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())


    def test_blinds_underraise_same_stack(self):
        # 1 SB -> 2SB -> 6 SB -> 9SB
        logic = Game_Helpers()
        blocking = np.zeros(50,dtype=int)
        blocking[8] = 1
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        history[2, 1, 0:2] = 1
        history[3, 0:2, 0:4] = 1
        history[3, 2, 0] = 1
        stack = logic.chips_bitmask(90)
        legal_moves_arr = logic.legal_moves(stack, history,blocking,'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[8] = 1
        legal_moves_expected[51] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

    def test_flop_check(self):
        logic = Game_Helpers()
        # 1 SB -> 2SB -> 6SB -> 4SB
        blocking = np.zeros(52, dtype=int)
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        stack = logic.chips_bitmask(500)
        legal_moves_arr = logic.legal_moves(stack, history, blocking, 'FLOP')
        legal_moves_expected = np.ones(52)
        legal_moves_expected[0] = 0

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

    def test_8sb_45sb_raises(self):
        logic = Game_Helpers()
        # 1 SB -> 2SB -> 6SB -> 4SB
        blocking = np.zeros(52, dtype=int)
        history = np.zeros(1300)
        history = history.reshape(25 , 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2,:12,:] = 1
        stack = logic.chips_bitmask(410)
        legal_moves_arr = logic.legal_moves(stack, history, blocking, 'PREFLOP')
        legal_moves_expected = np.zeros(52)
        legal_moves_expected[40] = 1
        legal_moves_expected[51] = 1
        #legal_moves_expected[49] = 1

        self.assertEqual( legal_moves_expected .tolist(), legal_moves_arr.tolist())

if __name__ == '__main__':
    unittest.main()
