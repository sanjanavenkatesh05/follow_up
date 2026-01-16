from django.contrib import admin
from .models import Clinic, UserProfile, FollowUp, PublicViewLog

# Register your models here.
# admin.site.register(Clinic) 
# admin.site.register(UserProfile)
# admin.site.register(FollowUp)
# admin.site.register(PublicViewLog)

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "clinic_code",
        "created_at",
    )

    search_fields = ("name", "clinic_code")

    readonly_fields = (
        "clinic_code",
        "created_at",
    )

    ordering = ("-created_at",)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "clinic",
    )

    search_fields = (
        "user__username",
        "user__email",
        "clinic__name",
    )

    list_select_related = ("user", "clinic")
@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient_name",
        "clinic",
        "status",
        "due_date",
        "view_count",
        "created_at",
    )

    list_filter = (
        "status",
        "clinic",
        "language",
    )

    search_fields = (
        "patient_name",
        "phone",
        "public_token",
    )

    readonly_fields = (
        "public_token",
        "created_at",
        "updated_at",
    )

    date_hierarchy = "due_date"

    ordering = ("due_date",)

    list_select_related = ("clinic", "created_by")

    def view_count(self, obj):
        return obj.view_logs.count()

    view_count.short_description = "Public Views"
@admin.register(PublicViewLog)
class PublicViewLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "followup",
        "viewed_at",
        "ip_address",
    )

    list_filter = ("viewed_at",)

    search_fields = (
        "followup__patient_name",
        "ip_address",
    )

    readonly_fields = (
        "followup",
        "viewed_at",
        "user_agent",
        "ip_address",
    )

    ordering = ("-viewed_at",)
