from marshmallow import Schema, fields

class PlainItemSchema(Schema): # POST
    id = fields.Str(dump_only=True) # we never accept from outside, was generate from our code
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema): # POST
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)

class ItemUpdateSchema(Schema): # PUT
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()

class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)

class StoreSchema(PlainStoreSchema): # POST
    items = fields.List(fields.Nested(PlainItemSchema()),  dump_only=True)
