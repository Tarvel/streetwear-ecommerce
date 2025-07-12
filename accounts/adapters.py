from allauth.account.adapter import DefaultAccountAdapter

class EmailAsUsernameAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        This method is called by Allauth to set the username field.
        We'll override it so username = email.
        """
        if user.email:
            user.username = user.email
        return user.username
