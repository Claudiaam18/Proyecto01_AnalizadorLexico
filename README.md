# Proyecto01_AnalizadorLexico

----- Funcionamiento del proyecto -----
En la fase #1, el analizador léxico tiene como objetivo leer un archivo de texto que contiene fragmentos de código en un lenguaje específico, en este caso Python. El programa procesa el código línea por línea, identifica cada lexema y lo clasifica en tokens utilizando expresiones regulares definidas previamente. Con apoyo de la gramática, el analizador también detecta errores que no están permitidos en el lenguaje, como símbolos no definidos, números inválidos o niveles de indentación que exceden el límite establecido. Para cada token reconocido o error encontrado, se registra su tipo, el lexema correspondiente, la posición en la línea, la columna y el nivel de indentación.

----- Análisis de la gramática -----
La gramática tiene como objetivo definir la sintaxis del lenguaje y permitir la construcción del árbol de análisis. Con ella se interpreta de manera más precisa la lectura del código. Para este proyecto se diseñaron:
- Símbolos No Terminales: representados por las letras A–I, que estructuran las reglas de producción.
- Símbolos Terminales: definidos mediante expresiones regulares, invocadas según los casos de prueba (id, int, float, txt, op, key, comp, esp, punt, salt, coment).
- Símbolo inicial: S, que contiene la producción principal y puede derivar en diversas instrucciones opcionales.

Se expresa como: 

GM =  {(S,A,B,C,D, E, F, G, H, I), (id, int, float, txt, op, key, comp, esp, punt, salt, coment), (S), (
S -> Key A| id B | int | float | tzx | coment | boolean | key[Return] S | S + C| S – C| C
A -> (E) {codex} F| Key(H) {codex}| (text)| id = J| id[int nombreVariable]
B -> comp| ε| =G| comp id[id+= id]
C -> C*D| C/D| D
D -> (S)| num| id| float
E -> S comp S G| S, S comp S, S| S G
F -> key(E){-}F| Key{-}| ε
G -> key S comp S G| ε| key[and|or]S G
H -> ε| I
I -> S,I| S
J -> num| txt| bool| id
codex -> salt S| ε
)}

Ejemplos posibles:
Casos de operaciones:
S -> S + 5_ -> 5_ + 6_ -> 6_ + id -> (S) + id -> (5_) + id -> (5_ * 6_) + id -> (6_ * num) + id -> (num * num) + id -> (15*12) + x

Casos de inicio sin key
x -> Variable para usar
x++ | x-- | x+= | x -=
x = otraVariable | int | float | boolean

Casos inicio con key
int x = 18 | int x = otraVariable
int x | Boolean cosita | float variable
Print(“algo”)
Public main(int jalapeño, string papitas, Boolean pilin) {}
For(int i = 0, i < [10 | var], i++){ más código }
If(idBoolean) {} | If([num | var ] == [num | var] [and | or] idBoolean)
If([num | var] == [num | var] [and|or] [num | var] == [num | var]){} [elif(){} | else {} | ε]
While([num | var] == [num | var] [and|or] [num | var] == [num | var] | varBool){}


----- Decisiones tomadas para el diseño de la gramática -----
Se decidió trabajar con Python, por lo que la gramática debía contemplar la sintaxis del lenguane, se optó por una gramática reducida que, con ayuda de las expresiones, contempla las construcciones más comunes dentro de la programación.
Se trabajó con el símbolo ε para validar las construcciones del código.

----- Expresiones regulares -----
a. Identificadores (ID) con una longitud máxima de 31 caracteres. 
id = [(A-Z) | (a-z) | (0-9) | _]+

b. Números enteros y flotantes. 
int = [0 | (1-9) (0-9)*] 
Float = [0 | (1-9)(0-9)*] “.” (0-9)+ 

c. Cadenas de texto.
txt = “[(A-Z) | (a-z) | (0-9) | ( | _ | - | @ | % | ¿ | ? | ¡ | ! | ) | ‘ | ’ | (; | ( | . | ) ]*“  

d. Operadores aritméticos y lógicos.
op = [+ | - | * | /] 

e. Palabras clave (int, float, if, else, while, etc.). 
key = [ int | float | if | else | while | return | and | switch | do | not | for | default | case | boolean | try | catch | or| main| elif | public | void | private] 

f. Símbolos especiales ({}, (), ;, %. <,>, <=, >=, ==, !=, ,).
comp  = [ == | != | <= | >= | < | > | % | ++ | -- | += | -= ]
esp = [@ | $ | & | ~ | ¬ | °| ( | ) | { | } | = | !]
punt = [, | :|]

g. Saltos de línea e indentación
salt = [ \n | \t | \r ]

h. Comentarios
coment = # [ (A-Z) | (a-z) | (0-9) | ( _ | - | @ | % | ¿ | ? | ¡ | !) | “ “ | (; | ( | . | ) ]*

En el caso de los operadores, símbolos especiales y comparadores se separaron por mayor flexibilidad

Casos de prueba:
1.	Programa que imprima “Hola mundo”
-	El programa leerá el archivo y se espera que el resultado sea:
Print(“Hola Mundo”) 
Print -> keyword
() -> símbolos especiales 
“Hola Mundo” -> cadena de texto
 
2.	Programa que realice una operación aritmética básica
-	El programa recibirá una operación aritmética básica clasificando según su token:
Ej: 
int x = (45 + 2)*10/4  
int -> keyword
x -> Identificador
= -> Comparador
( -> Símbolo Especial
45 -> Entero
+ -> Operador lógico
2 -> Entero
) -> Símbolo Especial 
* -> Operador aritmético
10 -> Entero
/ -> Operador aritmético
4	-> Entero

3.	Un programa que demuestre el uso del input de datos y de acuerdo con la entrada del usuario decidir el flujo del programa a través de un if.

Ej:

int x = input (“Ingrese un numero”)
if(x > 2):
	print(“Es mayor”)
else:
	print(“Es menor”)

int -> keyword
x -> Identificador
= -> Comparador
input -> Keyword
( -> Símbolo especial
“Ingrese un numero”  Cadena de texto
) -> Símbolo especial
If -> Keyword
> -> Comparador
2 -> Entero
: -> Puntuación
“Es mayor” -> Cadena de texto
else -> Keyword
“Es menor” -> Cadena de texto

4.	Definición de una función que reciba parámetros y devuelva un resultado, la función debe ser llamada desde el programa principal.

Ej:

main() {

Print(Funcion(3,5))

}

Int Funcion(int a, int b)
{
	Return a + b
}

main -> keyword
( -> Símbolo especial
) -> Símbolo especial
{ -> Símbolo especial
Print -> Keyword
Funcion -> ID
3 -> int
, -> puntuacion
5 -> int
} -> Símbolo especial
Int -> keyword
a -> ID
b -> ID
Return -> keyword
+ -> operador aritmético


5.	Programa que contenga definición de variables, entrada y salida de datos, y que utilice el bucle “while”
int x = 5
while(x > 2):
 	x = input (“Ingrese un numero”)
print(“El numero es: “ + x)

int -> Keyword
x -> Identificador
= -> Comparador
5 -> Entero
while -> Keword
( -> Símbolo Especial
> -> Comparador
2 -> Entero
) -> Símbolo Especial
: -> Símbolo Especial
input -> Keyword
“Ingrese un numero” -> Cadena de texto
print -> Keyword
“El numero es: “ -> Cadena de texto
+ -> Operador Aritmético

----- Manejo de errores -----
El analizador léxico maneja los errores de forma controlada y detallada. Cada lexema se valida contra expresiones regulares; si no coincide, se registra como error con información sobre el lexema, la línea, la columna y el nivel de indentación. Se contemplan errores de símbolos no definidos, números inválidos, comentarios o textos mal formados, operadores incorrectos y problemas de indentación (exceso de niveles o inconsistencias en la pila). Todos los errores se almacenan en una lista y se muestran junto con los tokens válidos, lo que permite un análisis completo del archivo sin detener la ejecución.

El programa tiene como lógica leer caracter por caracter, concatenando cada uno y registrando su token cuando exista una lógica dentro de la concatenación. Al momento de leer un caracter y valide que no se valida contra las expresiones, se agrega a self.errores con información sobre el error que se está presentando.

Para la indentación antes de empezar a clasificar los tokens, cuenta los tabs, los cuales serán los niveles, y se comparará con la pila, se contempla el caso de que se exceda el 5to nivel de indentación, forzándolo a bajar un nivel, si al desapilar no se encuentra el nivel en la pila, se identificará cómo error.