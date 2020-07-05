import unittest
import numpy as np

from game_static import Game_Helpers


class Minraise_Call_Test(unittest.TestCase):
    #The general unit for stacks is in small blinds, e.g. if 5 bits are on 5*0.5bb = 2.5bb are bet
    #Needs some updates, some tests are laid out for more than 2 players

    #SB and BB posted (1 and 2 SB respectively)
    def test_just_blinds(self):
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        #Small Blind
        history[0, 0, 0:1] = 1
        #Big Blind
        history[1, 0, 0:2] = 1
        minraise_arr, call_size_arr,check = logic.get_current_raise(history, 'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[3:50] = 1

        call_expected = np.zeros(50, dtype=int)
        call_expected[1] = 1

        check_expected = False
        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_full_allin(self):
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        #Small Blind
        history[0, 0, 0:1] = 1
        #Big Blind
        history[1, 0, 0:2] = 1
        history[2, 0:12,:] = 1
        history[2,12,0:2] =1

        minraise_arr, call_size_arr,check = logic.get_current_raise(history, 'FLOP')
        minraise_expected = np.zeros(50, dtype=int)

        call_expected = np.zeros(50, dtype=int)
        call_expected[49] = 1

        check_expected = False
        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_no_bets(self):
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        minraise_arr, call_size_arr, check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[1:] = 1
        call_expected = np.zeros(50, dtype=int)
        check_expected = True

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    #SB and BB posted and one call of 1 BB
    #Needs to be updated, after addition of streets and checks
    def test_blinds_and_call(self):
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:2] = 1
        minraise_arr, call_size_arr, check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[3:] = 1
        call_expected = np.zeros(50, dtype=int)
        call_expected[1] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    #BLOCKING RAISE, Question is if the size should be fixed here or in the other method
    #SB and BB posted and one underraise of 3SB
    def test_blinds_and_underraise(self):
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:3] = 1
        minraise_arr, call_size_arr, check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[3:] = 1
        call_expected = np.zeros(50, dtype=int)
        call_expected[2] = 1
        check_expected = False

        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_normal_raise(self):
        #1 SB -> 2SB -> 6SB -> minraise = 10 SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2,0,0:4] = 1
        history[2,1,0:2] = 1
        minraise_arr, call_size_arr, check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50,dtype = int)
        minraise_expected[9:] = 1
        call_expected = np.zeros(50, dtype=int)
        call_expected[5] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_multiple_raise(self):
        #1 SB -> 2SB -> 6SB -> 10 SB ->16SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2,0,0:4] = 1
        history[2,1,0:2] = 1
        history[3, 0:2, 0:4] = 1
        history[3, 2, 0:2] = 1
        history[4, 0:4, 0:4] = 1
        minraise_arr, call_size_arr,check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50,dtype = int)
        minraise_expected[21:] = 1
        call_expected = np.zeros(50, dtype=int)
        call_expected[15] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_raise_one_call(self):
        # 1 SB -> 2SB -> 6SB -> 6 SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        history[2, 1, 0:2] = 1
        history[3, 0, 0:4] = 1
        history[3, 1, 0:2] = 1
        minraise_arr, call_size_arr,check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[9:] = 1
        call_expected = np.zeros(50, dtype=int)
        call_expected[5] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_raise_two_call(self):
        # 1 SB -> 2SB -> 6SB -> 6SB -> 6SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        history[2, 1, 0:2] = 1
        history[3, 0, 0:4] = 1
        history[3, 1, 0:2] = 1
        history[4, 0, 0:4] = 1
        history[4, 1, 0:2] = 1
        minraise_arr, call_size_arr, check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[9:] = 1
        call_expected = np.zeros(50, dtype=int)
        call_expected[5] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_raise_undercall(self):
        # 1 SB -> 2SB -> 6SB -> 4SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:4] = 1
        history[2, 1, 0:2] = 1
        history[3, 0, 0:4] = 1
        minraise_arr, call_size_arr, check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[9:] = 1
        call_expected = np.zeros(50 , dtype=int)
        call_expected[5] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_allin_50sbs_first_action(self):
        # 1 SB -> 2SB -> 50 SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0:12, 0:4] = 1
        history[2, 12, 0:2] = 1
        minraise_arr, call_size_arr,check = logic.get_current_raise(history,'FLOP')
        minraise_expected = np.zeros(50, dtype=int)
        call_expected = np.zeros(50, dtype=int)
        call_expected[49] = 1
        check_expected = False

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

    def test_check_preflop(self):
        # 1 SB -> 2SB -> 50 SB
        logic = Game_Helpers()
        history = np.zeros(1300)
        history = history.reshape(25, 13, 4)
        history[0, 0, 0:1] = 1
        history[1, 0, 0:2] = 1
        history[2, 0, 0:2] = 1
        minraise_arr, call_size_arr,check = logic.get_current_raise(history,'PREFLOP')
        minraise_expected = np.zeros(50, dtype=int)
        minraise_expected[3:] = 1
        call_expected = np.zeros(50, dtype=int)
        check_expected = True

        self.assertEqual(minraise_expected.tolist(),minraise_arr.tolist())
        self.assertEqual(call_expected.tolist(), call_size_arr.tolist())
        self.assertEqual(check_expected, check)

if __name__ == '__main__':
    unittest.main()
