#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from os import sep
from sys import stderr

from http.client import HTTPConnection
from contextlib import closing
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from timeit import timeit


def wget(uri):
    """
    Retorna el contenido indicado por una URL

    Argumento :
    > uri (str, por ejemplo 'http://inspyration.org')

    Retorno :
    > contenido de un archivo (bytes, archivo textual o binario)
    """
    # Análisis de la URL
    parsed = urlparse(uri)
    # apertura de la conexión
    with closing(HTTPConnection(parsed.netloc)) as conn:
        # Ruta de servidor
        path = parsed.path
        if parsed.query:
            path += '?' + parsed.query
        # Envío de la consulta al servidor
        conn.request('GET', path)
        # Recuperación de la respuesta
        response = conn.getresponse()
        # Análisis de la respuesta
        if response.status != 200:
            # 200 = Ok, 3xx = redireccion, 4xx = error client, 5xx = error servidor
            return
        # Retorno de la respuesta si todo es OK.
        return response.read()


def download(uri):
    """
    Guarda en disco un archivo indicado por una URL

    Argumento :
    > uri (str, por ejemplo 'http://www.inspyration.org/logo.png')

    Retorno :
    > contenido de un archivo (bytes, archivo textual o binario)
    """
    content = wget(uri)
    if content is None:
        return None
    with open(uri.split(sep)[-1], 'wb') as f:
        f.write(content)
        return uri


def get_images_src_from_html(html_doc):
    """Recupera todo el contenido de los atributos src de las etiquetas img"""
    soup = BeautifulSoup(html_doc, "html.parser")
    return (img.get('src') for img in soup.find_all('img'))


def get_uri_from_images_src(base_uri, images_src):
    """Retorna una a una cada URL de imagen a descargar"""
    parsed_base = urlparse(base_uri)
    for src in images_src:
        parsed = urlparse(src)
        if parsed.netloc == '':
            path = parsed.path
            if parsed.query:
                path += '?' + parsed.query
            if path[0] != '/':
                if parsed_base.path == '/':
                    path = '/' + path
                else:
                    path = '/' + '/'.join(parsed_base.path.split('/')[:-1]) + '/' + path
            yield parsed_base.scheme + '://' + parsed_base.netloc + path
        else:
            yield parsed.geturl()


def get_images(page_uri):
    #
    # Recuperación de las URL de todas las imágenes de una página
    #
    html = wget(page_uri)
    if not html:
        print("Error: no se ha encontrado ninguna imagen", sys.stderr)
        return None
    images_src_gen = get_images_src_from_html(html)
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen)
    #
    # Recuperación de las imágenes
    #
    for image_uri in images_uri_gen:
        print('Descarga de %s' % image_uri)
        download(image_uri)


if __name__ == '__main__':
    print('--- Starting standard download ---')
    web_page_uri = 'http://www.formation-python.com/'
    print(timeit('get_images(web_page_uri)',
                 number=10,
                 setup="from __main__ import get_images, web_page_uri"))

# Tiempo evaluado: 16.50s

