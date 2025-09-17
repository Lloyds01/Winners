from utils import as_object
import math
import random
import time
from pprint import pprint
import math
from collections import defaultdict


class DalsHourMgr:
    def __init__(self, query_set, constant):

        self.query_set = query_set
        self.constant = constant

        self.decision_dict: dict = {}

        self._ORIGINAL_REWARDS = {10: 10000, 50: 50000, 100: 100000, 200: 200000}
        self._JACKPOT_REWARDS = {10: 50000, 50: 250000, 100: 500000, 200: 1000000}

        self.dalshr_config = self.constant.dalshr_config
        # self.dalshr_config = {
        #     "tier": {
        #         10: {"min": 5, "step": 2},
        #         50: {"min": 10, "step": 3},
        #         100: {"min": 20, "step": 5},
        #         200: {"min": 50, "step": 10},
        #     },
        #     "rtp": 0.7,
        #     "rt0": 0.3,
        #     "win_factor": {
        #         10: 0.5,
        #         50: 0.5,
        #         100: 0.5,
        #         200: 0.5,
        #     },
        # }

        self.upper_tier_jackpot_percent = 25
        self.middle_tier_jackpot_percent = 25
        self.lower_tier_jackpot_percent = 20
        self.last_tier_jackpot_percent = 15

    def compute_rewards(self):

        tiers = self.dalshr_config["tier"]
        win_factor = self.dalshr_config["win_factor"]

        rewards_percentage = {
            10: (random.choice(range(tiers[10]["min"], 110, tiers[10]["step"])) / 100),
            50: (
                random.choice(
                    list(range(tiers[50]["min"], 110, tiers[50]["step"])) + [100]
                )
                / 100
            ),
            100: (
                random.choice(range(tiers[100]["min"], 110, tiers[100]["step"])) / 100
            ),
            200: (
                random.choice(range(tiers[200]["min"], 110, tiers[200]["step"])) / 100
            ),
        }

        return {
            10: 10000 * win_factor[10] / 100 * rewards_percentage[10],
            50: 50000 * win_factor[50] / 100 * rewards_percentage[50],
            100: 100000 * win_factor[100] / 100 * rewards_percentage[100],
            200: 200000 * win_factor[200] / 100 * rewards_percentage[200],
        }

    def run_decisioning(self):
        """
        Run the decisioning logic without Pandas.
        Works directly with query_set provided as a list of dictionaries.
        Each dictionary is expected to have keys: "id", "rto", "rtp", "pool".
        """

        # Initial balance carried over (constant value)
        wyse_cash_running_balance = self.constant.wyse_cash_running_balance

        # Compute reward mapping (e.g., {200: 1000, 100: 500, 50: 200, 10: 100})
        rewards = self.compute_rewards()

        # Convert query_set into a list of dicts (if it isn’t already)
        records = list(self.query_set)

        # ---------------- AGGREGATIONS ---------------- #

        # Total number of players
        total_player = len(records)

        # Sum of RTP and RTO, plus group by pool (done in one pass)
        pool_sums = defaultdict(float)
        total_rtp_sum = 0.0
        total_rto_sum = 0.0

        for rec in records:
            total_rtp_sum += rec["rtp"]
            total_rto_sum += rec["rto"]
            pool_sums[rec["pool"]] += rec["rtp"]

        # Total revenue = sum of RTP + running balance
        total_revenue = total_rtp_sum + wyse_cash_running_balance

        # Return to owner
        rto = total_rto_sum

        # Return to player
        rtp = total_revenue

        # Global jackpot = 5% of RTP
        GLOBAL_JACKPOT = rtp * 0.05

        # ---------------- HELPER FUNCTIONS ---------------- #

        def calc_percent(amount: float) -> float:
            """Return percentage of total revenue contributed by 'amount'."""
            return (
                round(100 * amount / float(total_revenue), 2) if total_revenue else 0.0
            )

        def calc_percent_of_amount(amount: float, number: float) -> float:
            """Return 'number%' of a given amount."""
            return round(number / 100 * float(amount), 2)

        # ---------------- CONTRIBUTIONS ---------------- #

        # Each pool gets an equal share of the running balance
        pool_balance_share = wyse_cash_running_balance / 4

        sum_last_tier_contribution = pool_sums["TEN_THOUSAND"] + pool_balance_share
        last_tier_percentage_contrib = calc_percent(sum_last_tier_contribution)

        sum_lower_tier_contribution = pool_sums["FIFTY_THOUSAND"] + pool_balance_share
        lower_tier_percentage_contrib = calc_percent(sum_lower_tier_contribution)

        sum_middle_tier_contribution = (
            pool_sums["ONE_HUNDRED_THOUSAND"] + pool_balance_share
        )
        middle_tier_percentage_contrib = calc_percent(sum_middle_tier_contribution)

        sum_upper_tier_contribution = (
            pool_sums["TWO_HUNDRED_THOUSAND"] + pool_balance_share
        )
        upper_tier_percentage_contrib = calc_percent(sum_upper_tier_contribution)

        # ---------------- AMOUNTS AND JACKPOTS ---------------- #

        # Ten Thousand band
        ten_thousand_amnt = calc_percent_of_amount(last_tier_percentage_contrib, rtp)
        ten_thousand_jackpot_amount = calc_percent_of_amount(
            self.last_tier_jackpot_percent, ten_thousand_amnt
        )
        last_tier_jackpot_and_amount_diff = round(
            ten_thousand_amnt - ten_thousand_jackpot_amount, 2
        )

        # Fifty Thousand band
        fifty_thousand_amnt = calc_percent_of_amount(lower_tier_percentage_contrib, rtp)
        fifty_thousand_jackpot_amount = calc_percent_of_amount(
            self.lower_tier_jackpot_percent, fifty_thousand_amnt
        )
        lower_tier_jackpot_and_amount_diff = round(
            fifty_thousand_amnt - fifty_thousand_jackpot_amount, 2
        )

        # Hundred Thousand band
        hundred_thousand_amnt = calc_percent_of_amount(
            middle_tier_percentage_contrib, rtp
        )
        hundred_thousand_jackpot_amount = calc_percent_of_amount(
            self.middle_tier_jackpot_percent, hundred_thousand_amnt
        )
        middle_tier_jackpot_and_amount_diff = round(
            hundred_thousand_amnt - hundred_thousand_jackpot_amount, 2
        )

        # Two Hundred Thousand band
        two_hundred_thousand_amnt = calc_percent_of_amount(
            upper_tier_percentage_contrib, rtp
        )
        two_hundred_thousand_jackpot_amount = calc_percent_of_amount(
            self.upper_tier_jackpot_percent, two_hundred_thousand_amnt
        )
        upper_tier_jackpot_and_amount_diff = round(
            two_hundred_thousand_amnt - two_hundred_thousand_jackpot_amount, 2
        )

        # ---------------- REWARDS DISTRIBUTION ---------------- #

        # Upper Tier
        upper_tier = round(upper_tier_jackpot_and_amount_diff / rewards[200], 2)
        disbursement_amount = math.floor(upper_tier) * rewards[200]
        upper_tier_balance = upper_tier_jackpot_and_amount_diff - disbursement_amount

        # Middle Tier
        middle_tier = round(
            (middle_tier_jackpot_and_amount_diff + upper_tier_balance) / rewards[100], 2
        )
        disbursement_amount = math.floor(middle_tier) * rewards[100]
        middle_tier_balance = (
            middle_tier_jackpot_and_amount_diff + upper_tier_balance
        ) - disbursement_amount

        # Lower Tier
        lower_tier = round(
            (lower_tier_jackpot_and_amount_diff + middle_tier_balance) / rewards[50], 2
        )
        disbursement_amount = math.floor(lower_tier) * rewards[50]
        lower_tier_balance = (
            lower_tier_jackpot_and_amount_diff + middle_tier_balance
        ) - disbursement_amount

        # Last Tier
        last_tier = round(
            (last_tier_jackpot_and_amount_diff + lower_tier_balance) / rewards[10], 2
        )
        disbursement_amount = math.floor(last_tier) * rewards[10]
        last_tier_balance = (
            last_tier_jackpot_and_amount_diff + lower_tier_balance
        ) - disbursement_amount

        # ---------------- JACKPOTS ---------------- #

        tjkpt = 0

        # Upper Tier Jackpot
        upper_tier_jackpot = round(
            two_hundred_thousand_jackpot_amount / self._JACKPOT_REWARDS[200], 2
        )
        disbursement_amount = (
            math.floor(upper_tier_jackpot) * self._JACKPOT_REWARDS[200]
        )
        tjkpt += disbursement_amount
        upper_tier_jackpot_balance = (
            two_hundred_thousand_jackpot_amount - disbursement_amount
        )

        # Middle Tier Jackpot
        middle_tier_jackpot = round(
            (hundred_thousand_jackpot_amount + upper_tier_jackpot_balance)
            / self._JACKPOT_REWARDS[100],
            2,
        )
        disbursement_amount = (
            math.floor(middle_tier_jackpot) * self._JACKPOT_REWARDS[100]
        )
        middle_tier_jackpot_balance = (
            hundred_thousand_jackpot_amount + upper_tier_jackpot_balance
        ) - disbursement_amount
        tjkpt += disbursement_amount

        # Lower Tier Jackpot
        lower_tier_jackpot = round(
            (fifty_thousand_jackpot_amount + middle_tier_jackpot_balance)
            / self._JACKPOT_REWARDS[50],
            2,
        )
        disbursement_amount = math.floor(lower_tier_jackpot) * self._JACKPOT_REWARDS[50]
        lower_tier_jackpot_balance = (
            fifty_thousand_jackpot_amount + middle_tier_jackpot_balance
        ) - disbursement_amount
        tjkpt += disbursement_amount

        # Last Tier Jackpot
        last_tier_jackpot = round(
            (ten_thousand_jackpot_amount + lower_tier_jackpot_balance)
            / self._JACKPOT_REWARDS[10],
            2,
        )
        disbursement_amount = math.floor(last_tier_jackpot) * self._JACKPOT_REWARDS[10]
        last_tier_jackpot_balance = (
            ten_thousand_jackpot_amount + lower_tier_jackpot_balance
        ) - disbursement_amount
        tjkpt += disbursement_amount

        # ---------------- FINAL RESULT ---------------- #

        result = {
            "upper_tier": {
                "count": upper_tier,
                "reward": rewards[200],
                "pool": "TWO_HUNDRED_THOUSAND",
                "jackpot": self._JACKPOT_REWARDS[200],
                "jkpt_count": upper_tier_jackpot,
            },
            "middle_tier": {
                "count": middle_tier,
                "reward": rewards[100],
                "pool": "ONE_HUNDRED_THOUSAND",
                "jackpot": self._JACKPOT_REWARDS[100],
                "jkpt_count": middle_tier_jackpot,
            },
            "lower_tier": {
                "count": lower_tier,
                "reward": rewards[50],
                "pool": "FIFTY_THOUSAND",
                "jackpot": self._JACKPOT_REWARDS[50],
                "jkpt_count": lower_tier_jackpot,
            },
            "last_tier": {
                "count": last_tier,
                "reward": rewards[10],
                "pool": "TEN_THOUSAND",
                "jackpot": self._JACKPOT_REWARDS[10],
                "jkpt_count": last_tier_jackpot,
            },
            "rtp": rtp,
        }

        return result

    # def run_decisioning(self):
    #     wyse_cash_running_balance = self.constant.wyse_cash_running_balance
    #     rewards = self.compute_rewards()

    #     game_df = pd.DataFrame.from_records(self.query_set.values())
    #     print(game_df)
    #     # print(game_df)

    #     total_player = game_df["id"].count()  # total player count
    #     # total_revenue = game_df["amount_paid"].sum()  # Estimate total amount stake

    #     # get constant variables

    #     total_revenue = (
    #         game_df["rtp"].sum() + wyse_cash_running_balance
    #     )  # Estimate total amount stake

    #     rto = game_df["rto"].sum()  # return to owner
    #     # rtp = game_df["stake_amount"].sum()  # return to player
    #     rtp = total_revenue
    #     print(game_df["rtp"].sum())
    #     GLOBAL_JACKPOT = rtp * 0.05
    #     print("RTP : ", game_df["rtp"].sum())
    #     print("Brought Forward : ", wyse_cash_running_balance)
    #     print("Total RTP : ", rtp)

    #     # rtp = rtp - GLOBAL_JACKPOT

    #     def calc_percent(amount):
    #         return round(100 * amount / float(total_revenue), 2)

    #     calc_percent_of_amount = lambda amount, number: round(
    #         number / 100 * float(amount), 2
    #     )  # noqa

    #     #

    #     filter_pool_sum_up_stake_amnt = lambda pool: game_df[game_df["pool"] == pool][
    #         "rtp"
    #     ].sum()  # noqa

    #     sum_last_tier_contribution = filter_pool_sum_up_stake_amnt("TEN_THOUSAND") + (
    #         wyse_cash_running_balance / 4
    #     )
    #     # get the percent at which 10,000 band contributed to the total revenue
    #     last_tier_percentage_contrib = calc_percent(sum_last_tier_contribution)  # noqa

    #     sum_lower_tier_contribution = filter_pool_sum_up_stake_amnt(
    #         "FIFTY_THOUSAND"
    #     ) + (wyse_cash_running_balance / 4)
    #     # get the percent at which 50,000 band contributed to the total revenue
    #     lower_tier_percentage_contrib = calc_percent(
    #         sum_lower_tier_contribution
    #     )  # noqa

    #     sum_middle_tier_contribution = filter_pool_sum_up_stake_amnt(
    #         "ONE_HUNDRED_THOUSAND"
    #     ) + (wyse_cash_running_balance / 4)
    #     # get the percent at which 100,000 band contributed to the total revenue
    #     middle_tier_percentage_contrib = calc_percent(
    #         sum_middle_tier_contribution
    #     )  # noqa

    #     sum_upper_tier_contribution = filter_pool_sum_up_stake_amnt(
    #         "TWO_HUNDRED_THOUSAND"
    #     ) + (wyse_cash_running_balance / 4)
    #     upper_tier_percentage_contrib = calc_percent(
    #         sum_upper_tier_contribution
    #     )  # noqa

    #     print("1.", sum_last_tier_contribution)
    #     print("2.", sum_lower_tier_contribution)
    #     print("3.", sum_middle_tier_contribution)
    #     print("4.", sum_upper_tier_contribution)

    #     #

    #     ten_thousand_amnt = calc_percent_of_amount(
    #         last_tier_percentage_contrib, rtp
    #     )  # Amount
    #     ten_thousand_jackpot_amount = calc_percent_of_amount(
    #         self.last_tier_jackpot_percent, ten_thousand_amnt
    #     )  # Jackpot
    #     last_tier_jackpot_and_amount_diff = round(
    #         (ten_thousand_amnt - ten_thousand_jackpot_amount), 2
    #     )  # amount - jackpot

    #     fifty_thousand_amnt = calc_percent_of_amount(
    #         lower_tier_percentage_contrib, rtp
    #     )  # Amount
    #     fifty_thousand_jackpot_amount = calc_percent_of_amount(
    #         self.lower_tier_jackpot_percent, fifty_thousand_amnt
    #     )  # Jackpot
    #     lower_tier_jackpot_and_amount_diff = round(
    #         (fifty_thousand_amnt - fifty_thousand_jackpot_amount), 2
    #     )  # amount - jackpot

    #     hundred_thousand_amnt = calc_percent_of_amount(
    #         middle_tier_percentage_contrib, rtp
    #     )  # Amount
    #     hundred_thousand_jackpot_amount = calc_percent_of_amount(
    #         self.middle_tier_jackpot_percent, hundred_thousand_amnt
    #     )  # Jackpot
    #     middle_tier_jackpot_and_amount_diff = round(
    #         (hundred_thousand_amnt - hundred_thousand_jackpot_amount), 2
    #     )  # amount - jackpot

    #     two_hundred_thousand_amnt = calc_percent_of_amount(
    #         upper_tier_percentage_contrib, rtp
    #     )  # Amount
    #     two_hundred_thousand_jackpot_amount = calc_percent_of_amount(
    #         self.upper_tier_jackpot_percent, two_hundred_thousand_amnt
    #     )  # Jackpot
    #     upper_tier_jackpot_and_amount_diff = round(
    #         (two_hundred_thousand_amnt - two_hundred_thousand_jackpot_amount), 2
    #     )  # amount - jackpot

    #     print(
    #         ten_thousand_amnt,
    #         last_tier_jackpot_and_amount_diff,
    #         ten_thousand_jackpot_amount,
    #     )
    #     print(
    #         fifty_thousand_amnt,
    #         lower_tier_jackpot_and_amount_diff,
    #         fifty_thousand_jackpot_amount,
    #     )
    #     print(hundred_thousand_amnt, middle_tier_jackpot_and_amount_diff)
    #     print(
    #         two_hundred_thousand_amnt,
    #         upper_tier_jackpot_and_amount_diff,
    #         two_hundred_thousand_jackpot_amount,
    #     )
    #     #
    #     upper_tier = round((upper_tier_jackpot_and_amount_diff / rewards[200]), 2)
    #     disbursement_amount = math.floor(upper_tier) * rewards[200]
    #     upper_tier_balance = upper_tier_jackpot_and_amount_diff - disbursement_amount

    #     print("Upper", upper_tier)
    #     middle_tier = round(
    #         (middle_tier_jackpot_and_amount_diff + upper_tier_balance) / rewards[100],
    #         2,
    #     )

    #     disbursement_amount = math.floor(middle_tier) * rewards[100]
    #     middle_tier_balance = (
    #         middle_tier_jackpot_and_amount_diff + upper_tier_balance
    #     ) - disbursement_amount

    #     lower_tier = round(
    #         (lower_tier_jackpot_and_amount_diff + middle_tier_balance) / rewards[50],
    #         2,
    #     )
    #     print("lower", lower_tier)
    #     disbursement_amount = math.floor(lower_tier) * rewards[50]
    #     lower_tier_balance = (
    #         lower_tier_jackpot_and_amount_diff + middle_tier_balance
    #     ) - disbursement_amount

    #     last_tier = round(
    #         (last_tier_jackpot_and_amount_diff + lower_tier_balance) / rewards[10],
    #         2,
    #     )
    #     print("last ", last_tier)
    #     disbursement_amount = math.floor(last_tier) * rewards[10]
    #     last_tier_balance = (
    #         last_tier_jackpot_and_amount_diff + lower_tier_balance
    #     ) - disbursement_amount
    #     print("last_tier_balance", last_tier_balance)
    #     #
    #     tjkpt = 0
    #     upper_tier_jackpot = round(
    #         (two_hundred_thousand_jackpot_amount / self._JACKPOT_REWARDS[200]), 2
    #     )
    #     disbursement_amount = (
    #         math.floor(upper_tier_jackpot) * self._JACKPOT_REWARDS[200]
    #     )
    #     tjkpt += disbursement_amount
    #     upper_tier_jackpot_balance = (
    #         two_hundred_thousand_jackpot_amount - disbursement_amount
    #     )
    #     # print("UPPER TIER BAL", "__________________", upper_tier_jackpot_balance)
    #     print(
    #         "TOTALS",
    #         "__________________",
    #         two_hundred_thousand_jackpot_amount,
    #         self._JACKPOT_REWARDS[200],
    #     )
    #     print(
    #         "BUILD VALS",
    #         "__________________",
    #         two_hundred_thousand_jackpot_amount,
    #         disbursement_amount,
    #     )
    #     print(
    #         "UPPER TIER JKPT",
    #         "__________________",
    #         upper_tier_jackpot_balance,
    #     )

    #     middle_tier_jackpot = round(
    #         (hundred_thousand_jackpot_amount + upper_tier_jackpot_balance)
    #         / self._JACKPOT_REWARDS[100],
    #         2,
    #     )
    #     disbursement_amount = (
    #         math.floor(middle_tier_jackpot) * self._JACKPOT_REWARDS[100]
    #     )
    #     middle_tier_jackpot_balance = (
    #         hundred_thousand_jackpot_amount + upper_tier_jackpot_balance
    #     ) - disbursement_amount
    #     tjkpt += disbursement_amount
    #     # print("MIDDLE TIER BAL", "__________________", middle_tier_jackpot_balance)
    #     print(
    #         "\n\nTOTALS",
    #         "__________________",
    #         hundred_thousand_jackpot_amount,
    #         self._JACKPOT_REWARDS[100],
    #     )
    #     print(
    #         "BUILD VALS",
    #         "__________________",
    #         hundred_thousand_jackpot_amount,
    #         upper_tier_jackpot_balance,
    #         disbursement_amount,
    #     )
    #     print(
    #         "MIDDLE TIER JKPT",
    #         "__________________",
    #         middle_tier_jackpot_balance,
    #     )

    #     lower_tier_jackpot = round(
    #         (fifty_thousand_jackpot_amount + middle_tier_jackpot_balance)
    #         / self._JACKPOT_REWARDS[50],
    #         2,
    #     )
    #     disbursement_amount = math.floor(lower_tier_jackpot) * self._JACKPOT_REWARDS[50]
    #     tjkpt += disbursement_amount
    #     lower_tier_jackpot_balance = (
    #         fifty_thousand_jackpot_amount + middle_tier_jackpot_balance
    #     ) - disbursement_amount
    #     # print("DISB : :", disbursement_amount, "WINNERS : :", math.floor(lower_tier_jackpot), "VALUE : :", self._JACKPOT_REWARDS[50])

    #     print(
    #         "\n\nTOTALS",
    #         "__________________",
    #         fifty_thousand_jackpot_amount,
    #         self._JACKPOT_REWARDS[50],
    #     )
    #     print(
    #         "BUILD VALS",
    #         "__________________",
    #         fifty_thousand_jackpot_amount,
    #         middle_tier_jackpot_balance,
    #         disbursement_amount,
    #     )
    #     print("LOWER TIER BAL", "__________________", lower_tier_jackpot_balance)

    #     last_tier_jackpot = round(
    #         (ten_thousand_jackpot_amount + lower_tier_jackpot_balance)
    #         / self._JACKPOT_REWARDS[10],
    #         2,
    #     )
    #     disbursement_amount = math.floor(last_tier_jackpot) * self._JACKPOT_REWARDS[10]
    #     last_tier_jackpot_balance = (
    #         ten_thousand_jackpot_amount + lower_tier_jackpot_balance
    #     ) - disbursement_amount

    #     tjkpt += disbursement_amount

    #     print(
    #         "\n\nTOTALS",
    #         "__________________",
    #         ten_thousand_jackpot_amount,
    #         self._JACKPOT_REWARDS[10],
    #     )
    #     print(
    #         "BUILD VALS",
    #         "__________________",
    #         ten_thousand_jackpot_amount,
    #         lower_tier_jackpot_balance,
    #         disbursement_amount,
    #     )
    #     print("Jkpt_bal", "__________________", last_tier_jackpot_balance)
    #     print("FINAL BALANCE : ", tjkpt)

    #     print(
    #         f"""
    #             =================================================================
    #             Target Unique Players           | {total_player}
    #             -----------------------------------------------------------------
    #             Estimated Total Revenue         | {total_revenue}
    #             -----------------------------------------------------------------
    #             Return to Owner                 | {rto}
    #             -----------------------------------------------------------------
    #             Return to Player                | {rtp}
    #             -----------------------------------------------------------------
    #             Global Jackpot                  | {GLOBAL_JACKPOT}
    #             ========================================================================================================
    #             ___________________________________SOCIAL PROOF_____AMOUNT______JACKPOT_______BALANCE___________
    #             10,000 Band player count        | {last_tier_percentage_contrib}%  |      {ten_thousand_amnt} |  {ten_thousand_jackpot_amount}    |  {last_tier_jackpot_and_amount_diff}
    #             --------------------------------------------------------------------------------------------------------
    #             50,000 Band player count        | {lower_tier_percentage_contrib}%  |      {fifty_thousand_amnt} |  {fifty_thousand_jackpot_amount}     |  {lower_tier_jackpot_and_amount_diff}
    #             --------------------------------------------------------------------------------------------------------
    #             100,000 Band player count       | {middle_tier_percentage_contrib}%   |      {hundred_thousand_amnt}  |  {hundred_thousand_jackpot_amount}   |  {middle_tier_jackpot_and_amount_diff}
    #             --------------------------------------------------------------------------------------------------------
    #             200,000 Band player count       | {upper_tier_percentage_contrib}%   |      {two_hundred_thousand_amnt}  |  {two_hundred_thousand_jackpot_amount}  |  {upper_tier_jackpot_and_amount_diff}
    #             --------------------------------------------------------------------------------------------------------
    #             ========================================================================================================
    #             Upper Tier                      | {upper_tier} | REWARDS {self.REWARDS[200]} {self._REWARDS_PERCENT[200]}
    #             --------------------------------------------------------------------------------------------------------
    #             Middle Tier                     | {middle_tier} | REWARDS {self.REWARDS[100]}  {self._REWARDS_PERCENT[100]}
    #             --------------------------------------------------------------------------------------------------------
    #             Lower Tier                      | {lower_tier} | REWARDS {self.REWARDS[50]}  {self._REWARDS_PERCENT[50]}
    #             --------------------------------------------------------------------------------------------------------
    #             Last Tier                       | {last_tier} | REWARDS {self.REWARDS[10]}  {self._REWARDS_PERCENT[10]}
    #             --------------------------------------------------------------------------------------------------------
    #             =======================================================================================================
    #             Upper Tier jackpot                     | {upper_tier_jackpot}
    #             --------------------------------------------------------------------------------------------------------
    #             Middle Tier jackpot                   | {middle_tier_jackpot}
    #             --------------------------------------------------------------------------------------------------------
    #             Lower Tier jackpot                      | {lower_tier_jackpot}
    #             --------------------------------------------------------------------------------------------------------
    #             Last Tier jackpot                      | {last_tier_jackpot}
    #             --------------------------------------------------------------------------------------------------------
    #             """
    #     )

    #     result = {
    #         "upper_tier": {
    #             "count": upper_tier,
    #             "reward": rewards[200],
    #             "pool": "TWO_HUNDRED_THOUSAND",
    #             "jackpot": self._JACKPOT_REWARDS[200],
    #             "jkpt_count": upper_tier_jackpot,
    #         },
    #         "middle_tier": {
    #             "count": middle_tier,
    #             "reward": rewards[100],
    #             "pool": "ONE_HUNDRED_THOUSAND",
    #             "jackpot": self._JACKPOT_REWARDS[100],
    #             "jkpt_count": middle_tier_jackpot,
    #         },
    #         "lower_tier": {
    #             "count": lower_tier,
    #             "reward": rewards[50],
    #             "pool": "FIFTY_THOUSAND",
    #             "jackpot": self._JACKPOT_REWARDS[50],
    #             "jkpt_count": lower_tier_jackpot,
    #         },
    #         "last_tier": {
    #             "count": last_tier,
    #             "reward": rewards[10],
    #             "pool": "TEN_THOUSAND",
    #             "jackpot": self._JACKPOT_REWARDS[10],
    #             "jkpt_count": last_tier_jackpot,
    #         },
    #         "rtp": rtp,
    #     }

    #     return result

    # def draw(self):
    #     decision_dict = self.run_decisioning()

    #     for key, value in decision_dict.items():
    #         print(key, value)
    #         if key == "rtp":
    #             continue

    #         tier_players = self.query_set.filter(pool=value["pool"]).values_list(
    #             "game_play_id", flat=True
    #         )
    #         sample = math.floor(value["count"])
    #         if len(list(tier_players)) < math.floor(value["count"]):
    #             sample = len(list(tier_players))

    #         print("list(tier_players)", list(tier_players))
    #         print(
    #             'math.floor(value["count"])', math.floor(value["count"]), "\n\n\n\n\n"
    #         )

    #         winners = random.sample(list(tier_players), sample)

    #         decision_dict[key]["winners"] = winners

    #     # pprint(decision_dict)

    #     for key, value in decision_dict.items():
    #         # print(key, value)
    #         if key == "rtp":
    #             continue

    #         tier_players = self.query_set.filter(pool=value["pool"]).values_list(
    #             "game_play_id", flat=True
    #         )

    #         sample = math.floor(value["jkpt_count"])
    #         if len(list(tier_players)) < math.floor(value["jkpt_count"]):
    #             sample = len(list(tier_players))

    #         print("list(tier_players)", list(tier_players))
    #         print(
    #             'math.floor(value["count"])',
    #             math.floor(value["jkpt_count"]),
    #             "\n\n\n\n\n",
    #         )
    #         winners = random.sample(list(tier_players), sample)

    #         decision_dict[key]["jkpt_winners"] = winners

    #     total_payout_amount = 0

    #     for key, value in decision_dict.items():
    #         print(key)
    #         if key == "rtp":
    #             continue
    #         amount = len(value["winners"]) * value["reward"]
    #         jamount = len(value["jkpt_winners"]) * value["jackpot"]

    #         total_payout_amount += amount + jamount

    #     print(total_payout_amount)

    #     running_bal = decision_dict["rtp"] - total_payout_amount
    #     print("Final Vals", decision_dict["rtp"], total_payout_amount)

    #     constant_variable = ConstantVariable.objects.all().last()
    #     constant_variable.wyse_cash_running_balance = running_bal
    #     constant_variable.save()

    #     del decision_dict["rtp"]

    #     return decision_dict


class DecisioningDataFactory:
    POOLS = [
        "TEN_THOUSAND",
        "FIFTY_THOUSAND",
        "ONE_HUNDRED_THOUSAND",
        "TWO_HUNDRED_THOUSAND",
    ]

    @classmethod
    def generate_records(cls, count=10, rtp_range=(100, 1000), rto_range=(50, 500)):
        """
        Generate test records for run_decisioning.

        Args:
            count (int): Number of records to generate
            rtp_range (tuple): Min and max range for random RTP values
            rto_range (tuple): Min and max range for random RTO values

        Returns:
            list[dict]: A list of record dictionaries
        """
        records = []
        for i in range(1, count + 1):
            rec = {
                "id": i,
                "rtp": random.uniform(*rtp_range),  # random RTP amount
                "rto": random.uniform(*rto_range),  # random RTO amount
                "pool": random.choice(cls.POOLS),  # assign a random pool
            }
            records.append(rec)
        return records


# Generate 50 random test records
records = DecisioningDataFactory.generate_records(count=50)

# Now you can inject it into your class
# obj = MyDecisioningClass(query_set=records, constant=const)
# result = obj.run_decisioning()

# pprint(records)
cont_data = {
    "wyse_cash_running_balance": 150000,
    "dalshr_config": {
        "tier": {
            10: {"min": 5, "step": 2},
            50: {"min": 10, "step": 3},
            100: {"min": 20, "step": 5},
            200: {"min": 50, "step": 10},
        },
        "rtp": 0.7,
        "rt0": 0.3,
        "win_factor": {
            10: 0.5,
            50: 0.5,
            100: 0.5,
            200: 0.5,
        },
    },
}
dhl_object = DalsHourMgr(query_set=records, constant=as_object(cont_data))
result = dhl_object.run_decisioning()

pprint(result)
