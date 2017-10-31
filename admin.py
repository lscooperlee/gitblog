from django.contrib import admin

from .models import Address
from .models import Visit


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
        pass


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
        pass
