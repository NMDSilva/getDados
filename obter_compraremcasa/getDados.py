import urllib.request 
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from ..db.orm_bd import *
import datetime

load_dotenv("../.env")

class GetDados():
  def __init__(self) -> None:
    self.url = os.environ.get("SITE_CONSULTA")
    self.filtro = "/name/asc?page="
    bd_inicializar()

  def carregar_categorias(self):
    pagina = urllib.request.urlopen(self.url).read()
    html = BeautifulSoup(pagina, "html.parser")
    nav = html.find("ul", class_ = "navbar-nav")
    items = nav.findChildren("li", recursive = False)
    for item in items:
      a = item.find("a", href = True, recursive = False)
      try:
        if not a["href"].find(self.url):
          categoria_nome = a["href"].replace(self.url, "")
          if (not self.categoria_existe(categoria_nome)):
            Categoria.create(nome=categoria_nome)
      except:
        pass
  
  def categoria_existe(self, categoria):
    return Categoria.select().where(Categoria.nome == categoria).exists()

  def get_info_produto(self, slugProduto, categoria):
    pagina = urllib.request.urlopen(self.url + "/" + slugProduto).read()
    html = BeautifulSoup(pagina, "html.parser")
    if html.find("span", class_ = "form-price") != None:
      titulo = html.find("div", class_ = "brand").text.strip()
      descricao = html.find("div", class_ = "form-group").find("h1").text.strip()
      precoUnitario = html.find("span", class_ = "form-price").text.replace("€", "").strip()
      block = html.find("span", class_ = "product-block-list").text.strip().split("/")
      try: sku = html.find("span", class_ = "sku_elem").text.strip()
      except: sku = None
      preco = block[0].replace("€", "").strip()
      unidade = block[1].strip()
      try: img = html.find("img", class_="img-fluid")["src"]
      except: img = None
      self.registar_produto(slugProduto, titulo, descricao, precoUnitario, preco, img, categoria, unidade, sku)

  def registar_produto(self, slugProduto, titulo, descricao, precoUnitario, preco, img, categoria, unidade, sku):
    id_categoria = Categoria.get(Categoria.nome == categoria).get_id()

    unidade, create = Unidade.get_or_create(nome = unidade)

    produto, create = Produto.get_or_create(
      slug = slugProduto,
      defaults = {
        'titulo': titulo,
        'descricao': descricao,
        'img': img,
        'sku': sku,
        'categoria_id': id_categoria
      }
    )

    Preco.create(
      produto_id = produto.get_id(),
      precoUnitario = precoUnitario,
      preco = preco,
      unidade_id = unidade.get_id()
    )

  def novo_produto_ou_preco(self, slug):
    return not Produto.select().join(Preco).where(Produto.slug == slug & Preco.created_at >= (datetime.datetime.now() - datetime.timedelta(days=3))).exists()

  def carregar_produtos(self, categoria, page = 1):
    pagina = urllib.request.urlopen(self.url + categoria + self.filtro + str(page)).read()
    html = BeautifulSoup(pagina, "html.parser")
    produtos = html.find_all("div", class_ = "product-block")
    if len(produtos) > 0:
      for produto in produtos:
        slug = produto.find("a", class_ = "product-image")["href"][1:]
        if(self.novo_produto_ou_preco(slug)):
          self.get_info_produto(slug, categoria)
      self.carregar_produtos(categoria, page + 1)

  def iniciar(self):
    self.carregar_categorias()
    categorias = Categoria.select()
    for categoria in categorias:
      self.carregar_produtos(categoria.nome)

obj = GetDados()
obj.iniciar()

