# https://compraremcasa.pt/mercearia/name/asc?page=1
import urllib.request 
from bs4 import BeautifulSoup
import json

class GetDados():
    def __init__(self) -> None:
        self.url = "https://compraremcasa.pt/"
        self.filtro = "/name/asc?page="
        self.info = {
            "categorias": [],
            "produtos": []
        }
        self.total_produtos = 0

    def carregar_categorias(self):
        pagina = urllib.request.urlopen(self.url).read()
        html = BeautifulSoup(pagina, "html.parser")
        nav = html.find("ul", class_="navbar-nav")
        items = nav.findChildren("li", recursive = False)
        for item in items:
            a = item.find("a", href=True, recursive=False)
            try:
                if not a["href"].find(self.url):
                    self.info["categorias"].append(a["href"].replace(self.url, ""))
            except:
                pass

    def get_info_produto(self, linkProduto, categoria):
        pagina = urllib.request.urlopen(self.url + linkProduto).read()
        html = BeautifulSoup(pagina, "html.parser")
        if html.find("span", class_="form-price") != None:
            titulo = html.find("div", class_="brand").text.strip()
            descricao = html.find("div", class_="form-group").find("h1").text.strip()
            preco = html.find("span", class_="form-price").text.strip()
            block = html.find("span", class_="product-block-list").text.strip()
            # img = html.find("img", class_="img-fluid")["src"]
            produto = {
                "slug": linkProduto[1:],
                "titulo": titulo,
                "descricao": descricao,
                "preco": preco,
                "block": block,
                "categoria": categoria
            }
            self.registar_produto(produto)
            self.total_produtos += 1
            print(str(self.total_produtos) + " - " + produto["slug"] + " - " + produto["titulo"])
    
    def carregar_produtos(self, categoria, page = 1):
        pagina = urllib.request.urlopen(self.url + categoria + self.filtro + str(page)).read()
        html = BeautifulSoup(pagina, "html.parser")
        produtos = html.find_all("div", class_="product-block")
        if len(produtos) > 0:
            for produto in produtos:
                link = produto.find("a", class_="product-image")["href"]
                self.get_info_produto(link, categoria)
            self.carregar_produtos(categoria, page + 1)

    # def criar_json(self):
    #     with open('info.json', 'w', encoding='utf-8') as f:
    #         json.dump(self.info, f, ensure_ascii=False, indent=2)
    
    def registar_categorias(self):
        with open("info.json", "w", encoding='utf-8') as jsonFile:
            json.dump(self.info, jsonFile, ensure_ascii=False, indent=2)
    
    def registar_produto(self, produto):
        with open("info.json", "r", encoding='utf-8') as jsonFile:
            obj = json.load(jsonFile)

        obj["produtos"].append(produto)

        with open("info.json", "w", encoding='utf-8') as jsonFile:
            json.dump(obj, jsonFile, ensure_ascii=False, indent=2)

    def iniciar(self):
        self.carregar_categorias()
        self.registar_categorias()
        for categoria in self.info["categorias"]:
            self.carregar_produtos(categoria)
        self.criar_json()

obj = GetDados()
obj.iniciar()

