def wget(uri):    
    """    
    Devuelve el contenido indicado por una URI    
   
    Argumento:    
    > uri (str, por ejemplo 'http://inspyration.org')    
   
    Retorno:    
    > contenido de un archivo (bytes, archivo textual o binario)    
    """    
    # Análisis de la URI    
    parsed = urlparse(uri)    
    # Apertura de la conexión    
    with closing(HTTPConnection(parsed.netloc)) as conn:   
        # Ruta en el servidor    
        path = parsed.path    
        if parsed.query:    
            path += '?' + parsed.query    
        # Envío de la consulta al servidor    
        conn.request('GET', path)    
        # Recuperación de la respuesta    
        response = conn.getresponse()    
        # Análisis de la respuesta    
        if response.status != 200:    
            # 200 = Ok, 3xx = redirection, 4xx = error client,   
5xx = error servidor    
            print(response.reason, file=stderr)    
            return    
        # Devuelve la respuesta si todo está OK.    
        print('Respuesta OK')    
        return response.read() 