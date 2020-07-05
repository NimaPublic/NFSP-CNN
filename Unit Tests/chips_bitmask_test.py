import unittest
import numpy as np

from game_static import Game_Helpers

class Chips_Bitmask_Test(unittest.TestCase):
    def test_bitmask_500(self):
        logic = Game_Helpers()
        bitmask = logic.chips_bitmask(500)
        bitmask_expected = np.zeros(50)
        bitmask_expected[0:50] = 1

        self.assertEqual(bitmask_expected.tolist(), bitmask.tolist())

    def test_bitmask_600(self):
        logic = Game_Helpers()
        bitmask = logic.chips_bitmask(600)
        bitmask_expected = np.ones(50)

        self.assertEqual(bitmask_expected.tolist(), bitmask.tolist())

    def test_bitmask_417(self):
        logic = Game_Helpers()
        bitmask = logic.chips_bitmask(417)
        bitmask_expected = np.zeros(50)
        bitmask_expected[0:42] = 1

        self.assertEqual(bitmask_expected.tolist(), bitmask.tolist())

if __name__ == '__main__':
    unittest.main()
