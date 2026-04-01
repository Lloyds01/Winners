

# Register your models here.
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from account.models import (
    BlackListed,
    Otp,
    ResetPasswordToken,
    TelcosPhoneNumber,
    # Token,
    User,
    UserProfileOtp,
)


# Register your models here.
class UserModelResource(resources.ModelResource):
    class Meta:
        model = User

class OtpModelResource(resources.ModelResource):
    class Meta:
        model = Otp

class BlackListedModelResource(resources.ModelResource):
    class Meta:
        model = BlackListed

class TelcosPhoneNumberResource(resources.ModelResource):
    class Meta:
        model = TelcosPhoneNumber

class ResetPasswordTokenModelResource(resources.ModelResource):
    class Meta:
        model = ResetPasswordToken

    
class UserModelAdmin(ImportExportModelAdmin):
    resource_class = UserModelResource

    list_filter = ("channel", "created_at", "is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "phone")
    ordering = ("-date_joined",)
    date_hierarchy = "created_at"

    def get_list_display(self, request):
        data = [field.name for field in self.model._meta.concrete_fields]
        data.remove("password")
        # data.append('phone')
        return data

class OtpModelAdmin(ImportExportModelAdmin):
    resource_class = OtpModelResource

    search_fields = ("user__phone", "user__email", "phone")
    ordering = ("-created_at", "user", "otp", "is_verified", "otp_type")

    def get_list_display(self, request):
        data = [field.name for field in self.model._meta.concrete_fields]
        return data

class BlackListedModelAdmin(ImportExportModelAdmin):
    resource_class = BlackListedModelResource

    # search_fields = ("user__phone", "user__email", "key")
    # ordering = ("-created_at", "user", "key")

    def get_list_display(self, request):
        data = [field.name for field in self.model._meta.concrete_fields]
        return data

class TelcosPhoneNumberModelAdmin(ImportExportModelAdmin):
    resource_class = TelcosPhoneNumberResource

    list_filter = (
        "network",
        "created_at",
        "state",
        "lga",
        "gender",
    )
    search_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "address",
    )
    date_hierarchy = "created_at"

    def get_list_display(self, request):
        data = [field.name for field in self.model._meta.concrete_fields]
        return data

class ResetPasswordTokenModelAdmin(ImportExportModelAdmin):
    resource_class = ResetPasswordTokenModelResource

    search_fields = ("user__phone", "user__email", "key")
    ordering = ("-created_at", "user", "key")

    def get_list_display(self, request):
        data = [field.name for field in self.model._meta.concrete_fields]
        return data

admin.site.register(User, UserModelAdmin)
admin.site.register(Otp, OtpModelAdmin)
admin.site.register(BlackListed, BlackListedModelAdmin)
admin.site.register(TelcosPhoneNumber, TelcosPhoneNumberModelAdmin)
admin.site.register(ResetPasswordToken, ResetPasswordTokenModelAdmin)
