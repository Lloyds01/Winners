# from decisioning_engine.draws import MegaCashDraw

# # Create an instance of the class
# draw = MegaCashDraw()

# # Run a smaller simulation for testing (so it doesn’t take forever)
# draw.PLAYS = 50       # reduce total plays for quick test
# draw.BASE_N = 5       # smaller batch size for faster payouts

# # Call the draw method
# result = draw.draw()

# print("\n=== TEST COMPLETE ===")
# print("Total Contribution:", draw.TOTAL_CONTRIBUTION)
# print("Running Balance:", draw.RUNNING_BALANCE)
# print("Plays Recorded:", len(draw.PLAYS_LIST))
# print("Result:", result)

from django.core.management.base import BaseCommand

import random, datetime
from pprint import pprint

class Command(BaseCommand):
    # Minimal test setup
    PLAYS = 20  # reduced for testing
    N = 5       # trigger payout every 5 plays
    WINNINGS = {
    150: {"min_win": 4500, "mid_win": 5400, "max_win": 11250},
    300: {"min_win": 7500, "mid_win": 9000, "max_win": 13500},
    450: {"min_win": 9000, "mid_win": 10800, "max_win": 15750},
    600: {"min_win": 10800, "mid_win": 13000, "max_win": 18000},
    750: {"min_win": 12000, "mid_win": 14000, "max_win": 18750},
    900: {"min_win": 13500, "mid_win": 16000, "max_win": 22500},
    1000: {"min_win": 15000, "mid_win": 18000, "max_win": 25000},
}

    # Assume the rest of the constants and WINNINGS dict are defined as above

    # --- Mock a quick play simulation ---
    for i in range(PLAYS):
        play = random.choice(list(WINNINGS.keys()))
        TOTAL_CONTRIBUTION += play
        BATCH_CONTRIBUTION += play
        print(f"Play #{i+1}: Band {play}, Batch Contribution: {BATCH_CONTRIBUTION}")

        if (i + 1) % N == 0:
            print("\n--- TRIGGERING PAYOUT ---")
            share_money_result, RUNNING_BALANCE = prepare_payout(BATCH_CONTRIBUTION, RUNNING_BALANCE)
            pprint(share_money_result)
            print("Remaining Balance:", RUNNING_BALANCE)
            print("--- END OF BATCH ---\n")
            BATCH_CONTRIBUTION = 0
