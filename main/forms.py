from django import forms
from django.db.models import Q
from django.utils import timezone

from main.models import LotteryBatch
# from sport_app.models import FootballTable


class LotteryBatchCleanForm(forms.ModelForm):
    def clean(self):
        lottery_type = self.cleaned_data.get("lottery_type")
        is_active = self.cleaned_data.get("is_active")
        is_pos_batch = self.cleaned_data.get("is_pos_batch")
        batch_uuid = self.cleaned_data.get("batch_uuid")

        if is_active is True:
            if LotteryBatch.objects.filter(
                Q(lottery_type=lottery_type),
                Q(is_active=True),
                Q(is_pos_batch=is_pos_batch),
                ~Q(batch_uuid=batch_uuid),
            ).exists():
                raise forms.ValidationError("Lottery Type already active")

            # if LotteryBatch.objects.filter(
            #     lottery_type=lottery_type, is_active=True, is_pos_batch=False
            # ).exists():
            #     raise forms.ValidationError("Lottery Type already active")


# class FreemiumFixturesCleanForm(forms.ModelForm):
#     def clean(self):
#         soccer_freemium_fixtures_id = self.cleaned_data.get("soccer_freemium_fixtures_id")
#         if soccer_freemium_fixtures_id is not None:
#             freemium_list = soccer_freemium_fixtures_id.split(",")

#             if len(freemium_list) > 0:
#                 for id in freemium_list:
#                     foot_ball_table = FootballTable.objects.filter(
#                         fixture_id=id,
#                         fixture_date__gte=timezone.now(),
#                     ).last()

#                     if foot_ball_table is None:
#                         raise forms.ValidationError(f"Invalid fixtures id {id} for current game")
#                     else:
#                         # print("CONTINUE")
#                         FootballTable.toggle_freemium(id)
#                         continue
#         else:
#             pass
