import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import ReservationAmount


def get_reservation_amount():
    try:
        return ReservationAmount.objects.get(active=True).amount
    except ReservationAmount.DoesNotExist:
        return 10000


def send_reservation_email(reservation, res_amount, tradein=None):
    template = render_to_string(
        'reservation_email.html',
        {
            'tradein': tradein,
            'reservation': reservation,
            'res_amount': res_amount,
        }
    )
    send_mail(
        subject='Vehicle reservation confirmation - Cheshire West Vehicles',
        message=strip_tags(template),
        recipient_list=[reservation.email],
        from_email=os.environ.get('ADMIN_EMAIL'),
        html_message=template
    )


def send_new_reservation_email(vehicle):
    send_mail(
        subject=f'{vehicle} has been reserved.',
        message='''Hello \n\n The above vehicle has been reserved. \n
        \n Please log in to view the details and arrange a viewing. \n
        \n Thanks, \n Cheshire West Vehicles''',
        recipient_list=[os.environ.get('ADMIN_EMAIL')],
        from_email=os.environ.get('ADMIN_EMAIL'),
    )
