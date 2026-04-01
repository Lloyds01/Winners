from django.db import models
from account.managers import CustomUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from main.models import LotteryModel, UserProfile
from django.dispatch import receiver
from .signals import reset_password_token_created

# Create your models here.


class User(AbstractUser):
    CHANNEL = (
        ("WEB", "WEB"),
        ("APP/POS", "APP/POS"),
        ("MOBILE", "MOBILE"),
    )
    phone = models.CharField(_("phone number"), max_length=200, blank=True, null=True, unique=True)
    username = models.CharField(_("username"), max_length=200, blank=True, null=True, unique=True)
    email = models.EmailField(_("email address"), blank=True, null=True, unique=True)
    engage_uuid = models.CharField(_("Engage uuid"), max_length=200, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone_is_verified = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    can_withdraw = models.BooleanField(default=True)
    channel = models.CharField(max_length=200, choices=CHANNEL, default="WEB")

    objects = CustomUserManager()

    REQUIRED_FIELDS = []

    def __str__(self):
        if self.username is None or self.username == "":
            return self.email
        return self.username

    class Meta:
        verbose_name = "USER"
        verbose_name_plural = "USERS"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.phone:
                self.phone = LotteryModel.format_number_from_back_add_234(self.phone)

        else:
            if User.objects.filter(phone=LotteryModel.format_number_from_back_add_234(self.phone)).exists():
                del self.phone

        super().save(*args, **kwargs)

    def eligible_for_reset(self):
        if not self.is_active:
            # if the user is active we dont bother checking
            return False

        if getattr(settings, "DJANGO_REST_MULTITOKENAUTH_REQUIRE_USABLE_PASSWORD", True):
            # if we require a usable password then return the result of has_usable_password()
            return self.has_usable_password()
        else:
            # otherwise return True because we dont care about the result of has_usable_password()
            return True

    @classmethod
    def create_user(cls, request, serialized_data: dict = {}):
        from rest_framework.response import Response


        email = request.data.get("email", None)
        phone = request.data.get("phone", None)
        password = request.data.get("password", None)
        referral_code = request.data.get("referral_code", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)

        full_name = serialized_data.get("full_name", None)
        gender = serialized_data.get("gender", None)
        request_channel = serialized_data.get("request_channel", None)

        print("referral_code", referral_code)

        # referral section
        if referral_code and referral_code != "":
            check_referral_code = ReferralCode.get_referer_user(referral_code)

            if check_referral_code is None:
                data = {"message": "Invalid referral code"}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        try:
            phone_is_verified = False
            channel = "WEB"
            if request_channel == "MOBILE":
                phone_is_verified = True
                channel = "MOBILE"

            user = User.objects.create(
                email=email,
                phone=phone,
                password=make_password(password),
                is_active=False,
                phone_is_verified=phone_is_verified,
                channel=channel,
            )
            if first_name is not None:
                user.first_name = first_name

            if last_name is not None:
                user.last_name = last_name

            user.save()

            # ------------------- SEND ACCOUNT CREATION EVENT TO ENGAGE ------------------- #
        except Exception as e:
            print("create user error", e, "\n\n\n")
            return Response(
                {"message": "user with email or phone already exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)

        # save user in UserProfile Model
        formated_phone = LotteryModel.format_number_from_back_add_234(phone)

        # save user record in userporfile model
        # but, first check if user already exist in userprofile model
        user_profile = UserProfile.objects.filter(phone_number=formated_phone).last()
        if user_profile is None:
            user_profile = UserProfile.objects.create(phone_number=formated_phone, email=email, channel="WEB")

        # update user account details if gender and full name is provided
        if full_name and gender:
            _full_name_split = full_name_split(full_name)
            user.first_name = _full_name_split.get("first_name")
            user.last_name = _full_name_split.get("last_name") if _full_name_split.get("last_name") else _full_name_split.get("middle_name")
            user.save()

            user_profile.gender = gender.upper()
            user_profile.first_name = _full_name_split.get("first_name")
            user_profile.last_name = _full_name_split.get("last_name") if _full_name_split.get("last_name") else None
            user_profile.middle_name = _full_name_split.get("middle_name") if _full_name_split.get("middle_name") else None
            user_profile.save()
        elif first_name and last_name:
            user_profile.first_name = first_name
            user_profile.last_name = last_name
            user_profile.save()

        # save referral code
        if referral_code and referral_code != "":
            # get referral code instance
            referral_code_instance = ReferralCode.objects.filter(referral_code=referral_code).last()

            # generate referral code for this user
            get_code = ReferralCode.create_referal_code(user_profile)

            # create referral code in ReferralTable
            if referral_code_instance.user is None:
                pass
            else:
                ReferralTable.objects.create(
                    user=user_profile,
                    referral_code=get_code,
                    referred_by=referral_code_instance.user,
                )

        user_data = serialized_data

        del user_data["password"]

        try:
            del user_data["confirm_password"]
        except KeyError:
            pass

        # send activation email to user
        user_data["token"] = token.key

        # # CREDIT USER WALLET WITH BONUS
        # bonu_amount = ConstantVariable.get_constant_variable().get("bonus_amount")
        # UserWallet().fund_user_wallet_play_wallet_via_phone(user.phone, bonu_amount)

        UserWallet.objects.create(user=user_profile, wallet_tag="WEB")

        return Response(user_data, status=status.HTTP_201_CREATED)

    @classmethod
    def update_user(cls, user, **kwargs):
        serialized_data = kwargs.keys()

        # print("serialized_data", serialized_data)

        # return None

        # print("user update instance", user)
        # print("serialized_data", serialized_data)

        response = {}
        for key in serialized_data:
            if key == "phone_number":
                if kwargs.get("phone_number") is None:
                    response["phone_number"] = None
                else:
                    # print("phone number is none")
                    # print(kwargs.get("phone_number"))
                    phone = LotteryModel.format_number_from_back_add_234(kwargs.get("phone_number"))
                    user.phone = phone
                    response["phone"] = phone

            elif key == "email":
                if kwargs.get("email") is not None:
                    response["email"] = None
                else:
                    email = kwargs.get("email")
                    user.email = email
                    response["email"] = email

            elif key == "first_name":
                if kwargs.get("first_name") is not None:
                    response["first_name"] = None
                else:
                    user.first_name = kwargs.get("first_name")
                    response["first_name"] = kwargs.get("first_name")

            elif key == "last_name":
                if kwargs.get("last_name") is not None:
                    response["last_name"] = None
                else:
                    user.last_name = kwargs.get("last_name")
                    response["last_name"] = kwargs.get("last_name")

            user.save()

        update_engage_user.delay(user.id)

        return response

class UserProfileOtp(models.Model):
    OTP_TYPE = (("EMAIL_VERIFICATION", "EMAIL_VERIFICATION"),)

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    otp = models.CharField(max_length=200, editable=False)
    is_verified = models.BooleanField(default=False)
    otp_type = models.CharField(max_length=200, choices=OTP_TYPE, default="EMAIL_VERIFICATION")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.otp

    class Meta:
        verbose_name = "USER PROFILE OTP"
        verbose_name_plural = "USER PROFILE OTP"

    @classmethod
    def generate_otp(cls):
        return "".join(random.choices(string.digits, k=6))

    @property
    def minutes_ago(self):
        current_time = datetime.now(timezone.utc)
        time_difference = current_time - self.created_at
        return time_difference.total_seconds() / 60

    @classmethod
    def create_otp(cls, user_instance) -> str:
        """
        Generates and associates a One-Time Password (OTP) with a user instance.

        Parameters:
        - cls (class): The class containing this method.
        - user_instance: An instance of the user for whom the OTP is generated.

        Returns:
        - str: The generated OTP.

        This method generates a new OTP using the generate_otp() class method,
        associates it with the provided user instance, and returns the generated OTP.

        """
        otp = cls.generate_otp()
        otp_object = cls.objects.create(user=user_instance, otp=otp)
        return otp_object.otp

    @classmethod
    def verify_otp(cls, user_instance, otp) -> dict:
        """
        Verifies the provided One-Time Password (OTP) for a given user instance.

        Parameters:
        - cls (class): The class containing this method.
        - user_instance: An instance of the user for whom the OTP is being verified.
        - otp (str): The OTP to be verified.

        Returns:
        - dict: A dictionary containing verification status and a message.
          Example: {"verified": True, "message": "Verified successfully"}

        This method checks if the provided OTP is valid for the given user and has not expired.
        If the OTP is valid and has not expired, it marks the OTP as verified and returns a
        dictionary with verification status and a corresponding message.

        Example:
        # >>> user = User.objects.get(username='example_user')
        # >>> otp_to_verify = '123456'
        # >>> verification_result = OTP.verify_otp(user, otp_to_verify)
        # >>> print(verification_result)
        {'verified': True, 'message': 'Verified successfully'}
        """
        otp_qs = cls.objects.filter(user=user_instance, otp=otp, is_verified=False)
        if not otp_qs.exists():
            result = {"verified": False, "message": "Invalid OTP"}
            return result
        else:
            otp_instance = otp_qs.last()
            minute_interval = otp_instance.minutes_ago
            if minute_interval > 4:
                result = {"verified": False, "message": "OTP Expired, kindly re-verify"}
                return result
            else:
                otp_instance.is_verified = True
                otp_instance.save()
                result = {"verified": True, "message": "Verified successfully"}
                return result


class Otp(models.Model):
    OTP_TYPE = [
        ("REGISTRATION", "REGISTRATION"),
        ("PHONE_NUMBER_OTP", "PHONE_NUMBER_OTP"),
        ("PHONE_NUMBER_ACTIVATION", "PHONE_NUMBER_ACTIVATION"),
    ]

    OTP_LENGTH = 6

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    otp_type = models.CharField(max_length=200, choices=OTP_TYPE, default="REGISTRATION")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ussd_code_extension = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.otp

    class Meta:
        # ordering = ["-created_at"]
        verbose_name = "OTP TABLE"
        verbose_name_plural = "OTP TABLES"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp = Otp.generate_otp()

            if self.otp_type == "PHONE_NUMBER_OTP":
                code = Otp.generate_otp()
                self.ussd_code_extension = f"89*{code}"

            elif self.otp_type == "PHONE_NUMBER_ACTIVATION":
                code = Otp.generate_otp()
                self.ussd_code_extension = f"89*{code}"

            # send otp to user
            Otp.send_otp(self.otp, self.user.phone, self.user.email, self.otp_type)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.created_at + timedelta(minutes=60) < timezone.now()

    @classmethod
    def get_otp(cls, user: User):
        return cls.objects.filter(user=user).last()

    @classmethod
    def verify_otp(cls, user: User, otp, otp_type) -> dict:
        otp = cls.objects.filter(user=user, otp=otp, otp_type=otp_type, is_verified=False).last()
        if otp is not None:
            # check if otp is expired
            if otp.is_expired:
                return {"message": "OTP has expired", "status": False}

            else:
                otp.is_verified = True
                otp.save()
                otp.delete()

                token = Token.objects.get(user=user)
                return {
                    "message": "OTP verified successfully",
                    "token": token.key,
                    "status": True,
                }

        return {"message": "Invalid OTP", "status": False}

    @classmethod
    def resend_otp(cls, user: User, otp_type):
        otp = cls.objects.filter(user=user, otp_type=otp_type).last()
        if otp is not None:
            otp.delete()
        return cls.objects.create(user=user, otp_type=otp_type)

    @staticmethod
    def generate_otp():
        return "".join(random.choices(string.digits, k=Otp.OTP_LENGTH))

    @staticmethod
    def send_otp(otp, phone, email, otp_type):
        if otp_type == "REGISTRATION":
            # send registration otp to user

            # email otp
            try:
                email_sender = EmailHandler(email)
                email_sender.otp_activation_email(otp)
            except Exception as e:
                print(e)

            # sms otp
            # try:
            #     account_activation_otp_sms(phone, otp)
            # except Exception as e:
            #     print(e)

        elif otp_type == "PHONE_NUMBER_OTP":
            try:
                account_activation_otp_sms(phone, otp)
            except Exception as e:
                print(e)

        elif otp_type == "PHONE_NUMBER_ACTIVATION":
            try:
                account_activation_otp_sms(phone, otp)
            except Exception as e:
                print(e)

        return {"message": "otp sent successfully"}

    @classmethod
    def ussd_code_phone_mumber_activation(cls, phone, ussd_code):
        print(
            f"""

              ussd_code_phone_mumber_activation: {phone}, {ussd_code}

              """
        )

        otp = cls.objects.filter(user__phone=phone, ussd_code_extension=ussd_code, is_verified=False).last()

        print(f"otp instance: {otp}", "\n\n\n\n\n")
        if otp is not None:
            # check if otp is expired
            if otp.is_expired:
                return "END OTP has expired"

            if otp.otp_type == "PHONE_NUMBER_ACTIVATION":
                user = User.objects.filter(phone=phone).last()
                user.phone_is_verified = True
                user.save()

                otp.is_verified = True
                otp.save()

                return "END Phone number verified successfully"
            elif otp.otp_type == "PHONE_NUMBER_OTP":
                return f"END Your OTP is {otp.otp}"
            else:
                return "END Invalid command"

        else:
            return "END Invalid command"


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    token = f"token={reset_password_token.key}"

    # send an email to the user
    EmailHandler(reset_password_token.user.email).forgot_password_email(token)


class ResetPasswordToken(models.Model):
    class Meta:
        verbose_name = _("PASSWORD RESET TOKEN")
        verbose_name_plural = _("PASSWORD RESET TOKENS")

    @staticmethod
    def generate_key():
        """generates a pseudo random code using os.urandom and binascii.hexlify"""
        return TOKEN_GENERATOR_CLASS.generate_token()

    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        User,
        related_name="password_reset_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token"),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("When was this token generated"))

    # Key field, though it is not the primary key of the model
    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)

    ip_address = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="",
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default="",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ResetPasswordToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)


class BlackListed(models.Model):
    data = models.JSONField(help_text='{"emails": ["email1@example.com", "email2@example.com"],"phones": ["123-456-7890", "987-654-3210"]}')
    withdrawal = models.JSONField(
        help_text='{"emails": ["email1@example.com", "email2@example.com"],"phones": ["123-456-7890", "987-654-3210"]}',
        blank=True,
        null=True,
    )
    instant_cashout_game = models.JSONField(
        help_text='{"emails": ["email1@example.com", "email2@example.com"],"phones": ["123-456-7890", "987-654-3210"]}',
        blank=True,
        null=True,
    )
    salary_for_life_game = models.JSONField(
        help_text='{"emails": ["email1@example.com", "email2@example.com"],"phones": ["123-456-7890", "987-654-3210"]}',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ["-created_at"]
        verbose_name = "BLACK LISTED"
        verbose_name_plural = "BLACK LISTED"

    @classmethod
    def is_blacklisted(cls, email=None, phone=None):
        data = cls.objects.last()
        if data is not None:
            if email is not None:
                if email in data.data["emails"]:
                    return True
            if phone is not None:
                phone = User.format_number_from_back_add_234(phone)
                if phone in data.data["phones"]:
                    return True

            return False

        return False

    @classmethod
    def can_withdraw(cls, email=None, phone=None):
        # check if the phone number is a glo number
        if phone is not None:
            telco_user_instance = TelcoUsers.objects.using("external2").filter(phone_number=phone, network="GLO").first()
            if telco_user_instance is not None:
                return True

        data = cls.objects.last()
        if data is not None:
            if email is not None:
                if email in data.withdrawal["emails"]:
                    return True
            if phone is not None:
                if len(phone) != 13:
                    phone = User.format_number_from_back_add_234(phone)
                if phone in data.withdrawal["phones"]:
                    return True

            return False

        return False

    @classmethod
    def can_play_instant_cashout(cls, email=None, phone=None):
        data = cls.objects.last()
        if data is not None:
            if email is not None:
                if email in data.instant_cashout_game["emails"]:
                    return False
            if phone is not None:
                phone = User.format_number_from_back_add_234(phone)
                if phone in data.instant_cashout_game["phones"]:
                    return False

            return True

        return True

    @classmethod
    def can_play_salary_for_life(cls, email=None, phone=None):
        data = cls.objects.last()
        if data is not None:
            if email is not None:
                if email in data.salary_for_life_game["emails"]:
                    return False
            if phone is not None:
                phone = User.format_number_from_back_add_234(phone)
                if phone in data.salary_for_life_game["phones"]:
                    return False

            return True

        return True


class TelcosPhoneNumber(models.Model):
    NETWORK = (
        ("NETWORK_PROVIDER", "NETWORK_PROVIDER"),
        ("MTN", "MTN"),
        ("9MOBILE", "9MOBILE"),
        ("GLO", "GLO"),
        ("AIRTEL", "AIRTEL"),
    )
    GENDER = (
        ("GENDER", "GENDER"),
        ("MALE", "MALE"),
        ("FEMALE", "FEMALE"),
    )

    first_name = models.CharField(null=True, blank=True, max_length=200)
    last_name = models.CharField(null=True, blank=True, max_length=200)
    phone_number = models.CharField(null=True, blank=True, max_length=200, unique=True)
    network = models.CharField(null=True, blank=True, max_length=200, choices=NETWORK, default="NETWORK_PROVIDER")
    gender = models.CharField(null=True, blank=True, max_length=200, choices=GENDER, default="GENDER")
    dob = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True, default=0)
    state = models.CharField(null=True, blank=True, max_length=200)
    usage_naira = models.CharField(null=True, blank=True, max_length=200)
    phone_type = models.CharField(null=True, blank=True, max_length=200)
    address = models.CharField(null=True, blank=True, max_length=200)
    lga = models.CharField(null=True, blank=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # MSISDN,FIRSTNAME,LASTNAME,GENDER,DOB, AGE,STATE,ADDRESS,LGA,USAGE_NAIRA,PHONE_TYPE,

    def __str__(self):
        return self.first_name

    class Meta:
        unique_together = (
            "phone_number",
            "network",
        )
        verbose_name = "TELCO PHONE NUMBER"
        verbose_name_plural = "TELCO PHONE NUMBERS"
