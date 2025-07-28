from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class EmailAsUsernameAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        if user.email:
            user.username = user.email
        return user.username

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if sociallogin.account.provider == "google":
            user.email = sociallogin.account.extra_data.get("email", "")
            user.username = user.email
            user.save()
        return user
