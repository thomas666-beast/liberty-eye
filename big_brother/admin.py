from django.contrib import admin
from .models import Participant, Phone, Email, HistoricalRecord


class PhoneInline(admin.TabularInline):
    model = Phone
    extra = 1


class EmailInline(admin.TabularInline):
    model = Email
    extra = 1


class HistoricalRecordInline(admin.TabularInline):
    model = HistoricalRecord
    extra = 0
    readonly_fields = ['changed_at']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['username', 'nickname', 'get_full_name', 'status', 'role']
    list_filter = ['status', 'role']
    search_fields = ['username', 'nickname', 'first_name', 'last_name']
    inlines = [PhoneInline, EmailInline, HistoricalRecordInline]
    # exclude = ['password']  # Don't show password in admin

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = 'Full Name'


@admin.register(HistoricalRecord)
class HistoricalRecordAdmin(admin.ModelAdmin):
    list_display = ['participant', 'record_type', 'changed_at']
    list_filter = ['record_type', 'changed_at']
    search_fields = ['participant__username', 'value']
