import datetime
import itertools
import math
import random
import time
from functools import reduce
from dataclasses import dataclass, field
from collections import deque
# from .models import ConstantVariable

@dataclass
class MegaCashDraw:  #Instant Cashout
    # Constants
    SHARE_RATIO = (0.4, 0.35, 0.25)
    BASE_N = 40
    PLAYS = 24000000000
    WIN_PROGRESSION_FACTOR = 0.833  # (unused, but kept)

    # State variables
    TOTAL_CONTRIBUTION: int = 0
    RUNNING_BALANCE: int = 0
    BATCH_CONTRIBUTION: int = 0
    BATCH: int = 0
    SURGE: bool = False
    BASE_PPS: float = 0
    MOST_RECENT_ELAPSED_TIME: float = 0

    # Store play times efficiently (rolling window of last N)
    # play_times: deque = deque(maxlen=BASE_N)
    play_times: deque = field(default_factory=deque)

    # WINNINGS table
    WINNINGS = {
        150: {"min_win": 4500, "mid_win": 5400, "max_win": 11250},
        300: {"min_win": 7500, "mid_win": 9000, "max_win": 13500},
        450: {"min_win": 9000, "mid_win": 10800, "max_win": 15750},
        600: {"min_win": 10800, "mid_win": 13000, "max_win": 18000},
        750: {"min_win": 12000, "mid_win": 14000, "max_win": 18750},
        900: {"min_win": 13500, "mid_win": 16000, "max_win": 22500},
        1000: {"min_win": 15000, "mid_win": 18000, "max_win": 25000},
    }

    def __post_init__(self):
        # Precompute totals for efficiency
        for band, vals in self.WINNINGS.items():
            vals["total_possible_for_3"] = sum(vals.values())
            vals["total_possible_for_2"] = vals["min_win"] + vals["mid_win"]

        self.AVAILABLE_BANDS = list(self.WINNINGS.keys())

        # Build skew list for payouts
        seed = [1, 1, 1, 3, 5, 6, 10]
        random.shuffle(seed)
        skew = [[band] * seed_val for seed_val, band in zip(seed, self.AVAILABLE_BANDS)]
        self.skew_list = reduce(lambda l1, l2: l1 + l2, skew)

        # Tracks plays per band
        self.PLAYS_LIST = {}

    def sharemonies(self, bands, share_values) -> dict:
        """Distribute share_values across band tiers."""

        print("....SHARING MONIES ....")
        winners, balance = [], 0

        for band, share in zip(bands, share_values):
            # print("SHARE-BALANCE ::", share, "-", balance)
            share += balance
            payouts = self.WINNINGS[band]

            # print(f"{band} PAYOUT :::", payout_to_band_tiers)
            if share > payouts["total_possible_for_3"]:
                balance = share - payouts["total_possible_for_3"]
                winners.extend([(k, band, v) for k, v in payouts.items() if "win" in k])

            elif share > payouts["total_possible_for_2"]:
                balance = share - payouts["total_possible_for_2"]
                winners.append(("min_win", band, payouts["min_win"]))
                winners.append(("mid_win", band, payouts["mid_win"]))

            elif share > payouts["min_win"]:
                balance = share - payouts["min_win"]
                winners.append(("min_win", band, payouts["min_win"]))

            else:
                return {
                    "requesting_for_2": True,
                    "winners": winners,
                    "balance": balance,
                }

        return {"requesting_for_2": False, "winners": winners, "balance": balance}

    def draw(self):
        """Simulates the plays with timing + payouts."""
        try:
            # Load time delay once
            with open("variables.txt", "r") as f:
                time_delay = float(f.read().strip() or 1)
        except FileNotFoundError:
            time_delay = 1

        for _ in range(self.PLAYS):
            # Track play timing
            now = datetime.datetime.now()
            self.play_times.append(now)
            time.sleep(time_delay)

            # Simulate play
            picks = random.sample(range(1, 41), 4)
            play = random.choice(self.skew_list)
            self.TOTAL_CONTRIBUTION += play
            self.BATCH_CONTRIBUTION += play
            self.PLAYS_LIST[play] = self.PLAYS_LIST.get(play, 0) + 1
            self.BATCH += 1

            print(
                f"#{self.BATCH}",
                play,
                picks,
                "->",
                self.TOTAL_CONTRIBUTION,
                self.BATCH_CONTRIBUTION,
            )

            # Every N plays or surge → evaluate payouts
            if self.BATCH >= self.BASE_N or self.SURGE:
                time_elapsed = self.play_times[-1] - self.play_times[0]
                play_freq = self.BASE_N / time_elapsed.total_seconds()

                # Prepare bands & shares
                payout_bands = sorted(
                    random.sample(self.AVAILABLE_BANDS, 3), reverse=True
                )
                share_values = sorted(
                    [r * self.BATCH_CONTRIBUTION for r in self.SHARE_RATIO],
                    reverse=True,
                )

                result = self.sharemonies(payout_bands, share_values)
                print("PAYOUT RESULT:", result)

                if result.get("requesting_for_2"):
                    share_values[1] += share_values[0] * 0.6
                    share_values[2] += share_values[0] * 0.4
                    result = self.sharemonies(payout_bands[1:], share_values[1:])
                    print("ADJUSTED PAYOUT RESULT:", result)

                self.RUNNING_BALANCE = result.get("balance", 0)
                if not result["winners"]:
                    self.RUNNING_BALANCE = self.BATCH_CONTRIBUTION

                # Adjust N dynamically based on frequency
                if not self.BASE_PPS:
                    self.BASE_PPS = play_freq
                else:
                    pps_delta = play_freq / self.BASE_PPS
                    self.BASE_N = max(1, int(self.BASE_N * pps_delta))

                print(
                    f"Batch finished: {len(result['winners'])} winners, "
                    f"{round(time_elapsed.total_seconds(), 2)}s elapsed, "
                    f"{round(play_freq, 2)} plays/sec"
                )

                self.BATCH_CONTRIBUTION = 0

        return self.TOTAL_CONTRIBUTION


class ConstantVariable:
    """Stub for Django ConstantVariable.objects.last()"""

    def __init__(self):
        self.restrict_s4l_to_lower_wins = False
        self.max_s4l_single_win_to_rtp = 10
        self.s4l_number_of_match_limit = 2
        self.limit_wining_amount = False

    @classmethod
    def objects(cls):
        return cls()

    def all(self):
        return self

    def last(self):
        return ConstantVariable()

    def save(self):
        return None


# class SalaryForLifeDraw:
#     @staticmethod
#     def _generate_winning_combo():
#         """Generate 5 unique numbers from 1–49 without computing all combinations."""
#         return random.sample(range(1, 50), 5)

#     @staticmethod
#     def _get_const_obj():
#         """Fetch ConstantVariable once and reuse."""
#         return ConstantVariable.objects.all().last()

#     @staticmethod
#     def _process_play(play, combo, line_prices, jackpot_amount, rtp, banker=False):
#         """Process one play and return potential winnings."""
#         # Count matches
#         matched_count = search_number_occurences(play, combo)

#         # Compute potential winnings
#         if banker:
#             win_amount = get_banker_potential_winning(
#                 matched_count, line_prices, rtp, jackpot_amount
#             )
#         else:
#             win_amount = get_potential_winning(
#                 matched_count, line_prices, rtp, jackpot_amount
#             )

#         return win_amount, matched_count

#     @staticmethod
#     def _filter_winnings(winnings, rtp, const_obj):
#         """Apply ConstantVariable rules to winnings list."""
#         filtered = []
#         for play, amt, matches in winnings:
#             if amt <= 0:
#                 continue

#             # Cap by RTP if needed
#             if const_obj.restrict_max_winnings and amt > rtp:
#                 continue

#             # Restrict to lower tiers if enabled
#             if const_obj.restrict_wins and matches > 3:
#                 continue

#             filtered.append((play, amt, matches))
#         return filtered

#     @staticmethod
#     def _pick_winner(winnings, combo, rtp, banker=False):
#         """Select the best winner from potential winnings."""
#         if not winnings:
#             return {
#                 "combination": combo,
#                 "winning": "No Winner",
#                 "winning_play": [],
#                 "winning_amount": 0,
#                 "winnings": [],
#                 "rtp": rtp,
#                 "banker": banker,
#             }

#         # Pick the highest amount
#         play, amt, matches = max(winnings, key=lambda x: x[1])

#         return {
#             "combination": combo,
#             "winning": f"Matched {matches} numbers",
#             "winning_play": play,
#             "winning_amount": amt,
#             "winnings": winnings,
#             "rtp": rtp,
#             "banker": banker,
#         }

#     @classmethod
#     def draw(cls, plays, rtp, line_prices, jackpot_amount, disburse_jackpot=False):
#         """Regular draw method."""
#         combo = cls._generate_winning_combo()
#         const_obj = cls._get_const_obj()
#         # const_obj

#         winnings = []
#         for play in plays:
#             amt, matches = cls._process_play(
#                 play, combo, line_prices, jackpot_amount, rtp, banker=False
#             )
#             winnings.append((play, amt, matches))

#         filtered = cls._filter_winnings(winnings, rtp, const_obj)
#         return cls._pick_winner(filtered, combo, rtp, banker=False)

#     @classmethod
#     def banker_decisioning(
#         cls, plays, rtp, line_prices, jackpot_amount, disburse_jackpot=False
#     ):
#         """Banker draw method."""
#         combo = cls._generate_winning_combo()
#         const_obj = cls._get_const_obj()

#         winnings = []
#         for play in plays:
#             amt, matches = cls._process_play(
#                 play, combo, line_prices, jackpot_amount, rtp, banker=True
#             )
#             winnings.append((play, amt, matches))

#         filtered = cls._filter_winnings(winnings, rtp, const_obj)
#         return cls._pick_winner(filtered, combo, rtp, banker=True)



# # bands = [150, 300, 450]
# # share_values = [10000, 20000, 30000]

# # test = MegaCashDraw().sharemonies(bands=bands, share_values=share_values)
# # print(test)


# # import random

# # ===============================
# # Stub Functions (Mocks)
# # ===============================

# def search_number_occurences(play, combo):
#     """Return how many numbers match between play and combo."""
#     return len(set(play) & set(combo))

# def get_potential_winning(matches, line_prices, rtp, jackpot_amount):
#     """Return winnings for a regular player (very simplified)."""
#     if matches < 2:
#         return 0
#     if matches == 5:
#         return jackpot_amount
#     return line_prices[matches - 2] * matches  # just a mock formula

# def get_banker_potential_winning(matches, line_prices, rtp, jackpot_amount):
#     """Return winnings for banker mode (different rule)."""
#     if matches < 2:
#         return 0
#     if matches == 5:
#         return int(jackpot_amount * 0.8)  # banker pays less on jackpot
#     return line_prices[matches - 2] * matches * 2  # banker doubles payouts


# # ===============================
# # Mock ConstantVariable
# # ===============================


# class ConstantVariable:
#     """Stub for Django ConstantVariable.objects.last()"""

#     def __init__(self):
#         self.restrict_s4l_to_lower_wins = False
#         self.max_s4l_single_win_to_rtp = 10
#         self.s4l_number_of_match_limit = 2
#         self.limit_wining_amount = False
#         self.restrict_max_winnings = False
#         self.restrict_wins = False

#     @classmethod
#     def objects(cls):
#         return cls()

#     def all(self):
#         return self

#     def last(self):
#         return ConstantVariable()

#     def save(self):
#         return None

# # # ===============================
# # # SteadyWinDraw Class
# # # ===============================

# class SteadyWinDraw:
#     @staticmethod
#     def _generate_winning_combo():
#         """Generate 5 unique numbers from 1–49 without computing all combinations."""
#         return random.sample(range(1, 50), 5)

#     @staticmethod
#     def _get_const_obj():
#         """Fetch ConstantVariable once and reuse."""
#         return ConstantVariable.objects().last()

#     @staticmethod
#     def _process_play(play, combo, line_prices, jackpot_amount, rtp, banker=False):
#         """Process one play and return potential winnings."""
#         # Count matches
#         matched_count = search_number_occurences(play, combo)

#         # Compute potential winnings
#         if banker:
#             win_amount = get_banker_potential_winning(
#                 matched_count, line_prices, rtp, jackpot_amount
#             )
#         else:
#             win_amount = get_potential_winning(
#                 matched_count, line_prices, rtp, jackpot_amount
#             )

#         return win_amount, matched_count

#     @staticmethod
#     def _filter_winnings(winnings, rtp, const_obj):
#         """Apply ConstantVariable rules to winnings list."""
#         filtered = []
#         for play, amt, matches in winnings:
#             if amt <= 0:
#                 continue

#             # Cap by RTP if needed
#             if const_obj.restrict_max_winnings and amt > rtp:
#                 continue

#             # Restrict to lower tiers if enabled
#             if const_obj.restrict_wins and matches > 3:
#                 continue

#             filtered.append((play, amt, matches))
#         return filtered

#     @staticmethod
#     def _pick_winner(winnings, combo, rtp, banker=False):
#         """Select the best winner from potential winnings."""
#         if not winnings:
#             return {
#                 "combination": combo,
#                 "winning": "No Winner",
#                 "winning_play": [],
#                 "winning_amount": 0,
#                 "winnings": [],
#                 "rtp": rtp,
#                 "banker": banker,
#             }

#         # Pick the highest amount
#         play, amt, matches = max(winnings, key=lambda x: x[1])

#         return {
#             "combination": combo,
#             "winning": f"Matched {matches} numbers",
#             "winning_play": play,
#             "winning_amount": amt,
#             "winnings": winnings,
#             "rtp": rtp,
#             "banker": banker,
#         }

#     @classmethod
#     def draw(cls, plays, rtp, line_prices, jackpot_amount, disburse_jackpot=False):
#         """Regular draw method."""
#         combo = cls._generate_winning_combo()
#         const_obj = cls._get_const_obj()

#         winnings = []
#         for play in plays:
#             amt, matches = cls._process_play(
#                 play, combo, line_prices, jackpot_amount, rtp, banker=False
#             )
#             winnings.append((play, amt, matches))

#         filtered = cls._filter_winnings(winnings, rtp, const_obj)
#         return cls._pick_winner(filtered, combo, rtp, banker=False)

#     @classmethod
#     def banker_decisioning(
#         cls, plays, rtp, line_prices, jackpot_amount, disburse_jackpot=False
#     ):
#         """Banker draw method."""
#         combo = cls._generate_winning_combo()
#         const_obj = cls._get_const_obj()

#         winnings = []
#         for play in plays:
#             amt, matches = cls._process_play(
#                 play, combo, line_prices, jackpot_amount, rtp, banker=True
#             )
#             winnings.append((play, amt, matches))

#         filtered = cls._filter_winnings(winnings, rtp, const_obj)
#         return cls._pick_winner(filtered, combo, rtp, banker=True)


# # ===============================
# # Run Simulation
# # ===============================

# if __name__ == "__main__":
#     plays = [
#         random.sample(range(1, 50), 5) for _ in range(100)  # simulate 100 player tickets
#     ]
#     rtp = 10000
#     line_prices = [100, 200, 500, 1000]
#     jackpot_amount = 1_000_000

#     print("🎲 Regular Draw:")
#     print(SalaryForLifeDraw.draw(plays, rtp, line_prices, jackpot_amount))

#     print("\n🏦 Banker Decisioning:")
#     print(SalaryForLifeDraw.banker_decisioning(plays, rtp, line_prices, jackpot_amount))



































# ==================================================
# INITIAL LOGIC FOR MEGACASH DRAW AND STEADYWIN DRAW
# ==================================================



# @dataclass
#instancashout class
# class MegaCashDraw:
#     TOTAL_CONTRIBUTION = 0
#     RUNNING_BALANCE = 0
#     BATCH_CONTRIBUTION = 0

#     SHARE_RATIO = 0.4, 0.35, 0.25

#     PLAYS = 24000000000
#     BASE_N = 40
#     N = 40
#     BASE_PPS = 0  # BASE PLAYS PER SECOND
#     MOST_RECENT_ELAPSED_TIME = 0
#     BATCH = 0
#     SURGE = False

#     PLAYS_LIST = {}

#     sub_batch_time_elaspsed = 0

#     WIN_PROGRESSION_FACTOR = 0.833  # moving factor for winning from 3/4 -> 4/4 match

#     play_times = []

#     WINNINGS = {
#         150: {"min_win": 4500, "mid_win": 5400, "max_win": 11250},
#         300: {"min_win": 7500, "mid_win": 9000, "max_win": 13500},
#         450: {"min_win": 9000, "mid_win": 10800, "max_win": 15750},
#         600: {"min_win": 10800, "mid_win": 13000, "max_win": 18000},
#         750: {"min_win": 12000, "mid_win": 14000, "max_win": 18750},
#         900: {"min_win": 13500, "mid_win": 16000, "max_win": 22500},
#         1000: {"min_win": 15000, "mid_win": 18000, "max_win": 25000},
#     }

#     for band in WINNINGS.keys():
#         band_winning_values = list(WINNINGS[band].values())

#         WINNINGS[band]["total_possible_for_3"] = sum(band_winning_values)
#         WINNINGS[band]["total_possible_for_2"] = band_winning_values[0] + band_winning_values[1]

#     AVAILABLE_BANDS = list(WINNINGS.keys())

#     seed = [1, 1, 1, 3, 5, 6, 10]
#     random.shuffle(seed)
#     skew = [[band] * seed_val for seed_val, band in zip(seed, AVAILABLE_BANDS)]
#     skew_list = reduce(lambda l1, l2: l1 + l2, skew)

#     PAYOUTS = dict(WINNINGS.items())

#     def sharemonies(self, bands, share_values) -> dict:
#         print("....SHARING MONIES ....")

#         bands_n_shares = zip(bands, share_values)
#         winnin_tiers = []
#         print(bands, share_values)
#         BALANCE = 0

#         for band, share in bands_n_shares:
#             print("SHARE-BALANCE ::", share, "-", BALANCE)
#             share = share + BALANCE
#             payout_to_band_tiers = self.WINNINGS[band]

#             print(f"{band} PAYOUT :::", payout_to_band_tiers)

#             if share > payout_to_band_tiers["total_possible_for_3"]:
#                 BALANCE = share - (payout_to_band_tiers["min_win"] + payout_to_band_tiers["mid_win"] + payout_to_band_tiers["max_win"])

#                 winnin_tiers.append(("min_win", band, payout_to_band_tiers["min_win"]))
#                 winnin_tiers.append(("mid_win", band, payout_to_band_tiers["mid_win"]))
#                 winnin_tiers.append(("max_win", band, payout_to_band_tiers["max_win"]))

#             elif share > payout_to_band_tiers["total_possible_for_2"]:
#                 BALANCE = share - (payout_to_band_tiers["min_win"] + payout_to_band_tiers["mid_win"])
#                 winnin_tiers.append(("min_win", band, payout_to_band_tiers["min_win"]))
#                 winnin_tiers.append(("mid_win", band, payout_to_band_tiers["mid_win"]))

#             elif share > payout_to_band_tiers["min_win"]:
#                 BALANCE = share - (payout_to_band_tiers["min_win"])
#                 winnin_tiers.append(("min_win", band, payout_to_band_tiers["min_win"]))

#             else:
#                 print("BALANCE ::", BALANCE)
#                 return dict(requesting_for_2=True, winners=winnin_tiers, balance=BALANCE)

#         print("BALANCE ::", BALANCE)

#         return dict(requesting_for_2=False, winners=winnin_tiers, balance=BALANCE)

#     def draw(self):
#         for i in range(self.PLAYS):
#             self.play_times.append(datetime.datetime.now())

#             time_delay = open("variables.txt", "r").read() or 1
#             time.sleep(float(time_delay))

#             picks = random.sample(range(1, 41), 4)

#             play = random.choice(self.skew_list)
#             self.TOTAL_CONTRIBUTION += play
#             self.BATCH_CONTRIBUTION += play

#             band_play = self.PLAYS_LIST.get(play, 0)

#             if band_play:
#                 self.PLAYS_LIST[play] += 1
#             else:
#                 self.PLAYS_LIST[play] = 1

#             print(
#                 f"#{self.BATCH}",
#                 play,
#                 picks,
#                 "---->",
#                 self.TOTAL_CONTRIBUTION,
#                 self.BATCH_CONTRIBUTION,
#             )
#             self.BATCH += 1

#             if self.BATCH in list(range(0, int(self.N) + 1, 5)) and self.MOST_RECENT_ELAPSED_TIME != 0:
#                 play_times_recent_N_section = self.play_times[int(-self.BATCH) :]
#                 sub_batch_time_elaspsed: datetime.timedelta = play_times_recent_N_section[-1] - play_times_recent_N_section[0]

#                 if sub_batch_time_elaspsed.total_seconds() > self.MOST_RECENT_ELAPSED_TIME * 1.1:
#                     print(
#                         "BATCH TIMES: ",
#                         sub_batch_time_elaspsed.total_seconds(),
#                         self.MOST_RECENT_ELAPSED_TIME * 1.5,
#                     )
#                     print("OOUPS SURGE..!!!", "BATCH : ", -self.BATCH)

#                     if self.BATCH >= self.BASE_N:
#                         pass

#                 else:
#                     pass

#             ":::::::::::::"
#             if self.BATCH >= self.N or self.SURGE:
#                 print("BREAKING FROM BATCH")
#                 print("N=", self.N, "BATCH=", self.BATCH)
#                 # batch_play_times_recent_N_section = self.play_times[int(-self.BATCH) :]
#                 # batch_time_elaspsed: datetime.timedelta = batch_play_times_recent_N_section[-1] - batch_play_times_recent_N_section[0]
#                 # print(batch_play_times_recent_N_section[0])
#                 # print(batch_play_times_recent_N_section[-1])

#                 play_times_recent_N_section = self.play_times[int(-self.BATCH) :]
#                 time_elaspsed: datetime.timedelta = play_times_recent_N_section[-1] - play_times_recent_N_section[0]
#                 play_frequency = self.N / time_elaspsed.total_seconds()
#                 time_elaspsed.total_seconds()

#                 random.shuffle(self.AVAILABLE_BANDS)
#                 print("AVAILABLE_BANDS ::", self.AVAILABLE_BANDS)

#                 [[key] * value for key, value in self.PLAYS_LIST.items()]
#                 payout_skew_list = reduce(lambda l1, l2: l1 + l2, self.skew)
#                 print("NORMALIZED_PAY : ", payout_skew_list)

#                 while True:
#                     payout_bands = random.sample(payout_skew_list, 3)
#                     if len(set(payout_bands)) == 3:
#                         break

#                 payout_bands = sorted(payout_bands)

#                 print(payout_bands)
#                 print("ORIGINAL CONTRIB:::", self.BATCH_CONTRIBUTION)
#                 print("RUNNING_BALANCE:::", self.RUNNING_BALANCE)
#                 self.BATCH_CONTRIBUTION += self.RUNNING_BALANCE
#                 print("UPDATED CONTRIB:::", self.BATCH_CONTRIBUTION)

#                 SHARE_VALUES = (
#                     self.SHARE_RATIO[0] * self.BATCH_CONTRIBUTION,
#                     self.SHARE_RATIO[1] * self.BATCH_CONTRIBUTION,
#                     self.SHARE_RATIO[2] * self.BATCH_CONTRIBUTION,
#                 )

#                 print("SHARE VALUES : ", SHARE_VALUES)
#                 print("BATCH CONTRIB : ", self.BATCH_CONTRIBUTION)

#                 print(self.PLAYS_LIST)
#                 payout_bands = sorted(payout_bands, reverse=True)
#                 SHARE_VALUES = sorted(SHARE_VALUES, reverse=True)

#                 share_money_result = self.sharemonies(payout_bands, SHARE_VALUES)

#                 print("::::SHARE RES::::", share_money_result)
#                 print(f"""\n\n# {len(share_money_result["winners"])}WINNERS #\n\n""")

#                 if share_money_result.get("requesting_for_2"):
#                     print("\n\n:::::::::::::REQUESTED FOR 2::::::::::::::\n]\n")

#                     SHARE_VALUES[1] = SHARE_VALUES[1] + SHARE_VALUES[0] * 0.6
#                     SHARE_VALUES[2] = SHARE_VALUES[2] + SHARE_VALUES[0] * 0.4

#                     share_money_result = self.sharemonies(
#                         [payout_bands[1], payout_bands[2]],
#                         [SHARE_VALUES[1], SHARE_VALUES[2]],
#                     )
#                     print(f"""\n\n# {len(share_money_result["winners"])}WINNERS #\n\n""")

#                     print(
#                         "SHARE AFTER RESOLVE\n\n",
#                         [payout_bands[1], payout_bands[2]],
#                         [SHARE_VALUES[1], SHARE_VALUES[2]],
#                     )

#                 RUNNING_BALANCE = share_money_result.get("balance", 0)
#                 print(
#                     "\n\n\n=============================\nSHARES ::\n\n\n",
#                     share_money_result,
#                     "\n\n\n",
#                 )
#                 if share_money_result.get("winners") == []:
#                     RUNNING_BALANCE = self.BATCH_CONTRIBUTION

#                 print("RUNNING_BALANCE::::", RUNNING_BALANCE)

#                 if self.BASE_PPS == 0:
#                     self.BASE_PPS = play_frequency
#                 else:
#                     pps_delta = play_frequency / self.BASE_PPS
#                     NEW_N = self.BASE_N * pps_delta
#                     N = NEW_N if self.BASE_N < NEW_N else self.BASE_N

#                     # if SURGE:
#                     #     N = BATCH if BASE_N < BATCH else BASE_N
#                     print("DELTA : ", (pps_delta), "%")
#                     print("N : ", N, "players")

#                 print("BATCH REACHED")
#                 print(play_times_recent_N_section[0])
#                 print(play_times_recent_N_section[-1])
#                 print(round(time_elaspsed.total_seconds(), 2), "Secs")

#                 if self.sub_batch_time_elaspsed:
#                     print(round(sub_batch_time_elaspsed.total_seconds(), 2), "Secs @batch")

#                 print(play_frequency, "ps/sec", end="\n\n")

#                 if self.SURGE:
#                     input("Surge please press enter")

#                 self.BATCH_CONTRIBUTION = 0
#             # if BATCH/N > 0: # IF THE THRESHOLD N VALUE HAS BEEN MET IN TERMS OF NUMBER OF PLAYS

#             #     print("TIME TO ATTEMPT PAYOUT")
#             # print(play, picks)

#         print(self.TOTAL_CONTRIBUTION)
#         return self.TOTAL_CONTRIBUTION







# class SalaryForLifeDraw:
#     @staticmethod
#     def draw(plays, rtp, line_prices, jackpot_amount, disburse_jackpot=False) -> dict:
#         random_combo = list(itertools.combinations(range(1, 50), 5))
#         random.shuffle(random_combo)
#         const_obj = ConstantVariable.objects.all().last()
#         best_match = 0
#         best_winners = 0
#         best_match_combo = []

#         datetime.datetime.now()

#         restrict_or_not = const_obj.restrict_s4l_to_lower_wins
#         max_win_lim_ratio = const_obj.max_s4l_single_win_to_rtp

#         best_match_with_jkpt = 0
#         best_match_with_jkpt_combo = []

#         best_match_witho_jkpt = 0
#         best_match_witho_jkpt_combo = []

#         # print(line_prices)

#         # for combo in plays:
#         #     print(combo)
#         # for index, combo in enumerate(random_combo):

#         #     occurences = map(
#         #         lambda user_play: search_number_occurences(combo, user_play), plays
#         #     )  # CHECK FOR HOW MANY NUMBERS MATCH FOR EVERY COMBINATION IN LIST OF NUMBERS

#         #     play_occurences = zip(
#         #         occurences, plays
#         #     )  # Match number of occurences to number of matches found in selected combination
#         #     over3ocurrences = list(
#         #         filter(lambda x: x[0], play_occurences)
#         #     )  # FILTER ALL VALUES THAT ARE NOT 3 AND ABOVE (FILTER WITH FALSE)

#         #     play_occurences_with_amount = map(
#         #         lambda played: get_potential_winning(
#         #             played, line_prices, jackpot_amount
#         #         ),
#         #         over3ocurrences,
#         #     )

#         #     total_sum = 0
#         #     play_occurences_with_amount = list(play_occurences_with_amount)
#         #     # CALCULATE THE TOTAL WINNING AMOUNT
#         #     for index, ocurrence in enumerate(play_occurences_with_amount):
#         #         total_sum += ocurrence[-1]

#         #     has_jkpt = bool(
#         #         list(filter(lambda x: x[0] == 5, play_occurences_with_amount))
#         #     )
#         #     match = total_sum / rtp * 100

#         #     # print("TOTAL SUM ::", total_sum, "RTP ::", rtp)

#         #     # if match > 95 and match < 105:
#         #     #     input()

#         #     # if match > best_match and match < 100:

#         #     if match > best_match and match < 100:
#         #         best_match = match
#         #         best_match_combo = combo
#         #         best_total_sum = total_sum
#         #     if match > best_match_with_jkpt and match < 100 and has_jkpt:
#         #         best_match_with_jkpt = match
#         #         best_match_with_jkpt_combo = combo
#         #     if match > best_match_witho_jkpt and match < 100 and (not has_jkpt):
#         #         best_match_witho_jkpt = match
#         #         best_match_witho_jkpt_combo = combo

#         for index, combo in enumerate(random_combo):
#             occurences = map(
#                 lambda user_play: search_number_occurences(
#                     combo, user_play, const_obj.s4l_number_of_match_limit
#                 ),
#                 plays,
#             )  # CHECK FOR HOW MANY NUMBERS MATCH FOR EVERY COMBINATION IN LIST OF NUMBERS

#             play_occurences = zip(
#                 occurences, plays
#             )  # Match number of occurences to number of matches found in selected combination
#             over3ocurrences = list(
#                 filter(lambda x: x[0], play_occurences)
#             )  # FILTER ALL VALUES THAT ARE NOT 3 AND ABOVE (FILTER WITH FALSE)

#             # NOW FILTER HAS BEEN ALTERED TO ALLOW 2 AND ABOVE WIN COMBOs

#             play_occurences_with_amount = map(
#                 lambda played: get_potential_winning(
#                     played, line_prices, jackpot_amount
#                 ),
#                 over3ocurrences,
#             )

#             total_sum = 0
#             play_occurences_with_amount = list(play_occurences_with_amount)
#             # CALCULATE THE TOTAL WINNING AMOUNT
#             for index, ocurrence in enumerate(play_occurences_with_amount):
#                 total_sum += ocurrence[-1]

#                 if rtp / ocurrence[-1] < max_win_lim_ratio:
#                     total_sum = 99999999999
#                     break

#             if total_sum >= 99999999999:
#                 continue

#             has_jkpt = bool(
#                 list(filter(lambda x: x[0] == 5, play_occurences_with_amount))
#             )
#             match = total_sum / rtp * 100
#             winners = len(over3ocurrences)

#             # if match > 10 and match < 100 and len(over3ocurrences) >= 3: print(match, "-->", winners, "-->", int(match*winners))

#             # print("TOTAL SUM ::", total_sum, "RTP ::", rtp)

#             # if match > 95 and match < 105:
#             #     input()

#             # if match > best_match and match < 100:

#             if (winners >= best_winners or match > best_match) and match < 100:
#                 if winners == best_winners and match < best_match and restrict_or_not:
#                     # print("SWITCHING MATCH :::", best_match, "-->", match)
#                     # print("SWITCHING WINN :::", best_winners, "-->", winners)
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo

#                 elif winners > best_winners:
#                     # print("SWITCHING MATCH :::", best_match, "-->", match)
#                     # print("SWITCHING WINN :::", best_winners, "-->", winners)
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo

#                 elif best_winners == 0:
#                     # print("SWITCHING MATCH :::", best_match, "-->", match)
#                     # print("SWITCHING WINN :::", best_winners, "-->", winners)
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo

#                 if match > best_match and winners >= best_winners:
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo

#             # if match < 20:win_n_matches.append((int(best_match), best_winners))

#             if match > best_match_with_jkpt and match < 20 and has_jkpt:
#                 best_match_with_jkpt = match
#                 best_match_with_jkpt_combo = combo
#             if match > best_match_witho_jkpt and match < 20 and (not has_jkpt):
#                 best_match_witho_jkpt = match
#                 best_match_witho_jkpt_combo = combo

#         #     with open("s4ldraw.txt", "a") as file:
#         #         file.write(f"TIME :: {now.strftime('%d-%m %H:%M')}, BEST MATCH ::{best_match}, MATCH ::{match}, COMBO ::{best_match_combo} , TOTAL SUM ::{best_total_sum}\n")

#         # print("BEST MATCH ::", best_match, "MATCH ::", match, "COMBO ::", best_match_combo , "TOTAL SUM ::", best_total_sum)

#         # prices = SalaryForLifeDraw.filter_winnings(best_match_combo, plays, line_prices, jackpot_amount)
#         # from pprint import pprint

#         # pprint(prices)

#         return dict(
#             best_match=best_match,
#             best_match_combo=best_match_combo,
#             best_match_with_jkpt=best_match_with_jkpt,
#             best_match_with_jkpt_combo=best_match_with_jkpt_combo,
#             best_match_witho_jkpt=best_match_witho_jkpt,
#             best_match_witho_jkpt_combo=best_match_witho_jkpt_combo,
#         )

#     @staticmethod
#     def banker_decisioning(
#         plays, rtp, line_prices, jackpot_amount, disburse_jackpot=False
#     ) -> dict:
#         # print(":::::::::::NEW-TP:::", rtp)
#         print(plays)
#         random_combo = list(itertools.combinations(range(1, 49), 5))
#         random.shuffle(random_combo)
#         const_obj = ConstantVariable.objects.all().last()
#         best_match = 0
#         best_winners = 0
#         best_match_combo = []

#         LIMIT_WINING_AMOUNT = const_obj.limit_wining_amount
#         const_obj.limit_wining_amount = not const_obj.limit_wining_amount
#         const_obj.save()
#         # print(LIMIT_WINING_AMOUNT , "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
#         restrict_or_not = const_obj.restrict_s4l_to_lower_wins
#         max_win_lim_ratio = const_obj.max_s4l_single_win_to_rtp

#         best_match_with_jkpt = 0
#         best_match_with_jkpt_combo = []

#         best_match_witho_jkpt = 0
#         best_match_witho_jkpt_combo = []

#         best_total_sum = 0
#         for combo in plays:
#             print(combo)

#         for index, combo in enumerate(random_combo):
#             occurences = map(
#                 lambda user_play: search_number_occurences(
#                     combo, user_play, const_obj.s4l_number_of_match_limit
#                 ),
#                 plays,
#             )  # CHECK FOR HOW MANY NUMBERS MATCH FOR EVERY COMBINATION IN LIST OF NUMBERS

#             play_occurences = zip(
#                 occurences, plays
#             )  # Match number of occurences to number of matches found in selected combination
#             over3ocurrences = list(
#                 filter(lambda x: x[0], play_occurences)
#             )  # FILTER ALL VALUES THAT ARE NOT 3 AND ABOVE (FILTER WITH FALSE)

#             # NOW FILTER HAS BEEN ALTERED TO ALLOW 2 AND ABOVE WIN COMBOs

#             play_occurences_with_amount = map(
#                 lambda played: get_banker_potential_winning(
#                     played, line_prices, jackpot_amount, ticket_rtp=played[1][2]
#                 ),
#                 over3ocurrences,
#             )

#             # for ticket in play_occurences_with_amount:
#             #     print(ticket)

#             total_sum = 0
#             play_occurences_with_amount = list(play_occurences_with_amount)
#             # CALCULATE THE TOTAL WINNING AMOUNT
#             for index, ocurrence in enumerate(play_occurences_with_amount):
#                 if LIMIT_WINING_AMOUNT:
#                     break

#                 total_sum += ocurrence[-1]

#                 if rtp / ocurrence[-1] < max_win_lim_ratio:
#                     total_sum = 99999999999
#                     break

#             if total_sum >= 99999999999:
#                 continue

#             has_jkpt = bool(
#                 list(filter(lambda x: x[0] == 5, play_occurences_with_amount))
#             )
#             match = total_sum / rtp * 100
#             winners = len(over3ocurrences)

#             if (winners >= best_winners or match > best_match) and match < 100:
#                 # print("MATCH ::#:: ", match)

#                 if winners == best_winners and match < best_match and restrict_or_not:
#                     # print("SWITCHING MATCH :::", best_match, "-->", match)
#                     # print("SWITCHING WINN :::", best_winners, "-->", winners)
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo
#                     best_total_sum = total_sum

#                 elif winners > best_winners:
#                     # print("SWITCHING MATCH :::", best_match, "-->", match)
#                     # print("SWITCHING WINN :::", best_winners, "-->", winners)
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo
#                     best_total_sum = total_sum

#                 elif best_winners == 0:
#                     # print("SWITCHING MATCH :::", best_match, "-->", match)
#                     # print("SWITCHING WINN :::", best_winners, "-->", winners)
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo
#                     best_total_sum = total_sum

#                 if match > best_match and winners >= best_winners:
#                     best_match = match
#                     best_winners = winners
#                     best_match_combo = combo
#                     best_total_sum = total_sum

#             if match > best_match_with_jkpt and match < 20 and has_jkpt:
#                 best_match_with_jkpt = match
#                 best_match_with_jkpt_combo = combo

#             if match > best_match_witho_jkpt and match < 20 and (not has_jkpt):
#                 best_match_witho_jkpt = match
#                 best_match_witho_jkpt_combo = combo

#             # print("COMBO:::", combo, "INDEX:::", index)

#         if best_match == 0:
#             best_match_combo = []

#         print(
#             "BEST MATCH ::",
#             best_match,
#             "MATCH ::",
#             match,
#             "COMBO ::",
#             best_match_combo,
#             "TOTAL SUM ::",
#             best_total_sum,
#         )

#         prices = SalaryForLifeDraw.filter_banker_winnings(
#             best_match_combo, plays, line_prices, jackpot_amount
#         )

#         filterd_winners = SalaryForLifeDraw.filter_banker_winnings(
#             best_match_combo, plays, line_prices, jackpot_amount
#         )
#         total_winning = SalaryForLifeDraw.deep_sum(filterd_winners)

#         if total_winning > rtp:
#             best_match_combo = SalaryForLifeDraw.least_occurring_numbers(plays)
#             print("BEST MATCH COMBO ::", best_match_combo)
#             return

#         from pprint import pprint

#         pprint(prices)
#         # raise SyntaxError
#         return dict(
#             best_match=best_match,
#             best_match_combo=best_match_combo,
#             best_match_with_jkpt=best_match_with_jkpt,
#             best_match_with_jkpt_combo=best_match_with_jkpt_combo,
#             best_match_witho_jkpt=best_match_witho_jkpt,
#             best_match_witho_jkpt_combo=best_match_witho_jkpt_combo,
#             LIMIT_WINING_AMOUNT=LIMIT_WINING_AMOUNT,
#         )

#     @staticmethod
#     def least_occurring_numbers(data):
#         all_numbers = list(range(1, 51))

#         for item in data:
#             if isinstance(item, tuple) and len(item) == 3:
#                 all_numbers.extend(item[1])

#         # Count occurrences of each number
#         number_counts = Counter(all_numbers)

#         # Return all numbers with their occurrences, sorted by frequency
#         numbers, _ = zip(*sorted(number_counts.items(), key=lambda x: x[1]))
#         combo = numbers[:10]
#         selection = random.sample(combo, k=5)

#         return selection

#     @staticmethod
#     def deep_sum(data):
#         total_winning_amount = 0

#         for item in data:
#             if isinstance(item, list) and len(item) == 3:
#                 total_winning_amount += item[2]  # Sum the winning_amount

#         return total_winning_amount

#     @staticmethod
#     def filter_winnings(combo, plays, prices, jackpot_amount):
#         const_obj = ConstantVariable.objects.all().last()
#         occurences = map(
#             lambda user_play: search_number_occurences(
#                 combo, user_play, const_obj.s4l_number_of_match_limit
#             ),
#             plays,
#         )  # CHECK FOR HOW MANY NUMBERS MATCH FOR EVERY COMBINATION IN LIST OF NUMBERS

#         play_occurences = zip(
#             occurences, plays
#         )  # Match number of occurences to number of matches found in selected combination
#         over3ocurrences = list(
#             filter(lambda x: x[0], play_occurences)
#         )  # FILTER ALL VALUES THAT ARE NOT 3 AND ABOVE (FILTER WITH FALSE)

#         play_occurences_with_amount = map(
#             lambda played: get_potential_winning(played, prices, jackpot_amount),
#             over3ocurrences,
#         )
#         data = list(play_occurences_with_amount)

#         return data

#     @staticmethod
#     def filter_banker_winnings(combo, plays, prices, jackpot_amount):
#         const_obj = ConstantVariable.objects.all().last()
#         occurences = map(
#             lambda user_play: search_number_occurences(
#                 combo, user_play, const_obj.s4l_number_of_match_limit
#             ),
#             plays,
#         )  # CHECK FOR HOW MANY NUMBERS MATCH FOR EVERY COMBINATION IN LIST OF NUMBERS

#         play_occurences = zip(
#             occurences, plays
#         )  # Match number of occurences to number of matches found in selected combination
#         over3ocurrences = list(
#             filter(lambda x: x[0], play_occurences)
#         )  # FILTER ALL VALUES THAT ARE NOT 3 AND ABOVE (FILTER WITH FALSE)

#         play_occurences_with_amount = map(
#             lambda played: get_banker_potential_winning(played, prices, jackpot_amount),
#             over3ocurrences,
#         )
#         data = list(play_occurences_with_amount)

#         return data


# # import random
# # from itertools import combinations

# # plays = [
# #     random.sample(range(1, 50), 5) for _ in range(100)  # simulate 100 player tickets
# # ]
# # rtp = 10000
# # line_prices = [100, 200, 500, 1000]
# # jackpot_amount = 1_000_000


# # test = SalaryForLifeDraw.draw(plays, rtp, line_prices, jackpot_amount)
# # print(test)
