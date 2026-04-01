
from django.core.validators import MinValueValidator
from rest_framework import serializers

# from main.helpers.helper_functions import mask_winners_phone_number
# from main.models import CreditCard, LotteryWinnersTable

from .models import (
    # ContactUsForm,
    # ErroneousTransferRefundLog,
    LottoTicket,
    # SalaryForLifeParticipant,
    # SalaryForLifeSponsor,
    # ScratchCardPartnership,
    # Waitlist,
)


class MainLottoTicketSerializer(serializers.ModelSerializer):
    depth = 1

    class Meta:
        model = LottoTicket
        fields = "__all__"