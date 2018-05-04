# RI-Estructuras-de-datos
@author - Zamudio Fabian (2018)
Repositorio de Recuperación de Información

### Ejemplo de uso
Indexar corpus
```
python indexador.py -c <path_directorio_corpus> 
```

### Ejercicio
Asumiendo que tiene una cantidad limitada de memoria codifique un script que indexe una colección suficientemente grande y que requiera el volcado parcial a disco. 

### Estructura
Indice de documentos: doc_name
Indice de terminos: termino
Indice invertido: term_id | df | puntero_posting_list
Posting: doc_id 