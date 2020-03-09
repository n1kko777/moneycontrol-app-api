from django.contrib import admin
from . import models

admin.site.register(models.Tag)
admin.site.register(models.Action)
admin.site.register(models.Category)
admin.site.register(models.Transfer)
admin.site.register(models.Profile)
admin.site.register(models.Account)
admin.site.register(models.Company)
admin.site.register(models.Transaction)
