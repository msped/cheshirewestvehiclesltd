from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf.pisa import pisaDocument

def get_parts(request):
    parts = {}

    for item in range(1, len(request)):
        if request.get("description-" + str(item)) is not None:
            row = {}
            row["description"] = request["description-" + str(item)]
            row['qty'] = request['qty-' + str(item)]
            row['unit'] = request['unit-' + str(item)]
            row['line'] = request['line-' + str(item)]
            parts[str(item)] = row
        else:
            break
    return parts

def create_data_structure(request):
    data = {

        "customer": {
            "name": request["name"],
            "phone_number": request["phone_number"],
            "email": request["email"],
            "address_line_1": request["address_line_1"],
            "address_line_2": request["address_line_2"],
            "town_city": request["town_city"],
            "county": request["county"],
            "postcode": request["postcode"]
        },
        "vehicle": {
            "make": request["make"],
            "model": request["model"],
            "year": request["year"],
            "mileage": request["mileage"],
            "vrm": request["vrm"]
        },
        "labour": {
            "qty": request["labour-qty"],
            "unit": request["labour-unit"],
            "total": request["labour-total"],
        },
        "total": request["invoice-total"],
        "comments": request["comments"],
    }
    data["parts"] = get_parts(request)

    return data

def render_to_pdf(template, data=None):
    template = render_to_string("invoice_template.html", data).encode("utf-8")
    result = BytesIO()
    pdf = pisaDocument(src=BytesIO(template), dest=result, encoding="utf-8")
    if pdf.err:
        return None
    return HttpResponse(result.getvalue(), content_type="application/pdf")

def invoice_handler(request):
    data = create_data_structure(request)
    pdf = render_to_pdf(
        "invoice_template.html",
        {'data': data}
    )
    if pdf:
        message = "Hello,\n\nPlease see attached invoice for services by Cheshire West Vehicles.\
            \n\nMany Thanks,\n\nCheshireWestVehicles"
        email = EmailMessage(
            "Invoice for Services | Cheshire West Vehicles",
            message, "info@cheshirewestvehicles.co.uk",
            [data["customer"]["email"]]
        )
        email.attach("invoice.pdf", pdf.getvalue(), "application/pdf")
        email.send()
        return data["customer"]["email"]
    return None
