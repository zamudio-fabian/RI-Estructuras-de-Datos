# RI - Recuperación de información

@author - Zamudio Fabian (2017)
@Proyecto - Estructuras de Datos para RI

Repositorio de Recuperación de Información



1.  Escriba un programa que procese documentos de un directorio y arme los índices que
permitan soportar búsquedas booleanas. Luego, codifique un segundo programa que
permita buscar por uno o dos términos utilizando los operadores AND, OR y NOT. 

2.  Utilizando el programa anterior ejecute corridas con diferentes colecciones. Calcule los
tamaños mínimos, máximos y promedio de las listas de posteo. ¿Qué utilidad tiene esta
información? Calcule el overhead de los índices respecto de la colección. Calcule el
overhead para cada documento. ¿Qué conclusiones se pueden extraer?

3.  **Agregue documentos a una colección (indexación incremental) y repita el ejercicio 2. Sus resultados: ¿Son consistentes con la ley de Heaps? Este proceso es costoso: ¿Cómo se puede realizar eficientemente?**

4.  Modifique el programa del ejercicio 1 para armar un archivo invertido posicional a nivel de
palabra. Luego, implemente consultas con operadores de proximidad.

5.  Modifique el programa del ejercicio 1 para armar un archivo invertido con información de
frecuencias. Luego, implemente consultas utilizando el modelo vectorial utilizando tres
esquemas de ponderación y/o ranking diferentes.

6.  Modifique su programa anterior para que realice indexación posicional y soporte búsquedas
booleanas por frases.

7.  Agregue skip lists a su índice del ejercicio 1 y ejecute un conjunto de consultas AND sobre
el índice original y luego usando los punteros. Compare los tiempos de ejecución.

8.  A partir de un conjunto de posting lists provistas realice un programa que arme el
vocabulario utilizando un B+Tree por un lado y un archivo binario con la información de las
postings y frecuencias por el otro. Use DGaps y agregue skip-lists.

9.  A partir del archivo de palabras en inglés (words-en.txt)  calcule el tamaño necesario
para almacenarlo en memoria sin comprimir o como dictionary-as-string. Haga una
notebook y calcule la distribución de longitudes de las palabras y las estadísticas básicas.
Conviene tomar una valor máximo de palabra? Justifique.

10. Sobre la estructura del ejercicio 8 escriba un programa que realice una evaluación Term-ata-Time
y otro usando Document-at-a-Time. Compare los tiempos de ejecución para un
conjunto de queries dados. Separe su análisis por longitud de queries y de posting lists.

11. A partir de una colección utilizada en ejercicios previos construya el índice invertido con
información de frecuencias y comprímalo utilizando Elias-Gamma y Variable-Lenght Codes.
Calcule tiempos de compresión/descompresión y tamaño resultante en cada caso. Realice
dos experimentos, uno codificando con DGaps y otro sin codificar. Compare los tamanos de
los índices resultantes.