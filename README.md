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
Métodos permitidos

cerca TERMINO1 TERMINO2
adyacente TERMINO1 TERMINO2

### Ejercicio
 Modifique el script del ejercicio 1 para armar un archivo invertido posicional a nivel de palabra. Luego, implemente consultas con operadores de proximidad y búsquedas booleanas por frases.

### Estructura
Indice de documentos: doc_name
Indice de terminos: termino
Indice invertido: term_id | df | puntero_posting_list
Posting: doc_id | TF | [posiciones]