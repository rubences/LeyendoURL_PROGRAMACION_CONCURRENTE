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
    Devuelve el contenido designado por una URI

    Argumento :
    > uri (str, por ejemplo 'http://inspyration.org')

    Retorno :
    > contenido de un archivo (bytes, archivo de texto o binario)
    """
    # Análisis de la URI
    parsed = urlparse(uri)
    # apertura de  la conexión
    with closing(HTTPConnection(parsed.netloc)) as conn:
        # Ruta en el servidor
        path = parsed.path
        if parsed.query:
            path += '?' + parsed.query
        # Envío de la consulta al servidor
        conn.request('GET', path)
        # Recuperación de la respuesta
        response = conn.getresponse()
        # Analyse de la respuesta
        if response.status != 200:
            # 200 = Ok, 3xx = redirección, 4xx = error de cliente, 5xx = error de servidor
            return
        # Envío de la respuesta si todo está OK.
        return response.read()


def download(uri):
    """
    Guardar en disco duro un archivo designado por una URI

    Argumento :
    > uri (str, por ejemplo 'http://www.inspyration.org/logo.png')

    Retorno :
    > contenido de un archivo (bytes, archivo de texto o binario)
    """
    content = wget(uri)
    if content is None:
        return None
    with open(uri.split(sep)[-1], 'wb') as f:
        f.write(content)
        return uri


def get_images_src_from_html(html_doc):
    """Recupera todos los contenidos de los atributos src de las etiquetas img"""
    soup = BeautifulSoup(html_doc, "html.parser")
    return [img.get('src') for img in soup.find_all('img')]


def get_uri_from_images_src(base_uri, images_src):
    """Devuelve una a una cada URI de imagen a descargar """
    parsed_base = urlparse(base_uri)
    result = []
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
            result.append(parsed_base.scheme + '://' + parsed_base.netloc + path)
        else:
            result.append(parsed.geturl())
    return result


def get_images(page_uri):
    #
    # Recuperación de las URI de todas las imágenes de una página
    #
    html = wget(page_uri)
    if not html:
        print("Error: no se ha encontrado ninguna imagen", sys.stderr)
        return None
    images_src = get_images_src_from_html(html)
    images_uri = get_uri_from_images_src(page_uri, images_src)
    #
    # Recuperación de las imágenes
    #
    for image_uri in images_uri:
        print('Descarga de %s' % image_uri)
        download(image_uri)


if __name__ == '__main__':
    print('--- Starting standard download ---')
    web_page_uri = 'http://www.formation-python.com/'
    print(timeit('get_images(web_page_uri)',
                 number=10,
                 setup="from __main__ import get_images, web_page_uri"))

# Tiempo evaluado: 16.75s

