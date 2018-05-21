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
python vectorial.py [-t <A|B|C>]
```

### Ejercicio
Modifique el script del ejercicio 1 para armar un archivo invertido con información de frecuencias. Luego, implemente consultas utilizando el modelo vectorial utilizando tres esquemas de ponderación y/o ranking diferentes.

### Estructura
Indice de documentos: doc_name
Indice de terminos: termino
Indice invertido: term_id | DF | IDF | puntero_posting_list
Posting: doc_id | TF 