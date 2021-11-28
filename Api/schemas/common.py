from marshmallow import Schema, fields


class GenericReturnSchema(Schema):
    message = fields.String(required=True, description="The message about return")
