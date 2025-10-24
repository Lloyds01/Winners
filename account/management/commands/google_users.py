from django.core.management.base import BaseCommand

from account.models import User
from main.models import ConstantVariable, UserProfile
from wallet_app.models import UserWallet


class Command(BaseCommand):
    help = "CREATE DUMMY PHONE FOR USERS THAT SIGNUP USING GOOGLE"

    def handle(self, *args, **options):
        users = User.objects.filter(phone=None)
        if users:
            for user in users:
                phone = User().sudo_phone_number()

                UserProfile.objects.create(
                    phone_number=phone,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    has_sudo_phone_number=True,
                )

                user.phone = phone
                user.save()

                # CREDIT USER WALLET WITH BONUS
                bonu_amount = ConstantVariable.get_constant_variable().get("bonus_amount")
                UserWallet().fund_user_wallet_play_wallet_via_phone(user.phone, bonu_amount)

        else:
            print("No users to update")

        print("Done")
