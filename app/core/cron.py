#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from conf import config
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def poll():
    try:
        numero_rubrique, numeros_articles = findReferenceArticles()
        articles = findArticles(numero_rubrique, numeros_articles)
        logger.info(articles)
    except:
        logger.exception("polling exception")
        # TODO send email notification


def findReferenceArticles():
    data = requests.get(config.get(config.SITE_URL))
    html = BeautifulSoup(data.text, "html.parser")
    metas = html.head.select("meta")
    numero_rubrique = None
    numero_articles = []
    for meta in metas:
        if not meta.get("name"):
            continue
        if meta["name"] == "rubrique":
            numero_rubrique = meta["content"]
        elif meta["name"] == "article":
            numero_articles = meta["content"]
    if numero_rubrique and numero_articles:
        numero_articles = numero_articles.split(",")
    # saute le dernier article qui est une presentation de l'objet du site de 2016
    return numero_rubrique, numero_articles[:-1]


def findArticles(numero_rubrique, numero_articles):
    articles = []
    for numero_article in numero_articles:
        article_url = config.get(config.SITE_ARTICLE_URL).format(
            numero_rubrique, numero_article
        )
        date, titre, contenu = getArticle(article_url)
        articles.append({"date": date, "titre": titre, "contenu": contenu})
    return articles


def getArticle(url):
    data = requests.get(url)
    html = BeautifulSoup(data.text, "html.parser")
    date_article_div = html.find(id="dateETautre")
    article_div = date_article_div.parent
    titre_h2 = article_div.find(class_="titreArticle")
    soustitre_p = article_div.find(class_="sousTitre")
    titre_article = titre_h2.get_text() + soustitre_p.get_text()
    contenu_article = article_div.find("table").get_text()
    date_article = date_article_div.span.get_text()
    return date_article, titre_article, contenu_article
