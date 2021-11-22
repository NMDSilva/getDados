import sys
import os

import urllib.request 
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db")))

from schema import bd_inicializar, Categoria, Produto, Unidade, Preco, Loja

load_dotenv("../.env")

class GetDados():
  def __init__(self) -> None:
    self.url = os.environ.get("SITE_CONSULTA_CC")
    self.filtro = "/name/asc?page="
    bd_inicializar()
    loja, create = Loja.get_or_create(
      link = self.url,
      defaults = { "nome": "Comprar em Casa" }
    )
    self.id_loja = loja.get_id()

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
            Categoria.create(
              nome = categoria_nome,
              loja_id = self.id_loja
            )
      except:
        pass
  
  def categoria_existe(self, categoria):
    return Categoria.select().where(Categoria.nome == categoria).exists()
  
  def carregar_produtos(self, categoria, page = 1):
    pagina = urllib.request.urlopen(self.url + categoria + self.filtro + str(page)).read()
    html = BeautifulSoup(pagina, "html.parser")
    produtos = html.find_all("div", class_ = "product-block")
    if len(produtos) > 0:
      for produto in produtos:
        if produto.find("form") != None:
          slug, descricao, precoUnitario, preco, img, unidade = self.get_info_produto(produto)
          if(self.novo_produto_ou_preco(slug)):
            self.registar_produto(slug, descricao, precoUnitario, preco, img, categoria, unidade)

      self.carregar_produtos(categoria, page + 1)

  def get_info_produto(self, produto):
    slug = produto.find("a", class_ = "product-image")["href"][1:]
    descricao = produto.find("h3").find("a").text.strip()
    blocoPrecos = produto.find("div", class_ = "list-price")
    precoUnitario = blocoPrecos.findChildren("span", class_ = "product-block-normal", recursive = False)
    if len(precoUnitario) > 0:
      precoUnitario = precoUnitario[0].text.replace("€", "").strip()
    else:
      precoUnitario = blocoPrecos.findChildren("span", class_ = "product-block-list", recursive = False)[0].text.replace("€", "").strip()
    block = blocoPrecos.findChildren("div", recursive = False)[0].find("span", class_ = "product-block-list").text.strip().split("/")
    preco = block[0].replace("€", "").strip()
    unidade = block[1].strip()
    try: img = produto.find("img")["src"]
    except: img = None
    return slug, descricao, precoUnitario, preco, img, unidade

  def registar_produto(self, slugProduto, descricao, precoUnitario, preco, img, categoria, unidade):
    id_categoria = Categoria.get(Categoria.nome == categoria).get_id()

    unidade, create = Unidade.get_or_create(
      nome = unidade,
      defaults = {
        "loja_id": self.id_loja
      }
    )

    produto, create = Produto.get_or_create(
      slug = slugProduto,
      defaults = {
        "descricao": descricao,
        "img": img,
        "categoria_id": id_categoria,
        "loja_id": self.id_loja
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

  def iniciar(self):
    self.carregar_categorias()
    categorias = Categoria.select()
    for categoria in categorias:
      self.carregar_produtos(categoria.nome)

obj = GetDados()
obj.iniciar()
