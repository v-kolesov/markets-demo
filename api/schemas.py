from marshmallow.validate import Length
from marshmallow import Schema, fields


class UserLogin(Schema):
    username = fields.String(required=True, validate=[Length(min=6)])
    password = fields.String(required=True, validate=[Length(min=6)])
