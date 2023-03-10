from marshmallow import Schema, fields

class ItemSchema(Schema): # POST
    id = fields.Str(dump_only=True) # we never accept from outside, was generate from our code
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    store_id = fields.Str(required=True)

class ItemUpdateSchema(Schema): # PUT
    name = fields.Str()
    price = fields.Float()

class StoreSchema(Schema): # POST
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
