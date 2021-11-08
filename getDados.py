import urllib.request 
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
import os
import sqlite3

load_dotenv(".env")

class GetDados():
  def __init__(self) -> None:
    self.url = os.environ.get("SITE_CONSULTA")
    self.filtro = "/name/asc?page="
    self.conn = sqlite3.connect(os.environ.get("BD_NAME"), detect_types=sqlite3.PARSE_DECLTYPES)
    self.categorias = []

  def criar_tabelas(self):
    self.criar_tabela_categorias()
    self.criar_tabela_produtos()
    self.criar_tabela_precos()

  def criar_tabela_categorias(self):
    cur = self.conn.cursor()
    try:
      cur.execute("CREATE TABLE categorias (id_categoria integer PRIMARY KEY, categoria text, data_registo timestamp)")
    except:
      pass
    self.conn.commit()

  def criar_tabela_produtos(self):
    cur = self.conn.cursor()
    try:
      cur.execute("CREATE TABLE produtos (id_produto integer PRIMARY KEY, slug text, nome text, data_registo timestamp)")
    except:
      pass
    self.conn.commit()

  def criar_tabela_precos(self):
    cur = self.conn.cursor()
    try:
      cur.execute("CREATE TABLE precos (id_preco integer PRIMARY KEY, id_produto integer, preco real, data_registo timestamp)")
    except:
      pass
    self.conn.commit()
    
  def carregar_categorias(self):
    pagina = urllib.request.urlopen(self.url).read()
    html = BeautifulSoup(pagina, "html.parser")
    nav = html.find("ul", class_="navbar-nav")
    items = nav.findChildren("li", recursive=False)
    for item in items:
      a = item.find("a", href=True, recursive=False)
      try:
        if not a["href"].find(self.url):
          categoria_nome = a["href"].replace(self.url, "")
          id = self.registar_categorias(categoria_nome)
          self.categorias.append({
            "id_categoria": id,
            "categoria": categoria_nome
          })
      except:
        pass

  def registar_categorias(self, categoria):
    cur = self.conn.cursor()
    try:
      cur.execute("INSERT INTO categorias (categoria, data_registo) VALUES (?, ?)", (categoria, datetime.now()))
      self.conn.commit()
      return cur.lastrowid
    except:
      return 0

  # def get_info_produto(self, linkProduto, categoria):
  #   pagina = urllib.request.urlopen(self.url + linkProduto).read()
  #   html = BeautifulSoup(pagina, "html.parser")
  #   if html.find("span", class_="form-price") != None:
  #     titulo = html.find("div", class_="brand").text.strip()
  #     descricao = html.find("div", class_="form-group").find("h1").text.strip()
  #     preco = html.find("span", class_="form-price").text.strip()
  #     block = html.find("span", class_="product-block-list").text.strip()
  #     # img = html.find("img", class_="img-fluid")["src"]
  #     produto = {
  #       "slug": linkProduto[1:],
  #       "titulo": titulo,
  #       "descricao": descricao,
  #       "preco": preco,
  #       "block": block,
  #       "categoria": categoria
  #     }
  #     self.registar_produto(produto)
  #     self.total_produtos += 1
  #     print(str(self.total_produtos) + " - " + produto["slug"] + " - " + produto["titulo"])
  
  # def carregar_produtos(self, categoria, page = 1):
  #   pagina = urllib.request.urlopen(self.url + categoria + self.filtro + str(page)).read()
  #   html = BeautifulSoup(pagina, "html.parser")
  #   produtos = html.find_all("div", class_="product-block")
  #   if len(produtos) > 0:
  #     for produto in produtos:
  #       link = produto.find("a", class_="product-image")["href"]
  #       self.get_info_produto(link, categoria)
  #     self.carregar_produtos(categoria, page + 1)

  # def criar_json(self):
  #     with open('info.json', 'w', encoding='utf-8') as f:
  #         json.dump(self.info, f, ensure_ascii=False, indent=2)
  
  # def registar_produto(self, produto):
  #   with open("info.json", "r", encoding='utf-8') as jsonFile:
  #     obj = json.load(jsonFile)

  #   obj["produtos"].append(produto)

  #   with open("info.json", "w", encoding='utf-8') as jsonFile:
  #     json.dump(obj, jsonFile, ensure_ascii=False, indent=2)

  def iniciar(self):
    self.criar_tabelas()
    self.carregar_categorias()
    print(self.categorias)
    # self.registar_categorias()
    # for categoria in self.info["categorias"]:
    #   self.carregar_produtos(categoria)
    

obj = GetDados()
obj.iniciar()

