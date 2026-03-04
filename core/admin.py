from django.contrib import admin
from domestic.models import IshemaLinkUserAccountModel, Shipment, PaymentRecord

admin.site.register(IshemaLinkUserAccountModel)
admin.site.register(Shipment)
admin.site.register(PaymentRecord)