from django.contrib import admin

from library.models import Books, Reviews

# Register your models here.
admin.site.register(Books)
admin.site.register(Reviews)