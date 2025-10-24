import uuid
from django.db import models
from datetime import datetime, time, timedelta
from django.contrib.postgres.fields import ArrayField
from django.db.models.functions import Now, TruncDate


SERVICE_TYPE = [
    ("AWOOF", "AWOOF"),
    ("INSURANCE", "INSURANCE"),
]

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("MALE", "MALE"),
        ("FEMALE", "FEMALE"),
        ("OTHER", "OTHER"),
    ]

    CHANNEL = [
        ("USSD", "USSD"),
        ("WEB", "WEB"),
        ("USSD/WEB", "USSD/WEB"),
        ("WEB/USSD", "WEB/USSD"),
        ("MOBILE", "MOBILE"),
        ("POS", "POS"),
    ]

    NETWORK_PROVIDER = (
        ("MTN", "MTN"),
        ("GLO", "GLO"),
    )
    phone_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    account_num = models.CharField(max_length=150, null=True, blank=True)
    account_name = models.CharField(max_length=150, null=True, blank=True)
    bank_name = models.CharField(max_length=150, null=True, blank=True)
    bank_code = models.CharField(max_length=150, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    loandisk_player_id = models.CharField(max_length=150, null=True, blank=True)
    on_loandisk = models.BooleanField(default=False)
    ministry = models.CharField(max_length=300, null=True, blank=True)
    auth_code = models.CharField(max_length=100, null=True, blank=True)
    bvn_number = models.CharField(max_length=100, null=True, blank=True)
    gender = models.CharField(max_length=200, choices=GENDER_CHOICES, default="OTHER")
    # profile_img = CloudinaryField("image", null=True, blank=True)
    channel = models.CharField(max_length=200, choices=CHANNEL, default="USSD")
    pin = models.CharField(max_length=125, null=True, blank=True)
    has_pin = models.BooleanField(default=False)
    has_web_virtual_account = models.BooleanField(default=False)
    has_sudo_phone_number = models.BooleanField(default=False)
    has_sudo_email = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    avatar = models.URLField(max_length=2300, null=True, blank=True)
    debt_amount = models.FloatField(default=0.00)
    recovered_debt = models.FloatField(default=0.00)
    from_telco = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=250, editable=False, null=True, blank=True)
    email_is_verified = models.BooleanField(default=False)
    preverified_email = models.CharField(max_length=125, null=True, blank=True)
    network_provider = models.CharField(max_length=125, null=True, blank=True, choices=NETWORK_PROVIDER)

    def __str__(self) -> str:
        return str(self.phone_number)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.phone_number:
                self.phone_number = LotteryModel.format_number_from_back_add_234(self.phone_number)
                if UserProfile.objects.filter(phone_number=self.phone_number).exists():
                    pass
                else:
                    return super(UserProfile, self).save(*args, **kwargs)

class LotteryModel(models.Model):
    phone = models.CharField(max_length=300)


    @staticmethod
    def format_number_from_back_add_234(phone) -> str:
        if phone is None:
            return None

        formatted_num = phone[-10:]
        if formatted_num[0] == "0":
            return None
        else:
            return "234" + formatted_num
    pass

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


class LotteryGlobalJackPot(models.Model):
    """
    This model is used to store the salary for life jackpot amount
    """

    LOTTERY_TYPE = [
        ("SALARY_FOR_LIFE", "SALARY_FOR_LIFE"),
        ("INSTANT_CASHOUT", "INSTANT_CASHOUT"),
    ]

    threshold = models.FloatField(default=0.0)
    contributed_amount = models.FloatField(default=0.0)
    lottery_type = models.CharField(max_length=250, choices=LOTTERY_TYPE, default="SALARY_FOR_LIFE")
    is_active = models.BooleanField(default=True)
    is_drawn = models.BooleanField(default=False)
    jackpot_id = models.CharField(max_length=250, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lottery_type}-{self.jackpot_id}"

    class Meta:
        verbose_name = "MEGACSH FOR LIFE JACKPOT"
        verbose_name_plural = "MEGACSH FOR LIFE JACKPOT"

    def save(self, *args, **kwargs):
        if not self.pk:
            # check if jackpot is already active

            if LotteryGlobalJackPot.objects.filter(jackpot_id=self.jackpot_id).exists():
                self.jackpot_id = uuid.uuid4()
        return super(Jackpot, self).save(*args, **kwargs)

    @classmethod
    def get_jackpot(cls):
        """
        This method is used to get the jackpot amount
        """
        jackpot = cls.objects.filter(is_active=True).last()

        try:
            percentage = round((jackpot.contributed_amount / jackpot.threshold) * 100)
        except ZeroDivisionError:
            percentage = 0

        if jackpot:
            return {
                "threshold": jackpot.threshold,
                "contributed_amount": jackpot.contributed_amount,
                "percentage": percentage,
            }
        return {}

    @classmethod
    def get_jackpot_instance(cls):
        """
        This method is used to get the jackpot amount
        """
        jackpot = cls.objects.filter(is_active=True).last()

        if jackpot:
            return jackpot
        else:
            jackpot = cls.objects.create(threshold=1000000, contributed_amount=0.0)
            return jackpot

    @classmethod
    def update_jackpot(cls, amount):
        """
        This method is used to update the jackpot amount
        """
        jackpot = cls.objects.filter(is_active=True).last()
        if jackpot:
            jackpot.alltime_contributed_amount += amount
            jackpot.contributed_amount = amount
            jackpot.save()
        else:
            pass

    @classmethod
    def add_to_jackpot(cls, amount, lottery_type):
        """
        This method is used to add to the jackpot amount
        """
        jackpot = cls.objects.filter(is_active=True, lottery_type=lottery_type).last()
        if jackpot:
            jackpot.alltime_contributed_amount += amount
            jackpot.contributed_amount += amount
            jackpot.save()
        else:
            cls.objects.create(
                threshold=1000000,
                contributed_amount=float(amount),
                lottery_type=lottery_type,
            )

    def save(self, *args, **kwargs):  # noqa
        if not self.pk:
            # check if there is an active jackpot
            jackpot = self.__class__.objects.filter(is_active=True).last()
            if jackpot:
                raise ValidationError("There is an active jackpot")

        return super(LotteryGlobalJackPot, self).save(*args, **kwargs)


def generate_batch_uuid_func():
    formatted_month = datetime.now().strftime("%b%Y")  # Make sure to import datetime
    return f"{formatted_month}-{uuid.uuid4()}"

class LotteryBatch(models.Model):
    # super_winners
    # total_unique_paid_players_in_pool

    formatted_month = datetime.strftime(datetime.now(), "%b")

    LOTTERY_TYPE = [
        ("SALARY_FOR_LIFE", "SALARY_FOR_LIFE"),
        ("INSTANT_CASHOUT", "INSTANT_CASHOUT"),
        ("WYSE_CASH", "WYSE_CASH"),
        ("WHYSE_LOAN", "WHYSE_LOAN"),
        ("QUIKA", "QUIKA"),
        ("BANKER", "BANKER"),
    ]

    batch_uuid = models.CharField(max_length=150, default=generate_batch_uuid_func)
    total_players_in_pool = models.PositiveIntegerField(null=True, blank=True)
    total_unique_players_in_pool = models.PositiveIntegerField(null=True, blank=True)
    global_jackpot = models.ForeignKey("LotteryGlobalJackPot", on_delete=models.CASCADE, null=True, blank=True)
    total_unique_paid_playyers_in_pool = models.PositiveIntegerField(null=True, blank=True)
    total_accumulated_unpaid = models.FloatField(null=True, blank=True)
    total_accumulated_paid = models.FloatField(null=True, blank=True)
    total_accumulated_all = models.FloatField(null=True, blank=True)
    total_jackpot_amount_10 = models.FloatField(null=True, blank=True)
    total_jackpot_amount_50 = models.FloatField(null=True, blank=True)
    total_jackpot_amount_250 = models.FloatField(null=True, blank=True)
    total_jackpot_amount_500 = models.FloatField(null=True, blank=True)
    total_jackpot_amount_1000 = models.FloatField(null=True, blank=True)
    total_amount_won = models.FloatField(null=True, blank=True)
    RTO = models.FloatField(default=30)
    RTP = models.FloatField(null=True, blank=True)
    total_revenue = models.FloatField(null=True, blank=True)
    super_winers = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_pos_active = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    draw_date = models.DateTimeField(blank=True, null=True)
    batch_start = models.DateTimeField(null=True, blank=True)
    batch_end = models.DateTimeField(null=True, blank=True)
    lottery_type = models.CharField(max_length=100, choices=LOTTERY_TYPE, default="WHYSE_LOAN")
    lottery_winner_ticket = models.TextField(
        blank=True,
        null=True,
        help_text="Serialization of the winner ticket/selection of numbers",
    )
    lottery_winner_ticket_number = models.TextField(blank=True, null=True, help_text="The winning ticket number")
    instant_cashout_player_threshold = models.PositiveIntegerField(default=0, editable=False)
    is_pos_batch = models.BooleanField(default=False)
    list_of_ticket_numbers = ArrayField(models.IntegerField(), blank=True, null=True)
    manually_filtered_winnings = models.BooleanField(default=False)
    pending_telco_draw = models.BooleanField(default=False)

    @staticmethod
    def batch_paid_amount(batch):
        return list(
            PaymentTransaction.objects.filter(Q(has_paid=True) & Q(lottery_batch=batch))
            .aggregate(Sum("amount"))
            .values()
        )[0]

    @staticmethod
    def batch_paid_amount_today(batch):
        # start_date = datetime.today()
        # end_date
        # return list(
        #     PaymentTransaction.objects.filter(
        #         Q(has_paid=True)
        #         & Q(lottery_batch__id=batch.id)
        #         & Q(date_paid__date=datetime.today().date())
        #     )
        #     .aggregate(Sum("amount"))
        #     .values()
        # )[0]W

        if LotteryModel.objects.filter(batch__id=batch.id).exists():
            return (
                LotteryModel.objects.filter(batch__id=batch.id, date__date=timezone.now().date(), paid=True)
                .aggregate(Sum("amount_paid"))
                .get("amount_paid__sum")
            )

        elif LottoTicket.objects.filter(batch__id=batch.id).exists():
            return (
                LottoTicket.objects.filter(batch__id=batch.id, date__date=timezone.now().date(), paid=True)
                .aggregate(Sum("amount_paid"))
                .get("amount_paid__sum")
            )

        else:
            0

    def __str__(self):
        return str(self.batch_uuid)

    class Meta:
        verbose_name = "LOTTERY BATCH"
        verbose_name_plural = "LOTTERY BATCHES"

    @classmethod
    def get_current_batch(cls):
        return cls.objects.filter(is_active=True).last()

    def instant_cash_draw(self):
        # if self.lottery_type == "INSTANT_CASHOUT":
        #     self.lottery_winner_ticket = serialize_ticket([1,3,45,6,7,8,8])
        #     self.save()

        pass

    def clean(self):
        if self.lottery_type == "SALARY_FOR_LIFE" and self.global_jackpot is None:
            raise ValidationError("Global jackpot is required for salary for life")

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.lottery_type == "INSTANT_CASHOUT":
                # select random nth player for instant cashout draw
                number_range = ConstantVariable.get_constant_variable().get("instant_cashout_win_range_number")
                random_number = random.randrange(int(number_range.split("-")[0]), int(number_range.split("-")[1]), 10)

                self.instant_cashout_player_threshold = int(random_number)

                redis_storage = RedisStorage(f"{self.batch_uuid}-instant_cashout-nth_player")
                redis_storage.set_data(random_number)

                # save active bacth to redis
                redis_storage = RedisStorage("instant_cashout_active_batch")
                redis_storage.set_data(self.batch_uuid)

            if self.lottery_type == "SALARY_FOR_LIFE":
                if self.list_of_ticket_numbers is None or self.list_of_ticket_numbers == []:
                    self.list_of_ticket_numbers = LotteryBatch.salary_for_life_list_of_ticket_numbers()

            # --------------------------------------------  raise exception if a lottery batch is already active -------------------------------------------- #
            if self.is_active is True:
                if self.is_pos_batch is False:
                    if LotteryBatch.objects.filter(
                        lottery_type=self.lottery_type,
                        is_active=True,
                        is_pos_batch=False,
                    ).exists():
                        return ValidationError("A lottery batch is already active")

                # save lottery batch rto and rtp in redis
                redis_storage = RedisStorage(f"{self.lottery_type}-rto")
                redis_storage.set_data(self.RTO)

            # --------------------------------------------  raise exception if a lottery batch is already active -------------------------------------------- #

            # check if lottery batch uuid already exists
            formatted_month = datetime.strftime(datetime.now(), "%b")
            if LotteryBatch.objects.filter(batch_uuid=self.batch_uuid).exists():
                self.batch_uuid = f"{formatted_month}-{str(uuid.uuid4())}"

        return super(LotteryBatch, self).save(*args, **kwargs)

    @classmethod
    def create_batch(cls, **kwargs):
        global_jackpot = LotteryGlobalJackPot.get_jackpot_instance()

        instance = cls()
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.global_jackpot = global_jackpot
        instance.save()

        return instance

    @classmethod
    def salary_for_life_list_of_ticket_numbers(cls):
        # random number from 1 to 50
        random_list_50_numbers = random.sample(range(1, 51), 50)

        # random single number from 1 to 39
        random_single_number = random.randint(1, 38)

        slicer_pointer = random_single_number + 10

        sliced_random_number_list = random_list_50_numbers[random_single_number:slicer_pointer]

        poped_list_from_random_list_50_numbers = (
            random_list_50_numbers[0:random_single_number] + random_list_50_numbers[slicer_pointer:-1]
        )

        num_list_1 = poped_list_from_random_list_50_numbers * 100
        num_list_2 = sliced_random_number_list * 2

        return num_list_1 + num_list_2



class LottoTicket(models.Model):
    NETWORK_PROVIDER = (
        ("MTN", "MTN"),
        ("GLO", "GLO"),
    )

    TELCO_CHANNEL = [
        ("BROADBASE", "BROADBASE"),
        ("YELLOW_DOT_AFRICA", "YELLOW_DOT_AFRICA"),
    ]

    LOTTO_CHANNEL = [
        ("USSD", "USSD"),
        ("USSD_WEB", "USSD_WEB"),
        ("WEB", "WEB"),
        ("MOBILE", "MOBILE"),
        ("POS_AGENT", "POS_AGENT"),
        ("SYSTEM_BONUS", "SYSTEM_BONUS"),
    ]

    LOTTO_TYPE = [
        ("SALARY_FOR_LIFE", "SALARY_FOR_LIFE"),
        ("INSTANT_CASHOUT", "INSTANT_CASHOUT"),
        ("QUIKA", "QUIKA"),  # new game
        ("VIRTUAL_SOCCER", "VIRTUAL_SOCCER"),
        ("BANKER", "BANKER"),
    ]

    LOTTO_SOURCE = [
        ("NORMAL", "NORMAL"),
        ("BONUS", "BONUS"),
    ]

    GAME_TYPE = [
        ("AWOOF", "AWOOF"),
        ("NORMAL", "NORMAL"),
    ]

    DRAWN_FOR_CHOICES = [
        ("GLOBAL", "GLOBAL"),
        ("LOCAL", "LOCAL"),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # agent_profile = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey(LotteryBatch, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=300)
    stake_amount = models.FloatField(default=0.00)
    potential_winning = models.FloatField(default=0.00)
    expected_amount = models.FloatField(default=0.00)
    amount_paid = models.FloatField(default=0.00, db_index=True)
    illusion = models.FloatField(default=0.00)
    rto = models.FloatField(default=0.00)
    rtp = models.FloatField(default=0.00)
    rtp_per = models.FloatField(default=0.00)
    effective_rtp = models.FloatField(default=0.00)
    commission_per = models.FloatField(default=0.00)
    commission_value = models.FloatField(default=0.00)
    salary_for_life_jackpot_per = models.FloatField(default=0.00)
    salary_for_life_jackpot_amount = models.FloatField(default=0.00)
    win_commission_per = models.FloatField(default=0.00)
    win_commission_value = models.FloatField(default=0.00)
    ussd_telco_commission = models.FloatField(default=0.00)
    ussd_telco_commission_value = models.FloatField(default=0.00)
    ussd_telco_aggregator_commission = models.FloatField(default=0.00)
    ussd_telco_aggregator_commission_value = models.FloatField(default=0.00)
    paid = models.BooleanField(default=False, db_index=True)
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    number_of_ticket = models.IntegerField(default=0, db_index=True)
    channel = models.CharField(max_length=150, choices=LOTTO_CHANNEL, default="POS_AGENT", db_index=True)
    game_play_id = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    unique_game_play_id = models.CharField(max_length=150, null=True, blank=True)

    awoof_game_play_id = models.CharField(max_length=150, null=True, blank=True)
    lottery_type = models.CharField(max_length=150, choices=LOTTO_TYPE, default="SALARY_FOR_LIFE", db_index=True)
    lottery_source = models.CharField(max_length=150, choices=LOTTO_SOURCE, default="NORMAL", db_index=True)
    game_type = models.CharField(max_length=150, choices=GAME_TYPE, default="NORMAL", db_index=True)
    service_type = models.CharField(
        max_length=150,
        choices=SERVICE_TYPE,
        default="AWOOF",
        db_index=True,
        help_text="the type of service played, Awoof or Insurance",
    )
    has_interest = models.BooleanField(default=True)
    ticket = models.CharField(
        max_length=200,
        help_text="Serialization of the ticket/selection of numbers made by the player",
    )
    system_generated_num = models.CharField(max_length=300, null=True, blank=True)
    win_combo = models.CharField(
        max_length=200,
        help_text="Actual complete winning number for batch",
        null=True,
        blank=True,
    )
    is_agent = models.BooleanField(default=False)
    s4l_drawn = models.BooleanField(default=False)
    instant_cashout_drawn = models.BooleanField(default=False)
    pos_instant_cashout_drawn = models.BooleanField(default=False)
    icash_counted = models.BooleanField(default=False)
    icash_2_counted = models.BooleanField(default=False)
    icash_local_counted = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    game_id_treated = models.BooleanField(
        default=False,
        help_text="This tracks if or not a game id has been treated or not, because instant cash treats individual tickets seperately, but the paid amounts are not lumped, but have to be infered by a multiplication by the game ID.",
    )
    pin = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Pin use for cashout if the lottery is played from POS_AGENT and "
        "the player didn't provide his phone number. This's not the same as the pin used for retail ticket",
    )
    identity_id = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="This is basically created for transactional purpose",
    )
    played_via_telco_channel = models.BooleanField(default=False)
    telco_channel = models.CharField(
        max_length=150,
        choices=TELCO_CHANNEL,
        default="BROADBASE",
        help_text="This is the channel through which the ticket was played, either via telco or not",
    )
    is_new_quika_game = models.BooleanField(default=False)
    telco_network = models.CharField(
        max_length=150,
        choices=NETWORK_PROVIDER,
        blank=True,
        null=True,
    )
    drawn_for = models.CharField(max_length=25, choices=DRAWN_FOR_CHOICES, default="GLOBAL")
    seeder_status = models.CharField(
        max_length=100,
        choices=(("COMPLETE", "COMPLETE"), ("PROCESSING", "PROCESSING"), ("PENDING", "PENDING")),
        default="PENDING",
        help_text="Current status of the seeder for this ticket.",
    )
    content_delivery_sms_sent = models.BooleanField(default=False)
    product_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    # def __init__(self, *args, **kwargs):
    #     super(LottoTicket, self).__init__(*args, **kwargs)
    #     self._original_paid = self.paid
    #     self._original_amount_paid = self.amount_paid

    class Meta:
        verbose_name = "MEGACASH & STEADYWIN TICKET"
        verbose_name_plural = "MEGACASH & STEADYWIN TICKETS"
        indexes = [
            models.Index(fields=["phone", "paid", "channel"]),
            models.Index(fields=["game_play_id"]),
            models.Index(fields=["paid"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["lottery_type"]),
            models.Index(fields=["seeder_status"]),
            models.Index(TruncDate("date"), "date", name="date_date_idx"),
        ]

    def save(self, *args, **kwargs):
        """
        Override the default save method for the LottoTicket model to handle various business logic.

        This method performs several operations:
        1. Ensures batch records are saved
        2. Handles agent-related operations
        3. Processes financial calculations (commissions, RTO, RTP, etc.)
        4. Updates various wallets based on ticket status and channel
        5. Manages jackpot contributions

        Args:
            *args: Variable length argument list passed to parent save method
            **kwargs: Arbitrary keyword arguments passed to parent save method

        Returns:
            The result of the parent save method
        """
        # Save associated batch if it exists but hasn't been saved yet
        if self.batch is not None and self.batch.pk is None:
            self.batch.save()

        # Handle agent profile settings
        if self.agent_profile:
            self.is_agent = True

        # Track iCash local counting for agent profiles
        if self.paid and self.agent_profile and not self.icash_local_counted:
            self.icash_local_counted = True

        # Round financial values to 2 decimal places
        self.amount_paid = round(self.amount_paid, 2)
        self.expected_amount = round(self.expected_amount, 2)
        self.illusion = round(self.illusion, 2)

        # Handle existing ticket updates
        if self.pk:
            # Retrieve original values for comparison
            _original_paid = False

            old = self.__class__.objects.get(pk=self._get_pk_val())
            for field in self.__class__._meta.fields:
                if field.name == "paid":
                    _original_paid = field.value_from_object(old)
                elif field.name in ["amount_paid", "instant_cashout_drawn"]:
                    field.value_from_object(old)

            # Process payment status changes
            if _original_paid != self.paid and self.paid is True:
                self._process_payment()

                # UPDATING RTP AND RTO IN GAME DAILY ACTIVITIES TABLE
                if self.agent_profile:
                    _from_lotto_agent = True if self.agent_profile.terminal_id is not None else False
                    try:
                        GamesDailyActivities.create_record(
                            game_type=self.lottery_type, rtp=self.rtp, rto=self.rto, from_lotto_agent=_from_lotto_agent
                        )
                    except:
                        pass

                    try:
                        RetailWalletTransactions.create_debit_record_for_game_play(
                            amount=self.amount_paid,
                            wallet_value=self.rtp,
                            rto_value=self.rto,
                            rtp_value=self.rtp,
                            game_type=self.lottery_type,
                        )
                    except:
                        pass

                    agent_instance = self.agent_profile
                    GeneralRetailLottoGames.create_record(
                        agent_phone_number=agent_instance.phone,
                        agent_name=agent_instance.full_name,
                        agent_email=agent_instance.email,
                        batch_uuid=self.batch.batch_uuid,
                        game_play_id=self.game_play_id,
                        game_pin=self.pin,
                        lucky_number=self.ticket,
                        purchase_amount=self.amount_paid,
                        lotto_db_id=self.id,
                        paid=self.paid,
                        number_of_ticket=self.number_of_ticket,
                        rtp=self.rtp,
                        rto=self.rto,
                        commission_percentage=self.commission_per,
                        type_of_agent=agent_instance.agent_type,
                        lotto_game_type=self.lottery_type,
                        potential_winnings=self.potential_winning,
                    )

        # Set unique game play ID
        self.unique_game_play_id = self.game_play_id

        # Ensure batch is saved
        if self.batch is not None and self.batch.pk is None:
            self.batch.save()

        # Call parent save method
        return super(LottoTicket, self).save(*args, **kwargs)

    def _process_payment(self):
        """
        Process payment for an existing ticket that has been marked as paid.

        This method handles:
        - Commission calculations
        - RTP (Return to Player) calculations
        - RTO (Return to Operator) calculations
        - Jackpot contributions
        - Wallet updates

        Returns:
            None, or early returns None if batch is missing
        """

        # Early return if batch is missing
        if self.batch is None:
            return None

        amount_paid_after_removing_comission = self.amount_paid

        # Handle POS_AGENT / MOBILE APP / WEB channels
        if self.channel in ["POS_AGENT", "MOBILE", "WEB"]:
            self._process_agent_mobile_web_payment(amount_paid_after_removing_comission)
        else:
            # Handle USSD and other channels
            self._process_other_channels_payment(amount_paid_after_removing_comission)

        # Update agent commission
        if self.channel == "POS_AGENT":
            if self.agent_profile:
                AgentWallet.reward_commission(
                    agent_id=self.agent_profile.id,
                    game_play_amount=self.amount_paid,
                    commission_type="COMMISSION_ON_GAME_PLAY",
                    game_type=self.lottery_type,
                    rto_amount=self.rto,
                )