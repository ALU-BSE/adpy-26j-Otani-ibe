from django.contrib import admin
# Change the import source from .models to domestic.models
from domestic.models import IshemaLinkUserAccountModel, Shipment, PaymentRecord

admin.site.register(IshemaLinkUserAccountModel)
admin.site.register(Shipment)
admin.site.register(PaymentRecord)