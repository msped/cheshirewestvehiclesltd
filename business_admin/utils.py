from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf.pisa import pisaDocument

from .models import Customer, InvoiceItem


def get_customer(customer_data):
    queryset = Customer.objects
    if isinstance(customer_data, dict):
        customer = queryset.create(**customer_data)
    else:
        customer = queryset.get(customer_id=customer_data)
    return customer.id


def render_to_pdf(template, data=None):
    template = render_to_string("invoice_template.html", data).encode("utf-8")
    result = BytesIO()
    pdf = pisaDocument(src=BytesIO(template), dest=result, encoding="utf-8")
    if pdf.err:
        return None
    return HttpResponse(result.getvalue(), content_type="application/pdf")


def invoice_handler(data, extra_emails=None):
    pdf = render_to_pdf(
        "invoice_template.html",
        {'data': data}
    )
    if pdf:
        recipients = [data["customer"]["email"]]
        if extra_emails:
            recipients.append(extra_emails)
        message = "Hello,\n\nPlease see attached invoice for services by Cheshire West Vehicles.\
            \n\nMany Thanks,\n\nCheshireWestVehicles"
        email = EmailMessage(
            "Invoice for Services | Cheshire West Vehicles",
            message, "info@cheshirewestvehicles.co.uk",
            to=recipients
        )
        email.attach("invoice.pdf", pdf.getvalue(), "application/pdf")
        email.send()
        return True
    return False


def create_invoice_items(invoice_id, invoice_items):
    item_objects = [
        InvoiceItem(
            invoice_id=invoice_id,
            **item,
            line_price=round(item['quantity'] *
                             item['unit_price'], 2)
        ) for item in invoice_items
    ]
    InvoiceItem.objects.bulk_create(item_objects)
