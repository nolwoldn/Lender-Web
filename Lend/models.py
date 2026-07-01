from django.db import models

# Create your models here.


class Users(models.Model):
    Name = models.CharField(max_length=255)
    Lended_items_id = models.JSONField(default=list, null=True)
    Borrowed_items_id = models.JSONField(default=list, null=True)
    Password = models.CharField(max_length=255, null=True)


class Item(models.Model):
    Item_name = models.CharField(max_length=255)
    Item_desc = models.CharField(max_length=1200)
    Item_borrowed_state = models.BooleanField(default=False)
    


class Borrow_request(models.Model):
    Borrowing_user_id = models.IntegerField()
    user_Borrowing_from_id = models.IntegerField(null=True)
    Borrowing_item_id = models.IntegerField()
    Borrow_acceptance = models.BooleanField(null=True, default=False)


class Error_reporting(models.Model):
    reporting_usr = models.IntegerField()
    report = models.CharField(max_length=255)
