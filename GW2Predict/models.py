from django.db import models


class AllItems(models.Model):
    name = models.TextField(null=True)
    type = models.TextField(null=True)
    level = models.IntegerField(null=True)
    rarity = models.TextField(null=True)
    vendor_value = models.IntegerField(null=True)
    default_skin = models.IntegerField(null=True)
    game_types = models.TextField(null=True)
    flags = models.TextField(null=True)
    restrictions = models.TextField(null=True)
    id = models.IntegerField(primary_key=True)
    chat_link = models.TextField(max_length=20, null=True)
    icon = models.TextField(max_length=100, null=True)
    details = models.TextField(null=True)
    description = models.TextField(max_length=200, null=True)
    upgrades_from = models.TextField(max_length=100, null=True)
    upgrades_into = models.TextField(max_length=100, null=True)
