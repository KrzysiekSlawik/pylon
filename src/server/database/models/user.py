from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    wins = fields.IntField(default=0)
    loses = fields.IntField(default=0)

    class Meta:
        ordering = ["username"]

user_pydantic = pydantic_model_creator(Users, name="user")