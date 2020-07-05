import unittest
import numpy as np
from game_static import Game_Helpers


class Move_Class_Test(unittest.TestCase):
    def test_raise_class(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(500)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        move_arr = np.zeros(52, dtype = int)
        move_arr[8] = 1
        move_class,allin = logic.move_class(history,'PREFLOP',move_arr,stack)
        move_class_expected = 'RAISE'

        self.assertEqual(move_class_expected,move_class)
        self.assertEqual(False, allin)


    def test_allin_class(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(500)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        move_arr = np.zeros(52, dtype=int)
        move_arr[49] = 1
        move_class,allin = logic.move_class(history, 'PREFLOP', move_arr, stack)
        move_class_expected = 'RAISE'

        self.assertEqual(move_class_expected, move_class)
        self.assertEqual(True, allin)

    #allin is equal to call
    def test_allin_call_class(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(40)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        move_arr = np.zeros(52, dtype=int)
        move_arr[3] = 1
        move_class,allin = logic.move_class(history, 'PREFLOP', move_arr, stack)
        move_class_expected = 'CALL'

        self.assertEqual(move_class_expected, move_class)
        self.assertEqual(True, allin)

    def test_call_class(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(500)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        move_arr = np.zeros(52, dtype=int)
        move_arr[1] = 1
        move_class,allin = logic.move_class(history, 'PREFLOP', move_arr,stack)
        move_class_expected = 'CALL'

        self.assertEqual(move_class_expected, move_class)
        self.assertEqual(False, allin)

    def test_undercall_allin_class(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(90)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0:3,:] = 1

        move_arr = np.zeros(52, dtype=int)
        move_arr[8] = 1
        move_class,allin = logic.move_class(history, 'PREFLOP', move_arr,stack)
        move_class_expected = 'CALL'

        self.assertEqual(move_class_expected, move_class)
        self.assertEqual(True, allin)

    def test_underraise_allin_class(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(130)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0:3, :] = 1

        move_arr = np.zeros(52, dtype=int)
        move_arr[12] = 1
        move_class, allin = logic.move_class(history, 'PREFLOP', move_arr, stack)
        move_class_expected = 'RAISE'

        self.assertEqual(move_class_expected, move_class)
        self.assertEqual(True, allin)

    #gave a bug once
    def test_31sb_raise(self):
        logic = Game_Helpers()
        blocking = np.zeros(50)
        stack = logic.chips_bitmask(500)
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0:8, :] = 1
        history[2,7,3] = 0

        move_arr = np.zeros(52, dtype=int)
        move_arr[49] = 1
        move_class, allin = logic.move_class(history, 'PREFLOP', move_arr, stack)
        move_class_expected = 'RAISE'

        self.assertEqual(move_class_expected, move_class)
        self.assertEqual(True, allin)

if __name__ == '__main__':
    unittest.main()
