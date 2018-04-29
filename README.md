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
 Escriba un script que procese documentos de un directorio y arme los índices que permitan soportar búsquedas booleanas. Luego, codifique un segundo script que permita buscar por uno o dos términos utilizando los operadores AND, OR y NOT (En el caso del operador NOT, aplique solo a consultas de longitud igual a 2. Por ejemplo, “casa NOT perro”. Entiéndase el uso de este operador como “todos los documentos que posean el término A y no posean el término B”.)

### Estructura
Indice de documentos: doc_name
Indice de terminos: termino
Indice invertido: term_id | df | puntero_posting_list
Posting list: [doc_id]