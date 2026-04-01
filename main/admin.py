from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import LottoTicket, LotteryBatch, LotteryGlobalJackPot, LotteryWinnersTable, DisbursementTable
from main.forms import  LotteryBatchCleanForm #FreemiumFixturesCleanForm,
# from .models import ConstantVariable
# # Register your models here.



class LottoTicketResource(resources.ModelResource):
    class Meta:
        model = LottoTicket

class LotteryBatchResource(resources.ModelResource):
    class Meta:
        model = LotteryBatch

class LotteryGlobalJackPotResource(resources.ModelResource):
    class Meta:
        model = LotteryGlobalJackPot

class LotteryGlobalJackPotResource(resources.ModelResource):
    class Meta:
        model = LotteryGlobalJackPot

class LotteryWinnersTableResource(resources.ModelResource):
    class Meta:
        model = LotteryWinnersTable

class DisbursementTableResource(resources.ModelResource):
    class Meta:
        model = DisbursementTable

class LottoTicketResourceAdmin(ImportExportModelAdmin):

    raw_id_fields = ("user_profile", "batch") #"agent_profile", )
    resource_class = LottoTicketResource
    search_fields = [
        "id",
        "batch__batch_uuid",
        "user_profile__phone_number",
        # "agent_profile__email",
        "ticket",
        "game_play_id",
    ]
    list_filter = (
        "date",
        "channel",
        "telco_network",
        "lottery_type",
        "paid",
        "is_agent",
        "played_via_telco_channel",
        "instant_cashout_drawn",
        "pos_instant_cashout_drawn",
        "icash_counted",
        "icash_2_counted",
        "is_duplicate",
        "game_type",
        "s4l_drawn",
        "content_delivery_sms_sent",
        "telco_channel",
    )
    date_hierarchy = "date"

    def get_list_display(self, request):
        data = [field.name for field in self.model._meta.concrete_fields]
        data.remove("user_profile")
        # data.remove("agent_profile")
        # data.remove("batch")

        return data

class LotteryBatchResourceAdmin(ImportExportModelAdmin):
    form = LotteryBatchCleanForm
    resource_class = LotteryBatchResource
    search_fields = ["batch_uuid", "RTO", "RTP", "total_revenue"]
    list_filter = ("lottery_type", "created_date", "is_active")
    date_hierarchy = "created_date"

    def get_list_display(self, request):
        resources = [field.name for field in self.model._meta.concrete_fields]
        resources.remove("list_of_ticket_numbers")

        return resources

    actions = [
        "filterbankwinners",
        "filterretailsalaryforlifewinners",
        "run_banker_draw",
        "run_salary_for_life_draw",
    ]

class LotteryWinnersTableResourceAdmin(ImportExportModelAdmin):
        resource_class = LotteryWinnersTableResource
        search_fields = [
            "batch__batch_uuid",
            "game_play_id",
            "run_batch_id",
            "phone_number",
            "win_type",
            "pool",
            "share",
            "earning",
            "total_jackpot_amount",
        ]
        list_filter = ("date_won", "lottery_source_tag", "win_type")
        date_hierarchy = "date_won"

        def get_list_display(self, request):
            return [field.name for field in self.model._meta.concrete_fields]

class DisbursementTableResourceAdmin(ImportExportModelAdmin):
    autocomplete_fields = ["lottery_batch", "lotery_winner"]
    resource_class = DisbursementTableResource
    search_fields = [
        "player_phone_num",
        "lottery_batch__batch_uuid",
        "payout_account_num",
        "payout_account_name",
        "payout_bank_name",
    ]
    list_filter = ("date_created", "is_disbursed", "stattus")
    date_hierarchy = "date_created"

    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]

    # @admin.action(description="MANUALLY RUN DRAW BANKER WINNING FILTER")
    # def filterbankwinners(modeladmin, request, queryset):

    #     # messages.success(request, "successfully filtered banker winners")

    #     for obj in queryset:
    #         if obj.manually_filtered_winnings is True:
    #             messages.error(request, "Batch has already been filtered")
    #             continue
    #         if obj.lottery_type == "BANKER":

    #             lottery_qs = LottoTicket.objects.filter(batch=obj, paid=True, channel="POS_AGENT")

    #             plays = list(
    #                 map(
    #                     lambda x: (
    #                         x.number_of_ticket,
    #                         [int(i) for i in x.ticket.split(",")],
    #                         x.rtp,
    #                     ),
    #                     lottery_qs,
    #                 )
    #             )

    #             obj.manually_filtered_winnings = True
    #             obj.save()

    #             prices = LottoTicket.construct_earning(lottery_qs)

    #             rtp = lottery_qs.distinct().aggregate(Sum("effective_rtp"))["effective_rtp__sum"]
    #             real_rtp = lottery_qs.distinct().aggregate(Sum("rtp"))["rtp__sum"]  # FALL BACK  REAL RTP WHEN NO RTP
    #             rtp = rtp or real_rtp
    #             rtp = rtp or 0

    #             salary_for_life_jackpot_instance = LotteryGlobalJackPot.objects.filter(is_active=True).last()

    #             if salary_for_life_jackpot_instance is not None:
    #                 jackpot_amount = salary_for_life_jackpot_instance.threshold
    #             else:
    #                 jackpot_amount = 1000.00

    #             best_match_combo = machine_number_serializer(obj.lottery_winner_ticket_number)
    #             best_match_combo = best_match_combo[0]
    #             # best_match_combo = ",".join(str(i) for i in best_match_combo)

    #             # print("best_match_combo", best_match_combo, "\n\n")

    #             filterd_winners = SalaryForLifeDraw.filter_banker_winnings(
    #                 best_match_combo, plays, prices, jackpot_amount
    #             )

    #             # total_winning = SalaryForLifeDraw.deep_sum(filterd_winners)

    #             if filterd_winners:

    #                 for ticker_won in filterd_winners:
    #                     match_win_type = ticker_won[0]
    #                     match_ticket = ticker_won[1]
    #                     amount_won = ticker_won[2]
    #                     _orignal_stake_amount = ticker_won[1][2]

    #                     ticket = list(match_ticket)[1]

    #                     ticket_db_filter_qs = LottoTicket.objects.filter(
    #                         batch=obj,
    #                         ticket=serialize_ticket(ticket),
    #                         rtp=_orignal_stake_amount,
    #                     )

    #                     win_type = "PERM_4"

    #                     if match_win_type == 4:
    #                         win_type = "PERM_4"
    #                     elif match_win_type == 3:
    #                         win_type = "PERM_3"
    #                     elif match_win_type == 2:
    #                         win_type = "PERM_2"

    #                     amount_won = prices[ticker_won[1][2]][ticker_won[0]]

    #                     if ticket_db_filter_qs:
    #                         for lotto_ticket_instance in ticket_db_filter_qs:

    #                             amount_won = ticker_won[2]

    #                             if LottoWinners.objects.filter(
    #                                 game_play_id__iexact=lotto_ticket_instance.game_play_id
    #                             ).exists():
    #                                 pass
    #                             else:
    #                                 LottoWinners.create_lotto_winner_obj(
    #                                     lottery=lotto_ticket_instance,
    #                                     batch=obj,
    #                                     phone_number=lotto_ticket_instance.user_profile.phone_number,
    #                                     ticket=ticket,
    #                                     win_type="ORDINARY_WINNER",
    #                                     match_type=win_type,
    #                                     lotto_type="BANKER",
    #                                     game_play_id=lotto_ticket_instance.game_play_id,
    #                                     stake_amount=lotto_ticket_instance.stake_amount,
    #                                     earning=amount_won,
    #                                     channel_played_from=lotto_ticket_instance.channel,
    #                                     run_batch_id=obj.batch_uuid,
    #                                 )

    #             messages.success(request, "successfully filtered banker winners")
    #         else:
    #             messages.error(request, "Batch is not a banker batch")

class LotteryGlobalJackPotResourceAdmin(ImportExportModelAdmin):
    resource_class = LotteryGlobalJackPotResource
    search_fields = [
        "lottery_type",
    ]
    list_filter = ("lottery_type",)
    date_hierarchy = "created_at"

    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]


admin.site.register(LottoTicket, LottoTicketResourceAdmin)
admin.site.register(LotteryBatch, LotteryBatchResourceAdmin)
admin.site.register(LotteryGlobalJackPot, LotteryGlobalJackPotResourceAdmin)
admin.site.register(LotteryWinnersTable, LotteryWinnersTableResourceAdmin)
admin.site.register(DisbursementTable, DisbursementTableResourceAdmin)
