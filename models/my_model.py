from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.minimal.model'
    _description = 'My Minimal Model'

    name = fields.Char(string='Name')
