import datetime
import itertools
import math
import random
import time
from functools import reduce
from dataclasses import dataclass, field
from collections import deque

# @dataclass
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



@dataclass
class MegaCashDraw:
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
                return {"requesting_for_2": True, "winners": winners, "balance": balance}

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

            print(f"#{self.BATCH}", play, picks, "->", self.TOTAL_CONTRIBUTION, self.BATCH_CONTRIBUTION)

            # Every N plays or surge → evaluate payouts
            if self.BATCH >= self.BASE_N or self.SURGE:
                time_elapsed = self.play_times[-1] - self.play_times[0]
                play_freq = self.BASE_N / time_elapsed.total_seconds()

                # Prepare bands & shares
                payout_bands = sorted(random.sample(self.AVAILABLE_BANDS, 3), reverse=True)
                share_values = sorted(
                    [r * self.BATCH_CONTRIBUTION for r in self.SHARE_RATIO],
                    reverse=True
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

                print(f"Batch finished: {len(result['winners'])} winners, "
                      f"{round(time_elapsed.total_seconds(), 2)}s elapsed, "
                      f"{round(play_freq, 2)} plays/sec")

                self.BATCH_CONTRIBUTION = 0

        return self.TOTAL_CONTRIBUTION


# bands = [150, 300, 450]
# share_values = [10000, 20000, 30000]

# test = MegaCashDraw().sharemonies(bands=bands, share_values=share_values)
# print(test)