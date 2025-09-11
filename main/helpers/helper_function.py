import secrets
import string
import urllib
from datetime import datetime, timedelta

import pytz
import requests
from django.conf import settings
from django.db.models import Sum

from main.ussd.helpers import Utility
from overide_print import print


def currency_formatter(amount):
    return "{:,.2f}".format(amount)


def big_digit_currency_formatter(amount):
    if amount >= 1000000:
        return str(int(round(amount / 1000000, 2))) + "m"
    elif amount >= 1000:
        return (str(float(int(round(amount / 1000, 2)))).split("."))[0] + "k"
    else:
        return str(float(amount)).split(".")[0]


def match_masked_phone_number(masked_phone_number):
    first_covered = masked_phone_number[0:8]
    second_covered = masked_phone_number[-2:]

    return {"phone_start": first_covered, "phone_end": second_covered}


def mask_winners_phone_number(phone_number):
    formatted_num = "234" + phone_number[-10:]

    first_covered = formatted_num[0:5]
    second_covered = formatted_num[-3:]
    total_covered = first_covered + "*****" + second_covered
    return total_covered


def generate_bitly_link(link):
    url = "https://api-ssl.bitly.com/v4/bitlinks"

    payload = {"long_url": link}

    headers = {
        "Authorization": f"Bearer {settings.BITLY_TOKEN}",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, json=payload)

    res = response.json()
    print("bitly response", res, "\n\n\n\n\n\n")

    if res.get("link", None) is not None:
        return res.get("link")
    else:
        return None


def generate_cuttly_link(url):
    key = settings.CUTTLY_API_KEY
    url = urllib.parse.quote(url)
    name = "wyse-checkout"
    r = requests.get("http://cutt.ly/api/api.php?key={}&short={}&name={}".format(key, url, name))
    print(r.text)
    return r.json()


def fetch_account_name(account_number, bank_code):
    """ "
    This function calls another function that triggers a provider to fetch accunt name
    """

    url = f"https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}"

    headers = {"Authorization": f"Bearer {settings.PAYSTACK_BEARER}"}

    response = requests.request("GET", url=url, headers=headers)
    try:
        res = response.json()
    except Exception:
        res = response.text

    return res


def unpack_raw_winners_data(
    jackpot_raw_data,
    ordinary_raw_data,
    pool,
    stake_amount,
    total_jackpot_amount,
    batch,
    share,
    run_batch_id,
):
    from main.models import LotteryWinnersTable

    if jackpot_raw_data:
        for i in jackpot_raw_data:
            earning = i["earning"]
            player_id = i["id"]
            phone_number = i["phone"]
            unique_id = i["unique_id"]
            channel = i["channel"]
            i["lottery_type"]

            LotteryWinnersTable.create_winner_object(
                pool=pool,
                earning=earning,
                phone=phone_number,
                player_id=player_id,
                unique_id=unique_id,
                total_jackpot_amount=total_jackpot_amount,
                share=share,
                batch=batch,
                stake_amount=stake_amount,
                win_type="JACKPOT_WINNER",
                run_batch_id=run_batch_id,
                channel=channel,
            )

    if ordinary_raw_data:
        for i in ordinary_raw_data:
            earning = i["earning"]
            player_id = i["id"]
            phone_number = i["phone"]
            unique_id = i["unique_id"]
            channel = i["channel"]
            i["lottery_type"]

            LotteryWinnersTable.create_winner_object(
                pool=pool,
                earning=earning,
                phone=phone_number,
                player_id=player_id,
                unique_id=unique_id,
                total_jackpot_amount=total_jackpot_amount,
                share=share,
                batch=batch,
                stake_amount=stake_amount,
                win_type="ORDINARY_WINNER",
                run_batch_id=run_batch_id,
                channel=channel,
            )


def notify_whatsapp_admin_complete_raffle(
    batch,
    total_revenue,
    total_jackpots_10,
    total_jackpots_50,
    total_jackpots_250,
    total_jackpots_500,
    total_jackpots_1000,
):
    total_amount_won = list(batch.batch_disbursable_payouts.aggregate(Sum("payout_amount")).values())[0]
    batch.total_amount_won = total_amount_won
    batch.save()

    whatsapp_url = "https://pickyassist.com/app/api/v2/push"

    whatsapp_payload = {
        "token": f"{settings.PICKY_ASSIST_TOKEN}",
        "group_id": "120363043759006323",
        "application": "10",
        "mention_numbers": [
            "2348077469471",
            "2348031346306",
            "2347039115243",
            "2347039516293",
        ],
        "globalmessage": f"@2348077469471, @2348031346306, @2347039115243, @2347039516293, Dear Admins, \
            \nRaffle with batch {batch.batch_uuid} has completed. \n\nTotal Amount Won is capped at *{total_amount_won}*. \
            \nTotal Revenue: *{total_revenue}* \nTotal Jackpots_10: *{total_jackpots_10}*. \
            \nTotal Jackpots_50: *{total_jackpots_50} \nTotal Jackpots_250: *{total_jackpots_250}* \
            \nTotal Jackpots_500: *{total_jackpots_500}* \nTotal Jackpots_1000: *{total_jackpots_1000}*. \nThanks.",
    }

    whatsapp_Headers = {"Content-type": "application/json"}

    requests.post(whatsapp_url, json=whatsapp_payload, headers=whatsapp_Headers)

    return f"Whatsapp Message sent to admin on raffle closse out of batch id {batch.batch_uuid}"


def send_out_winners_result_data(received_winners_data, batch, run_batch_id):
    pass

    data_list = received_winners_data

    batch.batch_uuid

    total_revenue = None
    total_revenue = None
    total_jackpots_10 = None
    total_jackpots_50 = None
    total_jackpots_250 = None
    total_jackpots_500 = None
    total_jackpots_1000 = None

    for i in data_list:
        print(data_list)
        if i == 10:
            jackpot_raw_data = data_list[i]["jackpot_winners"]

            ordinary_raw_data = data_list[i]["ordinary_winners"]
            total_jackpot_amount = data_list[i]["total_jackpot_amount"]

            # unpacked_jackpot_data = unpack_raw_winners_data(
            #     jackpot_raw_data=jackpot_raw_data,
            #     ordinary_raw_data=ordinary_raw_data,
            #     pool="TEN_THOUSAND",
            #     stake_amount=100,
            #     total_jackpot_amount=total_jackpot_amount,
            #     batch=batch,
            #     share=i * 1000,
            #     run_batch_id=run_batch_id,
            # )

            total_jackpots_10 = total_jackpot_amount

        elif i == 50:
            jackpot_raw_data = data_list[i]["jackpot_winners"]
            ordinary_raw_data = data_list[i]["ordinary_winners"]
            total_jackpot_amount = data_list[i]["total_jackpot_amount"]

            unpack_raw_winners_data(
                jackpot_raw_data=jackpot_raw_data,
                ordinary_raw_data=ordinary_raw_data,
                pool="FIFTY_THOUSAND",
                stake_amount=200,
                total_jackpot_amount=total_jackpot_amount,
                batch=batch,
                share=i * 1000,
                run_batch_id=run_batch_id,
            )

            total_jackpots_50 = total_jackpot_amount

        elif i == 250:
            jackpot_raw_data = data_list[i]["jackpot_winners"]
            ordinary_raw_data = data_list[i]["ordinary_winners"]
            total_jackpot_amount = data_list[i]["total_jackpot_amount"]

            unpack_raw_winners_data(
                jackpot_raw_data=jackpot_raw_data,
                ordinary_raw_data=ordinary_raw_data,
                pool="TWO_FIFTY_THOUSAND",
                stake_amount=500,
                total_jackpot_amount=total_jackpot_amount,
                batch=batch,
                share=i * 1000,
                run_batch_id=run_batch_id,
            )

            total_jackpots_250 = total_jackpot_amount

        elif i == 500:
            jackpot_raw_data = data_list[i]["jackpot_winners"]
            ordinary_raw_data = data_list[i]["ordinary_winners"]
            total_jackpot_amount = data_list[i]["total_jackpot_amount"]

            unpack_raw_winners_data(
                jackpot_raw_data=jackpot_raw_data,
                ordinary_raw_data=ordinary_raw_data,
                pool="FIVE_HUNDRED_THOUSAND",
                stake_amount=1000,
                total_jackpot_amount=total_jackpot_amount,
                batch=batch,
                share=i * 1000,
                run_batch_id=run_batch_id,
            )

            total_jackpots_500 = total_jackpot_amount

        elif i == 1000:
            jackpot_raw_data = data_list[i]["jackpot_winners"]
            ordinary_raw_data = data_list[i]["ordinary_winners"]
            total_jackpot_amount = data_list[i]["total_jackpot_amount"]

            # unpacked_jackpot_data = unpack_raw_winners_data(
            #     jackpot_raw_data=jackpot_raw_data,
            #     ordinary_raw_data=ordinary_raw_data,
            #     pool="ONE_MILLION",
            #     stake_amount=2000,
            #     total_jackpot_amount=total_jackpot_amount,
            #     batch=batch,
            #     share=i * 1000,
            #     run_batch_id=run_batch_id,
            # )

            total_jackpots_1000 = total_jackpot_amount

        elif i == "totals":
            batch.RTO = data_list[i]["RTO"]
            batch.RTP = data_list[i]["RTP"]
            batch.super_winers = data_list[i]["super_winners"]
            batch.RTP = data_list[i]["RTP"]
            batch.total_revenue = data_list[i]["total_revenue"]
            batch.save()

            total_revenue = data_list[i]["total_revenue"]

    notify_whatsapp_admin_complete_raffle(
        batch,
        total_revenue,
        total_jackpots_10,
        total_jackpots_50,
        total_jackpots_250,
        total_jackpots_500,
        total_jackpots_1000,
    )

    # get_all_winners_number = LotteryWinnersTable.objects.filter(batch=batch).values_list('phone_number', flat=True)

    # get_non_winners_number = batch.lottery_players.filter(~Q(phone__in=get_all_winners_number)).distinct("phone")

    # for number in get_non_winners_number:
    #     send_list = notfy_non_winners_on_raffle_end(phone_number=number)


def trigger_whatsapp_admin_on_player_payment(
    phone_number,
    batch_id,
    amount,
    paid_via,
    total_amount_paid_for_batch,
    total_amount_paid_for_batch_today,
):
    from main.models import LotteryBatch, LotteryModel, LottoTicket
    from wyse_ussd.models import UssdLotteryPayment

    whatsapp_url = "https://pickyassist.com/app/api/v2/push"

    ussd_pending_payment = UssdLotteryPayment.objects.filter(user__phone_number=phone_number, game_play_id__isnull=False).last()

    # get total amount paid for lottery model
    lottery_model_queryset = LotteryModel.objects.filter(paid=True, batch__is_active=True)

    if lottery_model_queryset.exists():
        lottery_model_instance = lottery_model_queryset.last()

        total_amount_paid_for_lottery_model = lottery_model_queryset.aggregate(Sum("amount_paid"))["amount_paid__sum"]

        total_amount_not_paid_for_lottery_model = LotteryModel.objects.filter(paid=False, batch__is_active=True).aggregate(Sum("expected_amount"))[
            "expected_amount__sum"
        ]

        LotteryBatch.objects.filter(id=lottery_model_instance.batch.id).update(
            total_accumulated_paid=total_amount_paid_for_lottery_model,
            total_accumulated_unpaid=total_amount_not_paid_for_lottery_model,
        )

    else:
        total_amount_paid_for_lottery_model = 0
        total_amount_not_paid_for_lottery_model = 0

    # get total amount paid for salary for life
    salary_for_life_queryset = LottoTicket.objects.filter(paid=True, batch__is_active=True, lottery_type="SALARY_FOR_LIFE")

    if salary_for_life_queryset.exists():
        lottery_model_instance = salary_for_life_queryset.last()

        total_amount_paid_for_salary_for_life = salary_for_life_queryset.aggregate(Sum("amount_paid"))["amount_paid__sum"]
        total_amount_not_paid_for_salary_for_life = LottoTicket.objects.filter(
            paid=False, batch__is_active=True, lottery_type="SALARY_FOR_LIFE"
        ).aggregate(Sum("expected_amount"))["expected_amount__sum"]

        LotteryBatch.objects.filter(id=lottery_model_instance.batch.id).update(
            total_accumulated_paid=total_amount_paid_for_salary_for_life,
            total_accumulated_unpaid=total_amount_not_paid_for_salary_for_life,
        )

    else:
        total_amount_paid_for_salary_for_life = 0
        total_amount_not_paid_for_salary_for_life = 0
        total_amount_paid_for_lottery_model = 0

    # get total amount paid for instant cashout
    instant_cashout_queryset = LottoTicket.objects.filter(paid=True, batch__is_active=True, lottery_type="INSTANT_CASHOUT")

    if instant_cashout_queryset.exists():
        lottery_model_instance = instant_cashout_queryset.last()

        if lottery_model_instance is None:
            total_amount_paid_for_instant_cashout = 0
            total_amount_not_paid_for_instant_cashout = 0
            total_amount_paid_for_lottery_model = 0

        else:
            if lottery_model_instance.batch is None:
                instant_cashout_batch = LotteryBatch.objects.filter(lottery_type="INSTANT_CASHOUT").last()
                lottery_model_instance.batch = instant_cashout_batch
                lottery_model_instance.save()

            total_amount_paid_for_instant_cashout = instant_cashout_queryset.aggregate(Sum("amount_paid"))["amount_paid__sum"]
            total_amount_not_paid_for_instant_cashout = LottoTicket.objects.filter(
                paid=False, batch__is_active=True, lottery_type="INSTANT_CASHOUT"
            ).aggregate(Sum("expected_amount"))["expected_amount__sum"]

            LotteryBatch.objects.filter(id=lottery_model_instance.batch.id).update(
                total_accumulated_paid=total_amount_paid_for_instant_cashout,
                total_accumulated_unpaid=total_amount_not_paid_for_instant_cashout,
            )

    else:
        total_amount_paid_for_instant_cashout = 0
        total_amount_not_paid_for_instant_cashout = 0
        total_amount_paid_for_lottery_model = 0

    # combine all the total amount paid for lottery model and salary for life
    if total_amount_paid_for_lottery_model is None:
        total_amount_paid_for_lottery_model = 0

    if total_amount_paid_for_salary_for_life is None:
        total_amount_paid_for_salary_for_life = 0

    if total_amount_paid_for_instant_cashout is None:
        total_amount_paid_for_instant_cashout = 0

    _total_contributions = total_amount_paid_for_lottery_model + total_amount_paid_for_salary_for_life + total_amount_paid_for_instant_cashout

    print("_total_contributions", _total_contributions, "\n\n\n\n")

    lottery_qs = LotteryModel.objects.filter(game_play_id=ussd_pending_payment.game_play_id).last()

    if lottery_qs is not None:
        batch = LotteryBatch.objects.filter(id=lottery_qs.batch.id).last()

    else:
        lotto_qs = LottoTicket.objects.filter(game_play_id=ussd_pending_payment.game_play_id).last()

        if lotto_qs is not None:
            batch = LotteryBatch.objects.filter(id=lotto_qs.batch.id).last()

        else:
            batch = LotteryBatch.objects.filter(batch_uuid=batch_id).last()

    print(" trigger_whatsapp_admin_on_player_payment batch_id", batch_id)
    print("trigger_whatsapp_admin_on_player_payment type of batch_id", type(batch_id))

    # get game type from batch

    if total_amount_paid_for_batch_today is None:
        total_amount_paid_for_batch_today = 0

    # get total amount paid for batch
    if batch.lottery_type == "WYSE_CASH":
        print("entered_wyse_cash")
        # aggregate total amount paid for batch
        amount_paid = total_amount_paid_for_lottery_model
        # total_amount_paid = LotteryModel.objects.filter(batch__id=batch.id, paid=True)

        print("out from wyse cash")

    else:
        print("entered other lottery")
        amount_paid = 0
        if batch.lottery_type == "SALARY_FOR_LIFE":
            amount_paid = total_amount_paid_for_salary_for_life
        else:
            amount_paid = total_amount_paid_for_instant_cashout

    whatsapp_payload = {
        "token": f"{settings.PICKY_ASSIST_TOKEN}",
        "group_id": "120363043759006323",
        "application": "10",
        "mention_numbers": [
            "2348077469471",
            "2348031346306",
            "2347039516293",
        ],
        "globalmessage": f"@2348077469471, @2348031346306, @2347039516293, Dear Admins, \n\nA player with phone_number {phone_number} has made payment of *{amount}* via {paid_via} for {(batch.lottery_type).replace('_', ' ')} game. Batch_id: {batch_id}. \n\nTotal amount paid for batch is *{Utility.currency_formatter(float(amount_paid))}* \nTotal Amount paid for batch today is *{(Utility.currency_formatter(float(total_amount_paid_for_batch_today)))}* \n Total amount paid for all active batches is {Utility.currency_formatter(_total_contributions)} \n\nThanks.",
    }

    whatsapp_Headers = {"Content-type": "application/json"}

    requests.post(whatsapp_url, json=whatsapp_payload, headers=whatsapp_Headers)

    return f"Whatsapp Message sent to admin on player payment to batch id {batch_id}"


def notify_admin_on_fund_balance_for_payout(total_amount_needed):
    whatsapp_url = "https://pickyassist.com/app/api/v2/push"

    whatsapp_payload = {
        "token": f"{settings.PICKY_ASSIST_TOKEN}",
        "group_id": "120363043759006323",
        "application": "10",
        "mention_numbers": [
            "2348077469471",
            "2348031346306",
            "2347039115243",
            "2347039516293",
        ],
        "globalmessage": f"@2348077469471, @2348031346306, @2347039115243, @2347039516293, Dear Admins, \
            \nA total amount of *{total_amount_needed}* is needed to send a payout. Please fund balance as soon as possible\nThanks.",
    }

    whatsapp_Headers = {"Content-type": "application/json"}

    requests.post(whatsapp_url, json=whatsapp_payload, headers=whatsapp_Headers)

    return "Whatsapp Message sent to admin to fund balance"


# @dataclass
# class StringMarch:


#     def make_type_consistent(s1, s2):
#         """If both objects aren't either both string or unicode instances force them to unicode"""
#         if isinstance(s1, str) and isinstance(s2, str):
#             return s1, s2

#         elif isinstance(s1, unicode) and isinstance(s2, unicode):
#             return s1, s2

#         else:
#             return unicode(s1), unicode(s2)


class ByteHelper:
    def convert_byte_to_string(byte_text):
        return str(byte_text).replace("b'", "").replace("'", "")

    def convert_string_to_byte(text_str):
        return bytes(text_str, "utf-8")


_iteration = {}


def wyse_link_shortener(long_url, func_iterate=6):
    _iteration.get(long_url)

    if func_iterate < 0:
        return long_url

    def wyse_url_secret_key():
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(6))

    # check if url endswith /
    if long_url.endswith("/"):
        print("contains /")
        long_url = long_url[:-1]

    wyse_url = "https://wyse.onrender.com/url"
    payload = {"target_url": long_url, "secret_key": wyse_url_secret_key()}
    headers = {
        "Content-type": "application/json",
        "accept": "application/json",
    }

    try:
        response = requests.post(url=wyse_url, json=payload, headers=headers, timeout=10)
    except requests.exceptions.ReadTimeout:
        return wyse_link_shortener(long_url, func_iterate - 1)

    if response.status_code != 200:
        return wyse_link_shortener(long_url, func_iterate - 1)

    print("level 4")
    print("wyse response", response.text)

    """
        Response data

        {
            "target_url": "https://interviewing.io/mocks",
            "secret_key": "stringeee",
            "is_active": true,
            "clicks": 0,
            "url": "https://wyse.onrender.com/I7BH9",
            "admin_url": "https://wyse.onrender.com/admin/stringeee"
        }
    """

    try:
        return response.json()["url"]
    except Exception:
        return None


def link_shortener(url):
    """This function shortens the url passed to it and returns the shortened url"""
    try:
        if url in _iteration:
            _iteration[url] += 1
        else:
            _iteration[url] = 1
        if _iteration[url] >= 10:
            return url

        bitly = generate_bitly_link(url)
        if bitly is not None:
            _iteration.clear()

            return bitly

        wyse_short_link = wyse_link_shortener(url)
        if wyse_short_link is not None:
            return wyse_short_link

        return url

    except Exception as e:
        print(e)
        return url


def bold_text(text):
    """
    This function bolds the text passed to it
    """

    bold_start = "\033[1m"
    bold_end = "\033[0m"
    return bold_start + text + bold_end


def get_last_month(return_full_date=False):
    current_date = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    first_day_of_current_month = current_date.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)
    year_of_last_month = last_day_of_last_month.year
    month_of_last_month = last_day_of_last_month.month
    if return_full_date is False:
        return year_of_last_month, month_of_last_month
    else:
        return last_day_of_last_month
