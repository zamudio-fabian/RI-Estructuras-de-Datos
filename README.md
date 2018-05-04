# RI-Estructuras-de-datos
@author - Zamudio Fabian (2018)
Repositorio de Recuperación de Información

### Ejemplo de uso
Indexar corpus
```
python indexador.py -c <path_directorio_corpus> [-v <path_archivo_stopwords>] 
```
Busqueda booleana
```
python booleano.py 
```

### Ejercicio
Agregue skip lists a su índice del ejercicio 1 y ejecute un conjunto de consultas AND sobre el índice original y luego usando los punteros. Compare los tiempos de ejecución

### Estructura
Indice de documentos: doc_name
Indice de terminos: termino
Indice invertido: term_id | df | puntero_posting_list
Posting: doc_id