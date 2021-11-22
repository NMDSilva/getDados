import logging
from peewee import SqliteDatabase, Model, DateTimeField, CharField, ForeignKeyField, DecimalField, DatabaseProxy
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv("../.env")

db = DatabaseProxy()

# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

class BaseModel(Model):
  created_at = DateTimeField(default = datetime.now)
  updated_at = DateTimeField(default = datetime.now)

  class Meta:
    database = db

class Loja(BaseModel):
  nome = CharField(unique = True)
  link = CharField(unique = True)

class Unidade(BaseModel):
  nome = CharField(unique = True)
  descricao = CharField(null = True)
  loja = ForeignKeyField(Loja, backref = "loja")

class Categoria(BaseModel):
  nome = CharField(unique = True)
  loja = ForeignKeyField(Loja, backref = "loja")

class Produto(BaseModel):
  slug = CharField(unique = True, index = True)
  descricao = CharField()
  img = CharField(null = True)
  categoria = ForeignKeyField(Categoria, backref = "produto")
  loja = ForeignKeyField(Loja, backref = "loja")
  
class Preco(BaseModel):
  produto = ForeignKeyField(Produto, backref = "preco")
  precoUnitario = DecimalField(decimal_places = 2)
  preco = DecimalField(decimal_places = 2)
  unidade = ForeignKeyField(Unidade, backref = "unidade")

class bd_inicializar():
  db.initialize(SqliteDatabase(os.environ.get("BD_NAME")))
  db.connect()
  db.create_tables([
    Categoria,
    Produto,
    Preco,
    Unidade,
    Loja
  ])