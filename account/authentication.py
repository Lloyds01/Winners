import base64
import binascii
from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

# from account.models import BlackListed
from main.models import LotteryModel, UserProfile

utc = pytz.UTC


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Expiring token for mobile and desktop clients.
    It expires every {n} hrs requiring client to supply valid username
    and password for new one to be created.
    """

    model = Token

    def authenticate_credentials(self, key, request=None):
        models = self.get_model()

        try:
            token = models.objects.select_related("user").get(key=key)

        except AttributeError:
            raise AuthenticationFailed("Invalid token")
        except models.DoesNotExist:
            raise AuthenticationFailed({"message": "Invalid or Inactive Token", "is_authenticated": False})

        if not token.user.is_active:
            raise AuthenticationFailed({"message": "Invalid user", "is_authenticated": False})

        utc_now = timezone.now()
        # utc_now = utc.localize(timezone.now())
        # utc_now = utc_now.replace(tzinfo=pytz.utc)

        if token.created < utc_now - settings.TOKEN_TTL:
            token.delete()
            raise AuthenticationFailed({"message": "Token has expired", "is_authenticated": False})
        return token.user, token


class EmailBackend(ModelBackend):
    """
    Authenticate using an e-mail address.
    """

    def authenticate(self, request, email=None, phone=None, password=None, **kwargs):
        # print("e-mail address auth backend", "\n\n\n\n")
        from account.models import User

        if email:
            try:
                user = User.objects.get(email=email)

                if user.check_password(password):
                    return user
                else:
                    raise Exception("Invalid Credentials")
            except User.DoesNotExist:
                return None
        elif phone:
            try:
                phone = LotteryModel.format_number_from_back_add_234(phone)
                print("phone", phone, "\n\n\n\n\n")
                user = User.objects.get(phone=phone)
                if user.check_password(password):
                    return user
                else:
                    raise Exception("Invalid Credentials")
            except User.DoesNotExist:
                return None

    def get_user(self, user_id):
        from account.models import User

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class PhoneBackend(ModelBackend):
    """
    Authenticate using an phone number.
    """

    # print("phone auth backend", "\n\n\n\n")
    def authenticate(self, request, phone=None, password=None, **kwargs):
        from account.models import User

        try:
            user = User.objects.get(phone=phone)

            if user.check_password(password):
                return user
            else:
                raise Exception("Invalid Credentials")
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        from account.models import User

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class CustomBasicAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication against username/password.
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b"basic":
            return None

        if len(auth) == 1:
            msg = _("Invalid basic header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid basic header. Credentials string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            try:
                auth_decoded = base64.b64decode(auth[1]).decode("utf-8")
            except UnicodeDecodeError:
                auth_decoded = base64.b64decode(auth[1]).decode("latin-1")
            auth_parts = auth_decoded.partition(":")
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = _("Invalid basic header. Credentials not correctly base64 encoded.")
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self.authenticate_credentials(userid, password, request)

    def authenticate_credentials(self, userid, password, request=None):
        """
        Authenticate the userid and password against username and password
        with optional request for context.
        """
        # credentials = {get_user_model().USERNAME_FIELD: userid, "password": password}
        # user = authenticate(request=request, **credentials)

        if userid.casefold() != settings.CORAL_PAY_AUTH_USERNAME.casefold():
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        if password.casefold() != settings.CORAL_PAY_AUTH_PASSWORD.casefold():
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        # if user is None:
        #     raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        # if not user.is_active:
        #     raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return None

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get("HTTP_AUTHORIZATION", b"")
    if isinstance(auth, str):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)

    return auth


class PabblyCustomBasicAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication against username/password.
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b"basic":
            return None

        if len(auth) == 1:
            msg = _("Invalid basic header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid basic header. Credentials string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            try:
                auth_decoded = base64.b64decode(auth[1]).decode("utf-8")
            except UnicodeDecodeError:
                auth_decoded = base64.b64decode(auth[1]).decode("latin-1")
            auth_parts = auth_decoded.partition(":")
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = _("Invalid basic header. Credentials not correctly base64 encoded.")
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self.authenticate_credentials(userid, password, request)

    def authenticate_credentials(self, userid, password, request=None):
        """
        Authenticate the userid and password against username and password
        with optional request for context.
        """
        # credentials = {get_user_model().USERNAME_FIELD: userid, "password": password}
        # user = authenticate(request=request, **credentials)

        if userid.casefold() != settings.PABBLY_AUTH_USERNAME.casefold():
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        if password.casefold() != settings.PABBLY_AUTH_PASSWORD.casefold():
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        # if user is None:
        #     raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        # if not user.is_active:
        #     raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return None

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm


class AgencyBankingFundingAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication against username/password.
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.

        """

        auth = get_authorization_header(request).split()

        if auth is None or len(auth) == 0:
            msg = _("Invalid be header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)

        if not auth or auth[0].lower() != b"bearer":
            return None

        if len(auth) == 1:
            msg = _("Invalid be header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid be header. Credentials string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            try:
                auth_decoded = base64.b64decode(auth[1]).decode("utf-8")
            except UnicodeDecodeError:
                auth_decoded = base64.b64decode(auth[1]).decode("latin-1")
            auth_parts = auth_decoded.partition(":")
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = _("Invalid be header. Credentials not correctly base64 encoded.")
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        return self.authenticate_credentials(userid, password, request)

    def authenticate_credentials(self, userid, password, request=None):
        """
        Authenticate the userid and password against username and password
        with optional request for context.
        """
        # credentials = {get_user_model().USERNAME_FIELD: userid, "password": password}
        # user = authenticate(request=request, **credentials)

        # print(f"""
        # """)

        if userid.casefold() != settings.LIBERTY_VAS_AUTH_USERNAME.casefold():
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        if password.casefold() != settings.LIBERTY_VAS_AUTH_PASSWORD.casefold():
            raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        # if user is None:
        #     raise exceptions.AuthenticationFailed(_("Invalid username/password."))

        # if not user.is_active:
        #     raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return None

    def authenticate_header(self, request):
        return 'Basic realm="%s"' % self.www_authenticate_realm


class CustomTokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: 01f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = "Token"
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token

        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        print(
            "get_authorization_header(request)",
            get_authorization_header(request),
            "\n\n",
        )
        auth = get_authorization_header(request).split()

        if len(auth) == 0:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)

        print("auth", auth, "\n\n")

        if len(auth) == 2:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 1:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[0].decode()
        except UnicodeError:
            msg = _("Invalid token header. Token string should not contain invalid characters.")
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword


# ----------------- Custom Base Permission ----------------- #
class CustomOperationHolderMixin:
    def __and__(self, other):
        return CustomOperandHolder(CustomAND, self, other)

    def __or__(self, other):
        return CustomOperandHolder(CustomOR, self, other)

    def __rand__(self, other):
        return CustomOperandHolder(CustomAND, other, self)

    def __ror__(self, other):
        return CustomOperandHolder(CustomOR, other, self)

    def __invert__(self):
        return CustomSingleOperandHolder(NOT, self)


class CustomSingleOperandHolder(CustomOperationHolderMixin):
    def __init__(self, operator_class, op1_class):
        self.operator_class = operator_class
        self.op1_class = op1_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        return self.operator_class(op1)


class CustomOperandHolder(CustomOperationHolderMixin):
    def __init__(self, operator_class, op1_class, op2_class):
        self.operator_class = operator_class
        self.op1_class = op1_class
        self.op2_class = op2_class

    def __call__(self, *args, **kwargs):
        op1 = self.op1_class(*args, **kwargs)
        op2 = self.op2_class(*args, **kwargs)
        return self.operator_class(op1, op2)


class CustomBasePermissionMetaclass(CustomOperationHolderMixin, type):
    pass


class CustomAND:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, request, view):
        return self.op1.has_permission(request, view) and self.op2.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return self.op1.has_object_permission(request, view, obj) and self.op2.has_object_permission(
            request, view, obj
        )


class CustomOR:
    def __init__(self, op1, op2):
        self.op1 = op1
        self.op2 = op2

    def has_permission(self, request, view):
        return self.op1.has_permission(request, view) or self.op2.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return self.op1.has_object_permission(request, view, obj) or self.op2.has_object_permission(request, view, obj)


class NOT:
    def __init__(self, op1):
        self.op1 = op1

    def has_permission(self, request, view):
        return not self.op1.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return not self.op1.has_object_permission(request, view, obj)


class CustomBasePermission(metaclass=CustomBasePermissionMetaclass):
    """
    A base class from which all permission classes should inherit.
    """

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True


class PhoneNumberVerifedPermission(BaseAuthentication):
    """
    Allows access only to phone number verified users users.
    """

    def has_permission(self, request, view):
        if request.user and request.user.phone_is_verified:
            return True

        else:
            msg = _("Phone number is not verified.")
            raise exceptions.AuthenticationFailed(msg)


class IsAgentRemittanceDuePermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        agent = Agent.objects.filter(Q(phone=request.user.phone) | Q(email=request.user.email)).last()
        if agent is None:
            return True

        if AgentConstantVariables().get_unable_to_remit_but_allow_to_access_lotto() is True:
            return True

        _remittance_due_data = LottoAgentRemittanceTable().is_remittance_due(agent.id)

        if _remittance_due_data.get("status") is True:
            msg = _(
                f"Hello {agent.name}, you have a due remittance. Please remit your due amount {round(_remittance_due_data.get('amount'))} to continue."  # noqa
            )

            raise exceptions.AuthenticationFailed(msg)

        # check if agent pre funding has been settled
        if agent.wave == "WAVE_TWO":
            if (agent.has_settled_pre_funding is False) and (agent.agent_type == "LOTTO_AGENT") and (agent.terminal_id is not None):
                # check if agent pre funding amount has been credited
                if not TerminalPrefundingMoneyTransfer.objects.filter(
                    agent_phone=agent.phone, status="SUCCESSFUL"
                ).exists():
                    
                    failed_attempts = TerminalPrefundingMoneyTransfer.objects.filter(
                        agent_phone=agent.phone, status="FAILED"
                    )
                    
                    if len(failed_attempts) > 1:
                        msg = _(
                            f"Hello {agent.name}, your pre-funding amount has not been credited, please contact support"  # noqa
                        )
                        
                        raise exceptions.AuthenticationFailed(msg)
                    else:
                        
                        
                        last_failed_attempt = failed_attempts.last()
                        
                        lotto_agent_pre_funding_amount = AgentConstantVariables().get_lotto_agent_pre_funding_amount()
                        
                        if last_failed_attempt is not None:
                            last_failed_attempt.re_initiated = True
                            last_failed_attempt.save()
                            
                        
                        TerminalPrefundingMoneyTransfer.create_record(
                            amount=lotto_agent_pre_funding_amount,
                            agent_phone=agent.phone,
                            agent_name=agent.full_name,
                            agent_terminal_id=agent.terminal_id,
                        )
                        
                    
                    
                
                    
                    

                    

                agent.has_settled_pre_funding = True
                agent.save()
                agent.refresh_from_db()

        # check if agent is from wave 2 and has no supervisor
        if agent.wave == "WAVE_TWO":
            if agent.is_a_vertical_lead is False:
                if agent.agent_type == "LOTTO_AGENT" and agent.supervisor is None:
                    if agent.is_supervisor is False:

                        agent.fetch_supervisor_detail_on_agency_banking_and_update

                        if agent.supervisor is None:
                            # check if agent super
                            msg = _(
                                f"Hello {agent.name}, you currently don't have a supervisor assigned to you. please, contact support"  # noqa
                            )

                            raise exceptions.AuthenticationFailed(msg)

        return True


class IsBlackListedPermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        if BlackListed().is_blacklisted(email=request.user.email, phone=request.user.phone) is True:
            msg = _("You are blacklisted. Please contact winwise admin to resolve this issue.")
            raise exceptions.AuthenticationFailed(msg)

        else:
            return True


class UserDetailsPermission(BaseAuthentication):
    """ """

    def has_permission(self, request, view):
        user_profile = UserProfile.objects.filter(phone_number=request.user.phone).last()
        if user_profile is None:
            msg = _("Please update your profile.")

        if (
            (user_profile.first_name is None)
            or (user_profile.last_name is None)
            or (user_profile.email is None)
            or (user_profile.gender is None)
        ):
            msg = _("Please update your profile.")
            raise exceptions.AuthenticationFailed(msg)

        return True


class WithdrawalPermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        if BlackListed().can_withdraw(email=request.user.email, phone=request.user.phone) is True:
            msg = _(
                "Sorry, you are not allowed to withdraw at the moment. Please contact winwise admin to resolve this issue."
            )
            raise exceptions.AuthenticationFailed(msg)

        elif request.user.can_withdraw is False:
            msg = _(
                "Sorry, you are not allowed to withdraw at the moment. Please contact winwise admin to resolve this issue."
            )
            raise exceptions.AuthenticationFailed(msg)

        else:
            return True


class IsAgentSuspendedPermission(BaseAuthentication):
    """
    Allows access only to phone number verified users users.
    """

    def has_permission(self, request, view):
        agent = Agent.objects.filter(Q(phone=request.user.phone) | Q(email=request.user.email)).last()
        if agent is None:
            return True

            # msg = _("please contact winwise admin to verify your account.")
            # raise exceptions.AuthenticationFailed(msg)

        if agent.agent_type in ["LOTTO_AGENT", "AGENT"]:
            if agent.terminal_id is None:
                msg = _(
                    f"Hello {agent.name}, as {agent.agent_type} you are required to have a terminal id. Please contact winwise admin to continue."
                )
                raise exceptions.AuthenticationFailed(msg)

        if agent.is_suspended:
            msg = _(f"Hello {agent.name}, your account has been suspended. Please contact winwise admin to continue.")
            raise exceptions.AuthenticationFailed(msg)

        if agent.suspended_on_agency_banking is True:
            msg = _(f"Hello {agent.name}, your account has been suspended. Please contact winwise admin to continue.")
            raise exceptions.AuthenticationFailed(msg)

        if agent.should_have_super_agent is True:
            if agent.super_agent is None:
                msg = _(
                    f"Hello {agent.name}, your account should be linked to a super agent. Please contact winwise admin to continue."
                )
                raise exceptions.AuthenticationFailed(msg)
        else:
            return True


class SuperUserPermission(BaseAuthentication):
    """
    Allows access only to phone number verified users users.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        else:
            msg = _("You are not allowed to access this resource.")
            raise exceptions.AuthenticationFailed(msg)


class SuperUser2Permission(BaseAuthentication):
    """
    Allows access only to phone number verified users users.
    """

    def has_permission(self, request, view):
        if settings.DEBUG is True:
            return True

        if request.user.is_staff:
            if (
                request.user.username == "joe"
                or request.user.username == "chisom"
                or request.user.username == "admin"
                or request.user.username == "oti"
            ):
                return True
            elif request.user.email in ["lolu@libertyng.com"]:
                return True
            else:
                msg = _("Please meet Joseph or Chisom for access.")
                raise exceptions.AuthenticationFailed(msg)
        else:
            msg = _("You are not allowed to access this resource.")
            raise exceptions.AuthenticationFailed(msg)


class GhanaLottoDrawPermissionPermission(BaseAuthentication):
    """
    Allows access only to agents that can play (before draw closing time) and don't have due remittance.
    """

    def has_permission(self, request, view):
        africa_lotto_constant = AfricaLottoConstants.objects.last()
        if africa_lotto_constant is None:
            africa_lotto_constant = AfricaLottoConstants.objects.create(minimum_stake=50)

        # Get current time in 12-hour format
        TODAY = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
        current_time_str = TODAY.strftime("%I:%M %p")  # Ensures 12-hour format with AM/PM

        # Get day of the week to check if it's weekend
        day_of_week = TODAY.strftime("%A").lower()
        is_weekend = day_of_week in ["saturday", "sunday"]

        # Get draw end time and period from constants based on whether it's a weekend or not
        if is_weekend:
            if day_of_week == "sunday":
                draw_end_time_str = str(africa_lotto_constant.weekend_draw_end_time)
            else:
                draw_end_time_str = str(africa_lotto_constant.draw_end_time)
        else:
            draw_end_time_str = str(africa_lotto_constant.draw_end_time)

        draw_end_period = africa_lotto_constant.draw_end_time_period.upper()

        # print(f"draw_end_time_str: {draw_end_time_str}, draw_end_period: {draw_end_period}")
        # print(f"current_time_str: {current_time_str}")

        # Convert draw_end_time_str to 12-hour format with AM/PM
        if ":" not in draw_end_time_str:
            draw_end_time_str = f"{int(draw_end_time_str)}:00"
        draw_end_time_formatted = f"{draw_end_time_str} {draw_end_period}"

        # Check if draw is closed
        if self.is_draw_closed(current_time_str, draw_end_time_formatted):
            msg = _("Draw is closed. You cannot play at this time.")
            TOMORROW = TODAY + timedelta(days=1)
            day_of_week = TOMORROW.strftime("%A")
            name_of_new_batch = None

            if str(day_of_week).lower() == "sunday":
                name_of_new_batch = "sunday aseda"
            elif str(day_of_week).lower() == "monday":
                name_of_new_batch = "monday special"
            elif str(day_of_week).lower() == "tuesday":
                name_of_new_batch = "lucky tuesday"
            elif str(day_of_week).lower() == "wednesday":
                name_of_new_batch = "midweek"
            elif str(day_of_week).lower() == "thursday":
                name_of_new_batch = "fortune thursday"
            elif str(day_of_week).lower() == "friday":
                name_of_new_batch = "friday bonanza"
            elif str(day_of_week).lower() == "saturday":
                name_of_new_batch = "national weekly"

            try:
                AfricaLottoBatch.objects.create(
                    game_type=AfricaLottoGameType.GHANA_LOTTO, batch_name=name_of_new_batch
                )
            except Exception:
                pass

            raise PermissionDenied({"message": msg})
            # raise exceptions.AuthenticationFailed(msg)

        return True

    def is_draw_closed(self, current_time_str, draw_end_time_str):
        """
        Check if the current time has passed the draw closing time, considering next-day draws.
        """
        # Get today's date and timezone
        TODAY = datetime.now(tz=pytz.timezone(settings.TIME_ZONE)).date()

        # Convert time strings to datetime objects
        current_time = datetime.strptime(current_time_str, "%I:%M %p").replace(
            year=TODAY.year, month=TODAY.month, day=TODAY.day
        )
        draw_end_time = datetime.strptime(draw_end_time_str, "%I:%M %p").replace(
            year=TODAY.year, month=TODAY.month, day=TODAY.day
        )

        # If draw end time is in the early hours (e.g., 12:30 AM), it belongs to the next day
        if "AM" in draw_end_time_str and current_time.strftime("%p") == "PM":
            draw_end_time += timedelta(days=1)  # Move draw time to the next day

        print(f"Current Time: {current_time}")
        print(f"Draw End Time: {draw_end_time}")

        return current_time >= draw_end_time


class KenyaLottoDrawPermission(BaseAuthentication):
    """
    Allows access only to agents that can play (within valid play time slots).
    """

    STOP_TIMES = ["08:55 AM", "11:55 AM", "02:55 PM", "05:55 PM", "08:55 PM"]
    START_TIMES = ["09:00 AM", "12:00 PM", "03:00 PM", "06:00 PM", "09:00 PM"]

    def has_permission(self, request, view):
        timezone = pytz.timezone(settings.TIME_ZONE)
        current_time = datetime.now(tz=timezone)
        current_time_str = current_time.strftime("%I:%M %p")

        if self.is_draw_closed(current_time_str):
            msg = _("Draw is closed. You cannot play at this time.")
            raise PermissionDenied({"message": msg})

        return True

    def is_draw_closed(self, current_time_str):
        """
        Check if the current time falls within the closed periods.
        """
        timezone = pytz.timezone(settings.TIME_ZONE)
        today = datetime.now(tz=timezone).date()
        current_time = datetime.strptime(current_time_str, "%I:%M %p").replace(
            year=today.year, month=today.month, day=today.day
        )

        for stop, start in zip(self.STOP_TIMES, self.START_TIMES):
            stop_time = datetime.strptime(stop, "%I:%M %p").replace(year=today.year, month=today.month, day=today.day)
            start_time = datetime.strptime(start, "%I:%M %p").replace(
                year=today.year, month=today.month, day=today.day
            )

            if stop_time <= current_time < start_time:
                return True

        return False


k_30_draw_time = {
    "draw_time_interval": "30 minutes",
    "first_draw": "8:15 AM",
    "last_draw": "9:45 PM",
}

from datetime import datetime, timedelta

import pytz
from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied

k_30_draw_time = {
    "draw_time_interval": "30 minutes",
    "first_draw": "8:15 AM",
    "last_draw": "9:45 PM",
}


class Kenya30LottoDrawPermission(BaseAuthentication):
    """
    Allows access only to agents that can play (within valid play time slots).
    Blocks play 1 minute before each draw.
    """

    def __init__(self):
        # Generate all draw times based on the k_30_draw_time settings
        self.draw_times = self._calculate_draw_times()

    def _calculate_draw_times(self):
        """Calculate all draw times based on the first draw and interval"""
        draw_times = []
        timezone = pytz.timezone(settings.TIME_ZONE)
        today = datetime.now(tz=timezone).date()

        # Parse first and last draw time
        first_draw = datetime.strptime(k_30_draw_time["first_draw"], "%I:%M %p").replace(
            year=today.year, month=today.month, day=today.day
        )
        # Make first_draw timezone aware
        first_draw = timezone.localize(first_draw)

        last_draw = datetime.strptime(k_30_draw_time["last_draw"], "%I:%M %p").replace(
            year=today.year, month=today.month, day=today.day
        )
        # Make last_draw timezone aware
        last_draw = timezone.localize(last_draw)

        # Parse interval
        interval_parts = k_30_draw_time["draw_time_interval"].split()
        interval_minutes = int(interval_parts[0])

        # Generate all draw times
        current_draw = first_draw
        print("current_draw", current_draw)
        print("last_draw", last_draw)

        while current_draw <= last_draw:
            draw_times.append(current_draw)
            current_draw += timedelta(minutes=interval_minutes)

        return draw_times

    def has_permission(self, request, view):
        timezone = pytz.timezone(settings.TIME_ZONE)
        current_time = datetime.now(tz=timezone)
        current_time_str = current_time.strftime("%I:%M %p")

        if self.is_draw_closed(current_time):
            msg = _("Draw is closed. You cannot play at this time.")
            raise PermissionDenied({"message": msg})
        return True

    def is_draw_closed(self, current_time):
        """
        Check if the current time is within 1 minute of any draw time.
        """
        timezone = pytz.timezone(settings.TIME_ZONE)

        # print("draw_times", self.draw_times)

        # Check if we're within 1 minute before any draw
        for draw_time in self.draw_times:
            # Make sure draw_time is timezone aware
            if draw_time.tzinfo is None:
                draw_time = timezone.localize(draw_time)

            # Calculate 1 minute before the draw
            closed_period_start = draw_time - timedelta(minutes=1)

            # print("closed_period_start", closed_period_start)
            # print("draw_time", draw_time)
            # print("current_time", current_time)

            # If current time is between closed_period_start and draw_time
            if closed_period_start <= current_time < draw_time:
                return True

        return False


k_5_draw_time = {
    "draw_time_interval": "5 minutes",
    "first_draw": "8:05 AM",
    "last_draw": "9:55 PM",
}


class KNowLottoDrawPermission(BaseAuthentication):
    """
    Blocks play 1 minute before each 5-minute draw.
    """

    def __init__(self):
        # Generate all draw times based on the k_5_draw_time settings
        self.draw_times = self._calculate_draw_times()

    def _calculate_draw_times(self):
        """Calculate all draw times based on the first draw and interval"""
        draw_times = []
        timezone = pytz.timezone(settings.TIME_ZONE)
        today = datetime.now(tz=timezone).date()

        # Parse first and last draw time
        first_draw = datetime.strptime(k_5_draw_time["first_draw"], "%I:%M %p").replace(
            year=today.year, month=today.month, day=today.day
        )
        # Make first_draw timezone aware
        first_draw = timezone.localize(first_draw)

        last_draw = datetime.strptime(k_5_draw_time["last_draw"], "%I:%M %p").replace(
            year=today.year, month=today.month, day=today.day
        )
        # Make last_draw timezone aware
        last_draw = timezone.localize(last_draw)

        # Parse interval
        interval_parts = k_5_draw_time["draw_time_interval"].split()
        interval_minutes = int(interval_parts[0])

        # Generate all draw times
        current_draw = first_draw
        while current_draw <= last_draw:
            draw_times.append(current_draw)
            current_draw += timedelta(minutes=interval_minutes)

        return draw_times

    def has_permission(self, request, view):
        timezone = pytz.timezone(settings.TIME_ZONE)
        current_time = datetime.now(tz=timezone)

        if self.is_draw_closed(current_time):
            msg = _("Draw is closed. You cannot play at this time.")
            raise PermissionDenied({"message": msg})
        return True

    def is_draw_closed(self, current_time):
        """
        Check if the current time is within 1 minute of any draw time.
        """
        timezone = pytz.timezone(settings.TIME_ZONE)

        # Check if we're within 1 minute before any draw
        for draw_time in self.draw_times:
            # Make sure draw_time is timezone aware
            if draw_time.tzinfo is None:
                draw_time = timezone.localize(draw_time)

            # Calculate 1 minute before the draw
            closed_period_start = draw_time - timedelta(minutes=1)

            # If current time is between closed_period_start and draw_time
            if closed_period_start <= current_time < draw_time:
                return True

        return False


class IsGhanaGameActivePermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        if AfricaLottoGameType.GHANA_LOTTO in AfricaLottoConstants.active_africa_lotto_games():
            return True
        else:
            msg = _("Ghana Lotto is not active at the moment.")

            raise exceptions.AuthenticationFailed(msg)


class IsKenyaGameActivePermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        if AfricaLottoGameType.KENYA_LOTTO in AfricaLottoConstants.active_africa_lotto_games():
            return True
        else:
            msg = _("Kenya Lotto is not active at the moment.")

            raise exceptions.AuthenticationFailed(msg)


class IsKenya30GameActivePermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        if AfricaLottoGameType.KENYA_30_LOTTO in AfricaLottoConstants.active_africa_lotto_games():
            return True
        else:
            msg = _("Kenya 30 Lotto is not active at the moment.")

            raise exceptions.AuthenticationFailed(msg)


class IsKNowGameActivePermission(BaseAuthentication):
    """
    Allows access only to agent that does not have due remittance.
    """

    def has_permission(self, request, view):
        if AfricaLottoGameType.KENYA_30_LOTTO in AfricaLottoConstants.active_africa_lotto_games():
            return True
        else:
            msg = _("K Now Lotto is not active at the moment.")

            raise exceptions.AuthenticationFailed(msg)
