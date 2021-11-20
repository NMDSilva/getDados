import logging
from peewee import SqliteDatabase, Model, DateTimeField, CharField, ForeignKeyField, DecimalField
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv("../.env")

db = SqliteDatabase(os.environ.get("BD_NAME"))

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class BaseModel(Model):
  created_at = DateTimeField(default = datetime.now)
  updated_at = DateTimeField(default = datetime.now)

  class Meta:
    database = db

class Unidade(BaseModel):
  nome = CharField(unique = True)
  descricao = CharField(null = True)

class Categoria(BaseModel):
  nome = CharField(unique = True)

class Produto(BaseModel):
  slug = CharField(unique = True, index = True)
  # titulo = CharField()
  descricao = CharField()
  img = CharField(null = True)
  # sku = CharField(null = True)
  categoria = ForeignKeyField(Categoria, backref = "produto")
  
class Preco(BaseModel):
  produto = ForeignKeyField(Produto, backref = "preco")
  precoUnitario = DecimalField(decimal_places = 2)
  preco = DecimalField(decimal_places = 2)
  unidade = ForeignKeyField(Unidade, backref = "unidade")


class bd_inicializar():
  db.connect()
  db.create_tables([
    Categoria,
    Produto,
    Preco,
    Unidade
  ])