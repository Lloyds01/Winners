from django.db import models

# Create your models here.


# class ConstantVariable4(models.Model):
#     SHARING = [
#         "BLACK",
#         "BLACK",
#         "WHITE",
#         "BLACK",
#         "WHITE",
#         "BLACK",
#         "BLACK",
#         "BLACK",
#         "BLACK",
#         "BLACK",
#         "WHITE",
#         "BLACK",
#         "WHITE",
#         "BLACK",
#         "WHITE",
#     ]

#     USSD_BANK_PAYMENT_METHOD_CHOICES = (
#         ("WATU_PAY", "WATU_PAY"),
#         ("CORAL_PAY", "CORAL_PAY"),
#         ("REDBILLER", "REDBILLER"),
#     )

#     LINK_SHORTENER_CHOICES = (
#         ("BITLY", "BITLY"),
#         ("CUSTOM", "CUSTOM"),
#         ("CUTTLY", "CUTTLY"),
#     )

#     ICASH_TYPES = (
#         ("NEW ICASH", "NEW ICASH"),
#         ("OLD ICASH", "OLD ICASH"),
#         ("MIX ICASH", "MIX ICASH"),
#     )

#     DRAW_STYLES = (
#         ("GLOBAL", "GLOBAL"),
#         ("LOCAL", "LOCAL"),
#     )

#     OVERPAY_STATE = (
#         ("HIGH_RTP", "HIGH_RTP"),
#         ("LOW_RTP", "LOW_RTP"),
#     )

#     PAYOUT_SOURCE_CHOICES = (
#         ("WOVEN", "WOVEN"),
#         ("VFD", "VFD"),
#         ("BUDDY", "BUDDY"),
#         ("NOT_AVAILABLE", "NOT_AVAILABLE"),
#     )

#     JACKPOT_WINNING_CHANNEL_CHOICES = (
#         ("USSD", "USSD"),
#         ("WEB", "WEB"),
#         ("MOBILE", "MOBILE"),
#         ("POS_AGENT", "POS_AGENT"),
#         ("SYSTEM_BONUS", "SYSTEM_BONUS"),
#         ("ALL", "ALL"),
#     )

#     JACKPOT_GAME_CHOICES = (
#         ("ALL", "ALL"),
#         ("SALARY_FOR_LIFE", "SALARY_FOR_LIFE"),
#         ("INSTANT_CASHOUT", "INSTANT_CASHOUT"),
#         ("WYSE_CASH", "WYSE_CASH"),
#         ("WHYSE_LOAN", "WHYSE_LOAN"),
#         ("QUIKA", "QUIKA"),
#     )

#     GAME_illusion_FEATURE_CHOICES = (
#         ("OFF", "OFF"),
#         ("LOCAL", "LOCAL"),
#         ("GLOBAL", "GLOBAL"),
    # )
    # last_overpay_switch_time = models.DateTimeField(null=True, blank=True)
    # overpay_state = models.CharField(
    #     default="LOW_RTP",
    #     max_length=20,
    #     choices=OVERPAY_STATE,
    #     help_text="OVERPAY OR UNDERPAY RTP WINNINGS",
    # )
    # overpay_threshold = models.FloatField(
    #     default=0.00,
    #     help_text="ACCUMULATOR FOR TOTAL AMOUNT ACCUMULATED BEFORE STATE CHANGE OF OVERPAY STATE ",
    # )
    # overpay_threshold_percent = models.FloatField(
    #     default=0.00,
    #     help_text="ACCUMULATOR FOR TOTAL AMOUNT ACCUMULATED BEFORE STATE CHANGE OF OVERPAY STATE PERCENT",
    # )
    # shave_percent = models.FloatField(
    #     default=0.85,
    #     help_text="PERCENT SHAVE ON WINNINGS",
    # )
    # bulk_bonus_total_amount = models.FloatField(default=0.00, help_text="CUMMULATIVE BONUS AMOUNT TO SEED INTO GAME")
    # bulk_bonus_giveout_unit_amount = models.FloatField(
    #     default=0.00,
    #     help_text="AMOUNT TO GIVE OUT EACH TIME FROM THE CUMMULATIVE UNTIL EXHAUSTED",
    # )

    # banker_booster_balance = models.FloatField(default=0)
    # banker_booster_percent = models.CharField(
    #     default="1,2",
    #     max_length=50,
    #     help_text="Percentage increase in RTP at every draw",
    # )
    # banker_topup_balance = models.FloatField(default=0)
    # banker_booster_amount = models.CharField(
    #     default="1000,10000, 100",
    #     max_length=50,
    #     help_text="Fixed addition to RTP at every draw",
    # )
    # lotto_scratch_card_amount = models.FloatField(default=0)
    # lotto_agent_commission_percent = models.IntegerField(default=15)

    # delay_icash_winnings = models.BooleanField(default=True)
    # block_very_other_white = models.BooleanField(default=True)
    # allow_white = models.BooleanField(default=True)
    # suppress_a_percent_of_wins = models.BooleanField(default=False, help_text="This is for instant cash pending wins")
    # suppression_percent = models.IntegerField(default=0, help_text="Ignore this. (Deprecated)")
    # suppress_after_threshold = models.IntegerField(default=0)
    # suppression_count = models.IntegerField(default=0)
    # icash_winnings_divisor = models.FloatField(default=1.00, help_text="AMOUNT TO DIVIDE ICASH WINNINGS BY.")
    # global_agent_icash_sold = models.IntegerField(
    #     default=1, help_text="Total tickets sold by agents since last icash give out"
    # )
    # global_agent_icash_sold_dict = models.JSONField(default=dict)
    # icash_flavour_dict = models.JSONField(default=dict, blank=True, null=True)
    # icash_bonus_bias_dict = models.JSONField(default=icash_bonus_bias_dict_func, blank=True, null=True)
    # count_to_giver = models.IntegerField(
    #     default=0,
    # )
    # icash_contribution = models.FloatField(
    #     default=0,
    #     help_text="This tracks the total amount of money contributed by tickets. It is used with the 'icash_contribution_threshold' to release winnings.",
    # )
    # icash_contribution_threshold = models.FloatField(
    #     default=2000,
    #     help_text="This is the max threshold before a winning is released. Ususally the average of all possible winnings.",
    # )
    # icash_bonus_cap = models.FloatField(
    #     default=2000,
    #     help_text="This is the maximum winning that can be released on instant cash when bonus is active. Bonus entry model should feed this value once it has been created.",
    # )
    # icash_bonus_contribution = models.FloatField(
    #     default=2000,
    #     help_text="This is the total amount of bonus that has been given out since. once this is equal to bonus_cap, the bonuses should stop.",
    # )
    # new_quika_icash_count_to_giver = models.JSONField(
    #     new_quika_icash_count_to_giver_func,
    #     help_text="Total tickets globally before bonus on new Icash",
    # )
    # old_quika_icash_count_to_giver = models.JSONField(
    #     default=old_quika_icash_count_to_giver_func,
    #     help_text="Total tickets globally before bonus on old Icash",
    # )
    # icash_marketting_bonus_dict_feed = models.JSONField(
    #     default=dict,
    #     help_text="COPY OF DICTIONARY CONTAINING THE SCHEDULE OF BONUS GIVE OUTS WHERE GIVE OUTS ACTUALLY HAPPEN",
    # )
    # icash_marketting_bonus_dict_reference = models.JSONField(
    #     default=dict, help_text="DICTIONARY CONTAINING THE SCHEDULE OF BONUS GIVE OUTS"
    # )
    # icash_marketting_params = models.JSONField(
    #     default=dict, help_text="DICTIONARY CONTAINING MAIN BULK BONUS ALLOCATIONS"
    # )
    # seed_out_marketting_bonuses = models.BooleanField(default=False)
    # icash_excesses_from_count_before = models.FloatField(default=0)
    # excesses_giveout_threshold = models.CharField(max_length=120, default="300,1050,50")
    # giver_deployed = models.BooleanField(default=False)
    # giver_threshold = models.CharField(max_length=10, default="3,5")
    # new_icash2_draw_mode = models.CharField(
    #     max_length=100,
    #     choices=DRAW_STYLES,
    #     default="GLOBAL",
    #     help_text="Whether to draw instant cashout globally or locally.",
    # )
    # icash2_draw_mode = models.CharField(
    #     max_length=100,
    #     choices=DRAW_STYLES,
    #     default="GLOBAL",
    #     help_text="This has been depreacated. Please do not change.",
    # )
    # agent_play_counts_cleared = models.BooleanField(
    #     default=False,
    #     editable=False,
    #     help_text="Not to be altered manually. This value is used by the system to clear accumulated agent plays while in global draw mode ",
    # )
    # icash_base_n = models.IntegerField(default=9, help_text="Lower values here will always slow down winnings.")
    # icash_flavour_divisor = models.CharField(
    #     max_length=10,
    #     default="20,20",
    #     help_text="Any set value here will be divided by to this is to allow decimals with out breaking the random selector",
    # )
    # icash2_global_bonus_threshold = models.JSONField(
    #     default=dict, help_text="Total tickets globally before bonus on new Icash"
    # )
    # icash2_quika_giveout_tier = models.JSONField(
    #     default=dict,
    #     help_text="Tier to give out on quicka. This is to reatin a good average",
    # )
    # icash2_local_bonus_threshold = models.IntegerField(default=0)
    # icash2_global_bonus_available = models.FloatField(default=0.00)
    # icash2_local_bonus_available = models.FloatField(default=0.00)
    # icash_to_use = models.CharField(
    #     max_length=100,
    #     choices=ICASH_TYPES,
    #     default="NEW ICASH",
    #     help_text="Whether to draw instant cashoutold or new.",
    # )
    # icash_black_white_ratio = models.CharField(max_length=10, default="1,2")

    # game_show_lottery_ticket_cost = models.FloatField(default=1000.00)
    # game_lottery_ticket_count = models.IntegerField(default=10000)
    # game_lottery_instant_win_percentage = models.IntegerField(default=100)

    # game_lottery_instant_win_max_amount = models.FloatField(default=8000.00)
    # game_lottery_instant_win_mid_amount = models.FloatField(default=2000.00)
    # game_lottery_instant_win_min_amount = models.FloatField(default=1000.00)

    # game_lottery_weekly_win_amount = models.FloatField(default=200000.00)
    # game_lottery_weekly_game_show_amount = models.FloatField(default=1000000.00)

    # golden_hour_ticket_price = models.FloatField(default=1000.00)
    # golden_hour_no_winners = models.IntegerField(default=5)
    # golden_hour_daily_winning_amount = models.FloatField(default=100000.00)

    # sharing = models.JSONField(
    #     default=sharing_dict_func, help_text="Sharing mix for black white give outs for instant cashout."
    # )
    # icash_rtps = models.JSONField(default=dict)
    # ratio_for_icash2_bonus = models.CharField(max_length=10, default="7,11")
    # merge_pos_draw_icash = models.BooleanField(default=True)
    # merge_pos_draw_s4l = models.BooleanField(default=True)
    # restrict_s4l_to_lower_wins = models.BooleanField(default=False)
    # max_s4l_single_win_to_rtp = models.IntegerField(default=1)
    # s4l_number_of_match_limit = models.IntegerField(
    #     default=3,
    #     help_text="This determined how many numbers are matched per draw. 2 means up to 2 of 5 and 3 means up to 3 of 5.",
    # )
    # game_threshold = models.PositiveIntegerField()
    # winning_percentage = models.FloatField(default=0.00)
    # rto = models.FloatField(default=0.0)
    # rtp = models.FloatField(default=1.0)
    # rtp_s4l_bank_wysecash = models.FloatField(default=1.0)
    # global_jackpot_perc = models.FloatField(default=1.0)
    # salary_4_life_global_jackpot_perc = models.FloatField(default=1.0)
    # plays = models.PositiveIntegerField(default=0.0)
    # game_bands = models.JSONField(null=True, blank=True, default=dict)

    # payout_by_stake_summary = models.BooleanField(default=True)
    # stake_amount_summary = models.FloatField(null=True, blank=True, default=1000000.00)

    # payout_periodically = models.BooleanField(default=False)
    # monthly = models.BooleanField(default=False)
    # weekly = models.BooleanField(default=False)
    # daily = models.BooleanField(default=False)
    # hourly = models.BooleanField(default=False)
    # start_date_periodically = models.DateTimeField(null=True, blank=True)

    # payout_by_number_of_players = models.BooleanField(default=False)
    # number_of_players = models.PositiveBigIntegerField(null=True, blank=True)

    # payout_by_fixed_date = models.BooleanField(default=False)
    # fixed_date = models.DateTimeField(null=True, blank=True)
    # referral_reward_percentage = models.FloatField(default=15.0)
    # collect_bvn = models.BooleanField(default=False)
    # instant_cashout_win_range_number = models.CharField(
    #     max_length=100,
    #     default="80-150",
    #     help_text="This is the range of numbers that will be used to determine the nth player for instant cashout batch",
    # )
    # help_text = "To vary Rewards percentage where the first value is the minimum and right next to it is the step"
    # upper_tier = models.CharField(max_length=100, default="20,20", help_text=help_text)
    # middle_tier = models.CharField(max_length=100, default="20,20", help_text=help_text)
    # lower_tier = models.CharField(max_length=100, default="30,30", help_text=help_text)
    # last_tier = models.CharField(max_length=100, default="50,10", help_text=help_text)
    # wyse_cash_win_factor = models.JSONField(null=True, blank=True)
    # s4l_win_factor_constant = models.CharField(max_length=100, default="100,100")
    # nummber_of_duplicate_lottery_to_create = models.PositiveIntegerField(
    #     default=4, help_text="Number of duplicate lottery to create"
    # )

    # pos_agent_commission = models.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     default=0.05,
    #     help_text="This is the commission percentage for POS agent",
    # )

    # ussd_bank_payment_method = models.CharField(
    #     max_length=100, choices=USSD_BANK_PAYMENT_METHOD_CHOICES, default="WATU_PAY"
    # )
    # coralpay_biller_code = models.CharField(max_length=100, default="542")

    # wyse_cash_running_balance = models.FloatField(default=0.00, editable=False)
    # instant_cashout_running_balance = models.FloatField(default=0.00, editable=False)
    # salary_4_life_running_balance = models.FloatField(default=0.00)  # Making field editable
    # salary_4_life_current_total_winnings = models.FloatField(default=0.00, editable=False)
    # s4l_telco_tickets_inclusion_ratio = models.CharField(
    #     max_length=10,
    #     default="3:4",
    #     help_text="Ratio for including telco tickets in SalaryForLife draws (e.g., '3:4' means include telco tickets in 3 out of 7 draws)",
    # )

    # pos_wyse_cash_running_balance = models.FloatField(default=0.00)
    # pos_instant_cashout_running_balance = models.FloatField(default=0.00)
    # pos_salary_4_life_running_balance = models.FloatField(default=0.00)
    # salary_4_life_draw_ip = models.CharField(max_length=100, default="localhost")
    # pos_base_pps = models.FloatField(default=0.00)
    # pos_bonus_wysecash_max_amount = models.FloatField(default=1500.00)
    # pos_bonus_wysecash_max_qty = models.FloatField(default=20)
    # pos_bonus_cutoff_amount = models.FloatField(
    #     default=20,
    #     help_text="If an agent has reached this amount in sales, he may not receive more bonus",
    # )
    # pos_plays_since_last_icash = models.FloatField(
    #     default=5,
    #     help_text="how many plays since last i-cash pending win was made available for pos",
    # )
    # plays_since_last_icash = models.FloatField(
    #     default=5,
    #     help_text="how many plays since last i-cash pending win was made available web",
    # )
    # plays_before_icash = models.CharField(
    #     default="5,16",
    #     max_length=10,
    #     help_text="how many plays since last i-cash pending win was made available web",
    # )

    # merge_wysecash_draws = models.BooleanField(default=False)
    # merge_icash_draws = models.BooleanField(default=False)
    # merge_salary4life_draws = models.BooleanField(default=False)

    # # Scoccer Cash Const Variable
    # freemuim_play = models.BooleanField(default=False)
    # soccer_freemium_fixtures_id = models.CharField(max_length=300, null=True, blank=True)
    # freemium_winner_range = models.IntegerField(default=0)
    # freemium_leagues_count = models.IntegerField(default=0)
    # freemuim_play_count = models.IntegerField(default=1)

    # base_pps = models.FloatField(default=0.00)

    # merge_decisioning = models.BooleanField(
    #     default=False,
    #     help_text="This is to enable or disable the merge decisioning. If enabled, the merge decisioning for all lottery games will be merged",
    # )
    # create_pos_duplicate_lottery = models.BooleanField(
    #     default=False,
    #     help_text="This is to enable or disable the creation of duplicate lottery games for POS. If enabled, the duplicate lottery games for all lottery games will be created",
    # )

    # agent_bonus_amount = models.FloatField(default=0.00)

    # instant_cashout_n = models.FloatField(default=0.00)
    # bonus_amount = models.FloatField(default=0.00)
    # updated_at = models.DateTimeField(auto_now=True)
    # payout_source = models.CharField(max_length=100, choices=PAYOUT_SOURCE_CHOICES, default="NOT_AVAILABLE")
    # paid_global_jackpot_count = models.IntegerField(default=11)
    # jackpot_winning_channel = models.CharField(
    #     max_length=100, choices=JACKPOT_WINNING_CHANNEL_CHOICES, null=True, blank=True
    # )
    # jackpot_game_choice = models.CharField(max_length=100, choices=JACKPOT_GAME_CHOICES, default="INSTANT_CASHOUT")
    # link_shortener = models.CharField(
    #     max_lenhth=100, choices=LINK_SHORTENER_CHOICES, default="BITLY"
    # )
    # instant_cashout_line_restriction = models.CharField(default="1,3,5", max_length=20)
    # quika_line_restriction = models.CharField(default="1", max_length=20)
    # quika_stake_amount_restriction = models.CharField(default="100", max_length=200)
    # quika_winning_amount_restriction = models.CharField(default="1000", max_length=200)
    # game_illusion_feature = models.CharField(max_length=100, default="OFF", choices=GAME_illusion_FEATURE_CHOICES)
    # banker_running_balance = models.FloatField(default=0.00)
    # limit_wining_amount = models.BooleanField(
    #     default=True,
    #     help_text="This value will flip flop, and allow large winnings one time "
    #     "when false and limit large winning when true on instantcash("
    #     "banker)",
    # )
    # general_sms_charges = models.FloatField(default=3)
    # banker_draw_countdown_time = models.DateTimeField(blank=True, null=True)
    # use_new_icash_price = models.BooleanField(default=False)
    # winwise_agents_salary_amount = models.FloatField(
    #     default=0.00,
    #     help_text="This represents the monthly salary amount for Winwise Staff agents",
    # )
    # telco_commission = models.FloatField(
    #     default=0.00,
    #     help_text="this represents the percentage charge for all game played via telco channel. NOTE. any figure put in here will be divided by 100. e.g 90 / 100 = 0.9",
    # )
    # telco_rtp = models.FloatField(
    #     default=0.00,
    #     help_text="this represents the percentage charge for all game played via telco channel. NOTE. any figure put in here will be divided by 100. e.g 90 / 100 = 0.9",
    # )
    # aggregator_commission = models.FloatField(
    #     default=0.00,
    #     help_text="this represents the percentage charge for all game played via telco channel. NOTE. any figure put in here will be divided by 100. e.g 90 / 100 = 0.9",
    # )
    # last_lotto_ticket_count = models.FloatField(
    #     default=0.00,
    #     help_text="Number of instantcash tickets sold at last count",
    # )
    # telco_bonus_purse_value = models.FloatField(
    #     default=0.00,
    #     help_text="Total amount waiting to be given out to telco",
    # )
    # telco_bonus_give_threshold = models.IntegerField(
    #     default=0.00,
    #     help_text="Count before dropping each telco bonus",
    # )
    # i_cash_jackpot_winning_amount = models.FloatField(default=0.00)
    # total_icash_jackpot_winning = models.FloatField(default=0.00)
    # mancala_running_bal = models.FloatField(default=1000.00)

    # new_icash_fifty_drought_bonus_draw_type = models.CharField(
    #     max_length=100,
    #     default="BONUS",
    # )
    # new_icash_fifty_drought_bonus_ticket_count = models.IntegerField(default=0)
    # new_icash_fifty_drought_bonus_contributed_ticket_count = models.IntegerField(default=0)
    # new_icash_fifty_iteration_reset_number = models.IntegerField(default=15)
    # new_icash_fifty_iterated_count = models.IntegerField(default=0)

    # new_icash_hundred_drought_bonus_draw_type = models.CharField(
    #     max_length=100,
    #     default="BONUS",
    # )
    # new_icash_hundred_drought_bonus_ticket_count = models.IntegerField(default=0)
    # new_icash_hundred_drought_bonus_contributed_ticket_count = models.IntegerField(default=0)
    # new_icash_hundred_iteration_reset_number = models.IntegerField(default=15)
    # new_icash_hundred_iterated_count = models.IntegerField(default=0)

    # general_drought_control_bonus_draw_type = models.CharField(
    #     max_length=100,
    #     default="BONUS",
    # )
    # general_drought_control_expected_contribution = models.FloatField(default=200)
    # general_drought_control_contributed_value = models.FloatField(default=0)
    # general_drought_control_count_value = models.FloatField(default=0)
    # general_drought_control_iteration_reset_number = models.IntegerField(default=12)
    # general_drought_control_iterated_count = models.IntegerField(default=0)
    # users_exempted_from_limit = models.TextField(default="")
    # drought_enabled = models.BooleanField(
    #     default=False, help_text="Enable bonus winnings after a number of plays if there are no winnings"
    # )

    # def __str__(self):
    #     return "Constant Variables"



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