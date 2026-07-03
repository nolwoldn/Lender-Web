from django.contrib import admin
from .models import Error_reporting, Users, Item
# Register your models here.


class ErrorAdmin(admin.ModelAdmin):
    list_display = ("id", "report", "reporting_usr")


class UsrAdmin(admin.ModelAdmin):
    list_display = ("id", "Name")


class ItmAdmin(admin.ModelAdmin):
    list_display = ("id", "Item_name")


admin.site.register(Error_reporting, ErrorAdmin)
admin.site.register(Users, UsrAdmin)
admin.site.register(Item, ItmAdmin)
