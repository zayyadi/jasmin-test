from django.db import models


# from django.utils.translation import gettext as _


class Settings(models.Model):
    cid = models.CharField(
        max_length=40,
    )
    url = models.URLField(
        max_length=200,
    )
    email_list = models.TextField()

    def get_emails(self):
        return self.email_list.split(",")

    def set_emails(self, emails):
        self.email_list = ",".join(emails)


class UserModel(models.Model):
    uid = models.CharField(
        max_length=40,
    )
    url = models.URLField(
        max_length=200,
    )
    designated_bound = models.IntegerField(default=0)
    email_list = models.TextField()

    def get_emails(self):
        return self.email_list.split(",")

    def set_emails(self, emails):
        self.email_list = ",".join(emails)
