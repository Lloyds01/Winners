import datetime
import random
import time
from functools import reduce
from pprint import pprint

from django.db.models import Q

from overide_print import print


def instant_cashout_draw() -> list:
    from main.models import ConstantVariable, LottoTicket

    TOTAL_CONTRIBUTION = 0
    RUNNING_BALANCE = 0
    BATCH_CONTRIBUTION = 0
    PREVIOUS_BATCH_PLAYS = 0

    SHARE_RATIO = 0.4, 0.35, 0.25

    BASE_N = 9
    N = 9
    BASE_PPS = 0  # BASE PLAYS PER SECOND
    MOST_RECENT_ELAPSED_TIME = 0
    BATCH = 0
    GLOBAL_BATCH = 0
    SURGE = False
    LAST_PLAY_TIME = datetime.datetime.now()
    MAX_TIME_BETWEEN_WIN = 5  # IN MINUTES

    PLAYS_LIST = {}

    sub_batch_time_elaspsed = 0

    # WIN_PROGRESSION_FACTOR = 0.833  # moving factor for winning from 3/4 -> 4/4 match
    LAST_WIN_TIME = datetime.datetime.now()

    play_times = []

    const_obj = ConstantVariable.objects.all().last().instant_cashout_running_balance
    if const_obj is None:
        const_obj = ConstantVariable.objects.create(game_threshold=1)

    # WINNINGS = {
    #     150: {"min_win": 4500, "mid_win": 5400, "max_win": 11250},
    #     300: {"min_win": 7500, "mid_win": 9000, "max_win": 13500},
    #     450: {"min_win": 9000, "mid_win": 10800, "max_win": 15750},
    #     600: {"min_win": 10800, "mid_win": 13000, "max_win": 18000},
    #     750: {"min_win": 12000, "mid_win": 14000, "max_win": 18750},
    #     900: {"min_win": 13500, "mid_win": 16000, "max_win": 22500},
    #     1000: {"min_win": 15000, "mid_win": 18000, "max_win": 25000},
    # }

    WINNINGS = {
        # 150: {
        #     "min_win": 4500
        #     / ConstantVariable.objects.all().last().icash_winnings_divisor,
        #     "mid_win": 5400
        #     / ConstantVariable.objects.all().last().icash_winnings_divisor,
        #     "max_win": 11250
        #     / ConstantVariable.objects.all().last().icash_winnings_divisor,
        # },
        200: {
            "min_win": 4500 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 5400 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 11250 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        300: {
            "min_win": 7500 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 9000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 13500 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        450: {
            "min_win": 9000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 10800 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 15750 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        600: {
            "min_win": 10800 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 13000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 18000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        750: {
            "min_win": 12000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 14000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 18750 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        800: {
            "min_win": 12000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 14000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 18750 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        900: {
            "min_win": 13500 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 16000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 22500 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
        1000: {
            "min_win": 15000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "mid_win": 18000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
            "max_win": 25000 / ConstantVariable.objects.all().last().icash_winnings_divisor,
        },
    }

    for band in WINNINGS.keys():
        band_winning_values = list(WINNINGS[band].values())

        WINNINGS[band]["total_possible_for_3"] = sum(band_winning_values)
        WINNINGS[band]["total_possible_for_2"] = band_winning_values[0] + band_winning_values[1]

    AVAILABLE_BANDS = list(WINNINGS.keys())

    seed = [1, 1, 1, 3, 5, 6, 10]
    random.shuffle(seed)
    [[band] * seed_val for seed_val, band in zip(seed, AVAILABLE_BANDS)]
    # skew_list = reduce(lambda l1, l2: l1 + l2, skew)

    dict(WINNINGS.items())

    def sharemonies(bands, share_values, requesting_for_2=False, batch=0):
        from main.models import InstantCashoutPendingWinning

        print("....SHARING MONIES ....")
        print(f"BNDS....{bands} ....")
        print(f"SH_V....{share_values} ....")
        print(f"REQ2....{requesting_for_2} ....")

        bands_n_shares = zip(bands, share_values)
        winnin_tiers = []
        print(bands, share_values)

        BALANCE = 0  # const_obj.instant_cashout_running_balance

        for band, share in bands_n_shares:
            print("SHARE-BALANCE ::", share, "-", BALANCE)
            share = share + BALANCE
            payout_to_band_tiers = WINNINGS[band]

            print(f"{band} PAYOUT :::", payout_to_band_tiers)

            if share > payout_to_band_tiers["total_possible_for_3"]:
                BALANCE = share - (payout_to_band_tiers["min_win"] + payout_to_band_tiers["mid_win"] + payout_to_band_tiers["max_win"])

                winnin_tiers.append(("min_win", band, payout_to_band_tiers["min_win"]))
                winnin_tiers.append(("mid_win", band, payout_to_band_tiers["mid_win"]))
                winnin_tiers.append(("max_win", band, payout_to_band_tiers["max_win"]))

            elif share > payout_to_band_tiers["total_possible_for_2"]:
                BALANCE = share - (payout_to_band_tiers["min_win"] + payout_to_band_tiers["mid_win"])
                winnin_tiers.append(("min_win", band, payout_to_band_tiers["min_win"]))
                winnin_tiers.append(("mid_win", band, payout_to_band_tiers["mid_win"]))

            elif share > payout_to_band_tiers["min_win"]:
                BALANCE = share - (payout_to_band_tiers["min_win"])
                winnin_tiers.append(("min_win", band, payout_to_band_tiers["min_win"]))

            elif requesting_for_2 is False:
                print("BALANCE ::", BALANCE)
                return dict(
                    requesting_for_1=False,
                    requesting_for_2=True,
                    winners=winnin_tiers,
                    balance=BALANCE,
                )

            else:
                print("BALANCE ::", BALANCE)
                return dict(
                    requesting_for_1=True,
                    requesting_for_2=False,
                    winners=winnin_tiers,
                    balance=BALANCE,
                )

        InstantCashoutPendingWinning.handle_game_winning_list(batch, winnin_tiers)

        print("BALANCE ::", BALANCE)

        return dict(requesting_for_2=False, winners=winnin_tiers, balance=BALANCE)

    def get_unique_random(values, qty):
        time.sleep(1)
        # print(f"""SUSPECT PARAMETERS : {values}, {qty}""")
        # print(f""" : {WINNINGS.keys()}, {qty}""")
        attempts = 0

        while True:
            attempts += 1
            if len(values) < qty:
                values = list(WINNINGS.keys())
                # print(f""" : {WINNINGS.keys()}, {qty}""")

            # print(f"""NEW KEYS : {values}, {qty}""")
            payout_bands = random.sample(values, qty)
            if len(set(payout_bands)) == 3:
                break

            if attempts > 10:
                break

        return payout_bands

    while True:
        merge_pos_draw_icash = ConstantVariable.objects.all().last().merge_pos_draw_icash
        if (datetime.datetime.now() - LAST_WIN_TIME).total_seconds() > MAX_TIME_BETWEEN_WIN * 60:
            N = BASE_N

        if merge_pos_draw_icash:
            instant_cahsout_qs = LottoTicket.objects.filter(
                Q(lottery_type="INSTANT_CASHOUT") | Q(lottery_type="VIRTUAL_SOCCER") | Q(lottery_type="QUIKA"),
                Q(instant_cashout_drawn=False),
                Q(paid=True),
            )[:100]
        else:
            instant_cahsout_qs = LottoTicket.objects.filter(
                Q(lottery_type="INSTANT_CASHOUT") | Q(lottery_type="VIRTUAL_SOCCER") | Q(lottery_type="QUIKA"),
                Q(is_agent=False),
                Q(instant_cashout_drawn=False),
                Q(paid=True),
            )[:100]

        print(f"N: {N} BASE N: {BASE_N}")
        print(instant_cahsout_qs)

        # instant_cashout_ids = instant_cahsout_qs.values_list("pk", flat=True)
        # LottoTicket.objects.filter(pk__in=list(instant_cashout_ids)).update(
        #     instant_cashout_drawn=True
        # )

        instant_cashout_ids = []
        const_obj = ConstantVariable.objects.all().last()

        BATCH_CONTRIBUTION = const_obj.instant_cashout_running_balance

        time.sleep(1)
        for player in instant_cahsout_qs:
            instant_cashout_ids.append(player.pk)
            play_times.append(datetime.datetime.now())

            # time_delay = open("variables.txt", "r").read() or 1
            # time.sleep(float(time_delay))

            picks = [int(pick) for pick in player.ticket.split(",")]

            if player.number_of_ticket == 7:
                play = 1000
            else:
                play = 150 * player.number_of_ticket

            TOTAL_CONTRIBUTION += player.rtp
            BATCH_CONTRIBUTION += player.rtp

            print("BATCH :::", BATCH_CONTRIBUTION, "+", player.rtp)

            band_play = PLAYS_LIST.get(play, 0)

            print(f"PLAYER RTP: {player.rtp}")

            if band_play:
                PLAYS_LIST[play] += player.rtp
            else:
                PLAYS_LIST[play] = player.rtp

            string = f"""#{BATCH}", {play}, {picks},"---->", Total : {TOTAL_CONTRIBUTION} Batch :{BATCH_CONTRIBUTION}"""
            const_obj.instant_cashout_running_balance = BATCH_CONTRIBUTION
            const_obj.save()

            print(string)

            BATCH += 1

            if BATCH in list(range(0, int(N) + 1, 5)) and MOST_RECENT_ELAPSED_TIME != 0:
                play_times_recent_N_section = play_times[int(-BATCH) :]
                sub_batch_time_elaspsed: datetime.timedelta = play_times_recent_N_section[-1] - play_times_recent_N_section[0]

                if sub_batch_time_elaspsed.total_seconds() > MOST_RECENT_ELAPSED_TIME * 1.1:
                    print(
                        "BATCH TIMES: ",
                        sub_batch_time_elaspsed.total_seconds(),
                        MOST_RECENT_ELAPSED_TIME * 1.5,
                    )
                    print("OOUPS SURGE..!!!", "BATCH : ", -BATCH)

                    if BATCH >= BASE_N:
                        SURGE = True

                else:
                    pass

            time_since_lastplay = (datetime.datetime.now() - LAST_PLAY_TIME).total_seconds()
            print(f"""{BATCH} >= {N} or {SURGE} or {BATCH_CONTRIBUTION} > 60000 or {time_since_lastplay} > 1800""")

            if BATCH >= N or SURGE or BATCH_CONTRIBUTION > 60000 or time_since_lastplay > 1800:  # or if its more than 30mins sinces last play
                print("BREAKING FROM BATCH")
                print("N=", N, "BATCH=", BATCH)
                LAST_WIN_TIME = datetime.datetime.now()
                # batch_play_times_recent_N_section = play_times[int(-BATCH) :]
                # batch_time_elaspsed: datetime.timedelta = batch_play_times_recent_N_section[-1] - batch_play_times_recent_N_section[0]
                # print(batch_play_times_recent_N_section[0])
                # print(batch_play_times_recent_N_section[-1])

                play_times_recent_N_section = play_times[int(-BATCH) :]
                time_elaspsed: datetime.timedelta = play_times_recent_N_section[-1] - play_times_recent_N_section[0]
                play_frequency = N / (time_elaspsed.total_seconds() or 1)
                MOST_RECENT_ELAPSED_TIME = time_elaspsed.total_seconds()

                def prepare_payout(BATCH_CONTRIBUTION, RUNNING_BALANCE):
                    random.shuffle(AVAILABLE_BANDS)
                    # print("AVAILABLE_BANDS ::", AVAILABLE_BANDS)

                    payout_skew = [[key] * value for key, value in PLAYS_LIST.items()]
                    payout_skew_list = reduce(lambda l1, l2: l1 + l2, payout_skew)
                    # print("NORMALIZED_PAY : ", payout_skew_list)

                    payout_bands = sorted(get_unique_random(payout_skew_list, 3))

                    print(payout_bands)
                    print(f"ORIGINAL CONTRIB::: {BATCH_CONTRIBUTION}")
                    print(f"RUNNING_BALANCE::: {RUNNING_BALANCE}")

                    BATCH_CONTRIBUTION += RUNNING_BALANCE

                    print("UPDATED CONTRIB:::", BATCH_CONTRIBUTION)

                    SHARE_VALUES = (
                        SHARE_RATIO[0] * BATCH_CONTRIBUTION,
                        SHARE_RATIO[1] * BATCH_CONTRIBUTION,
                        SHARE_RATIO[2] * BATCH_CONTRIBUTION,
                    )

                    print("SHARE VALUES : ", SHARE_VALUES)
                    print("BATCH CONTRIB : ", BATCH_CONTRIBUTION)

                    payout_bands = sorted(payout_bands, reverse=True)
                    SHARE_VALUES = sorted(SHARE_VALUES, reverse=True)

                    share_money_result = sharemonies(payout_bands, SHARE_VALUES, batch=GLOBAL_BATCH)

                    print("::::SHARE RES::::", share_money_result)
                    print(f"""\n\n# {len(share_money_result["winners"])}WINNERS #\n\n""")

                    if share_money_result.get("requesting_for_2"):
                        print("\n\n:::::::::::::REQUESTED FOR 2::::::::::::::\n]\n")

                        SHARE_VALUES[1] = SHARE_VALUES[1] + SHARE_VALUES[0] * 0.6
                        SHARE_VALUES[2] = SHARE_VALUES[2] + SHARE_VALUES[0] * 0.4

                        share_money_result = sharemonies(
                            [payout_bands[1], payout_bands[2]],
                            [SHARE_VALUES[1], SHARE_VALUES[2]],
                            requesting_for_2=True,
                            batch=GLOBAL_BATCH,
                        )
                        print(f"""\n\n# {len(share_money_result["winners"])}WINNERS #\n\n""")

                        print(
                            "SHARE AFTER RESOLVE\n\n",
                            [payout_bands[1], payout_bands[2]],
                            [SHARE_VALUES[1], SHARE_VALUES[2]],
                        )

                    RUNNING_BALANCE = share_money_result.get("balance", 0)
                    if share_money_result.get("requesting_for_1"):
                        print("\n\n:::::::::::::REQUESTED FOR 1::::::::::::::\n]\n")

                        share_money_result = sharemonies(
                            [payout_bands[2]],
                            [SHARE_VALUES[1] + SHARE_VALUES[2]],
                            batch=GLOBAL_BATCH,
                        )
                        print(f"""\n\n# {len(share_money_result["winners"])}WINNERS #\n\n""")

                        print(
                            "SHARE AFTER RESOLVE FOR 1\n\n",
                            [payout_bands[2]],
                            [SHARE_VALUES[1] + SHARE_VALUES[2]],
                        )

                    print("::::SHARE RES 2::::")
                    pprint(share_money_result)

                    RUNNING_BALANCE = share_money_result.get("balance", 0)
                    print(
                        "\n\n\n=============================\nSHARES ::\n\n\n",
                        share_money_result,
                        "\n\n\n",
                    )
                    if share_money_result.get("winners") == []:
                        RUNNING_BALANCE = BATCH_CONTRIBUTION

                    print("RUNNING_BALANCE::::", RUNNING_BALANCE)

                    return share_money_result, RUNNING_BALANCE

                share_money_result, RUNNING_BALANCE = prepare_payout(BATCH_CONTRIBUTION, RUNNING_BALANCE)
                print("\n\n\n=============================BLAKKA ::\n\n\n", "\n\n\n")
                print("====|->", share_money_result, RUNNING_BALANCE)
                print("\n\n\n=============================BLAKKA ::\n\n\n", "\n\n\n")
                print("\n\n\n=============================BLAKKA ::\n\n\n", "\n\n\n")

                clear_balance_attempts = 0

                while RUNNING_BALANCE > 4500:
                    clear_balance_attempts += 1
                    # print("\n\n\n=============================START SECOND RUN ", i)
                    print("============================SECOND RUN ")
                    print("============================SECOND RUN ")
                    print("============================SECOND RUN ")

                    share_money_result, RUNNING_BALANCE = prepare_payout(0, RUNNING_BALANCE)
                    const_obj.instant_cashout_running_balance = RUNNING_BALANCE
                    const_obj.save()

                    print("============================BLAKKA ::\n\n\n", "\n\n\n")
                    print("====|->", share_money_result, RUNNING_BALANCE)
                    print("============================BLAKKA ::\n\n\n", "\n\n\n")

                    print("============================SECOND RUN ")
                    print("============================SECOND RUN ")
                    print("============================SECOND RUN ")
                    print("============================ ENDED SECOND RUN ")

                    if clear_balance_attempts > 5:
                        break

                print("UPDATING BALANCE")
                const_obj.instant_cashout_running_balance = RUNNING_BALANCE
                const_obj.save()
                print(f"UPDATE VALUE :  {RUNNING_BALANCE}")
                print(f"UPDATED BALANCE : {const_obj.instant_cashout_running_balance}")
                RUNNING_BALANCE = 0
                BATCH_CONTRIBUTION = const_obj.instant_cashout_running_balance

                if BASE_PPS == 0:
                    BASE_PPS = play_frequency

                else:
                    pps_delta = play_frequency / BASE_PPS
                    NEW_N = BASE_N * pps_delta
                    N = NEW_N if BASE_N < NEW_N and NEW_N < 50 else BASE_N

                    if SURGE and BATCH < (PREVIOUS_BATCH_PLAYS * 0.5):
                        N = BATCH if BASE_N < BATCH else BASE_N
                        # print("OOOPSIE DOWNWARD SURGE..!!!!")
                        # print(BATCH, PREVIOUS_BATCH_PLAYS, (PREVIOUS_BATCH_PLAYS * 1.5))
                        # # input()

                    print("DELTA : ", (pps_delta), "%")
                    print("N : ", N, "players")

                # save base pps
                const_obj.pos_base_pps = BASE_PPS
                const_obj.save()

                PREVIOUS_BATCH_PLAYS = BATCH
                BATCH = 0
                GLOBAL_BATCH += 1

                print("BATCH REACHED")
                print(play_times_recent_N_section[0])
                print(play_times_recent_N_section[-1])
                print(round(time_elaspsed.total_seconds(), 2), "Secs")

                if sub_batch_time_elaspsed:
                    print(round(sub_batch_time_elaspsed.total_seconds(), 2), "Secs @batch")

                print(play_frequency, "ps/sec", end="\n\n")

                if SURGE:
                    # input("Surge please press enter")
                    SURGE = False

            LAST_PLAY_TIME = datetime.datetime.now()
            # BATCH_CONTRIBUTION = 0
            # if BATCH/N > 0: # IF THE THRESHOLD N VALUE HAS BEEN MET IN TERMS OF NUMBER OF PLAYS

            #     print("TIME TO ATTEMPT PAYOUT")
            # print(play, picks)

        # LottoTicket.objects.bulk_update(instant_cahsout_qs, ["instant_cahsout_qs", True])
        # LottoTicket.objects.bulk_update(instant_cahsout_qs, update_fields = {"instant_cahsout_qs":instant_cahsout_qs})
        # instant_cahsout_qs.update(instant_cashout_drawn = True)
        print(f"Batch contrib : {BATCH_CONTRIBUTION}")
        LottoTicket.objects.filter(pk__in=list(instant_cashout_ids)).update(instant_cashout_drawn=True)


def round_down(num):
    return num // 100 * 100
