from lector import Lector
import re

class Lexer:
    def __init__(self):
        
        self.tokens = [] #Se guardarán todos los tokens
        self.archivo = None #El archivo a leer
        self.token = {
                    "id" : r"^[A-Za-z0-9_]{1,31}$",
                    "int" : r"^(0|[1-9][0-9]*)$",
                    "float" : r"^(0|[1-9][0-9]*)\.[0-9]+$",
                    "txt" : r"^\"[A-Za-z0-9_\-@%¿?¡!'\(\);:\.\+= ]*\"$",
                    "op" : r"^[+\-*/]$",
                    "key" : r"^(int|float|if|else|while|return|and|switch|do|not|for|default|case|boolean|try|catch|or|main|elif|print|input)$",
                    "comp" : r"^(==|!=|<=|>=|<|>|%|\+\+|--|\+=|-=)$",
                    "esp" : r"^[@$&~¬°(){}=!]$",
                    "punt" : r"^[,:]$",
                    "salt" : r"^[\n\t\r]$",
                    "coment" : r"^#([A-Za-z0-9 _\-@%¿?¡!;\(\)\.' '#]*)$"
                    }
        self.totalLineas = 0
        self.numeroErrores = 0
        self.errores = []
        self.lexemaAuxiliar = "" #Auxiliar para textos
        self.lexemaAux = "" #Auxiliar para id's o lo que sea (texto)
        self.lexemaAC = "" #Auxiliar para comentarios
        self.pila = [0]

    def leerArchivo(self, fileName):
        lec = Lector(fileName)
        self.archivo  = lec.readFile()
        #lexemas = self.archivo.split() #División por espacios/saltos

        if self.archivo == None:
            print("Error con la lectura del archivo")
        else:

            i = 0
            columna = 0 
            linea = 0 
            nivelId = 0
            inicioLinea = True

            while i < len(self.archivo):
                c = self.archivo[i]

                #Contar tabs al inicio de línea
                if inicioLinea:
                    contadorEspacios = 0 #si en vez de tabs usan espacios

                    while i < len(self.archivo) and self.archivo[i] in ['\t', ' ']:
                        if self.archivo[i] == '\t':
                            nivelId += 1
                        
                        elif self.archivo[i] == ' ':
                            contadorEspacios += 1
                            if contadorEspacios == 4:# 1 tab son 4 espacios
                                nivelId += 1
                                contadorEspacios = 0
                        
                        columna += 1
                        i += 1
                    
                    inicioLinea = False

                    #validar el tope de indentación
                    if nivelId > 5:
                        self.errores.append({
                            "lexema": "<ERROR PROFUNDIDAD>",
                            "tipo": "ERROR",
                            "linea": linea,
                            "columna": columna,
                            "identacion": nivelId,
                            "Desc": "Se fue momia :)"
                        })
                        nivelId = 5
                    
                    #si el nivel es mayor a la última indentación que se hizo, se agrega una nueva a la pila
                    if nivelId > self.pila[-1]:
                        self.tokens.append({
                            "lexema":"<INDENT>",
                            "tipo":"INDENT",
                            "linea":linea,
                            "columna":columna,
                            "identacion":nivelId
                        })
                        self.pila.append(nivelId)

                    #si el nivel es menor al que hay en la pila
                    elif nivelId < self.pila[-1]:
                        #mientras la indentación exista en la pila y sea menor a la indentación ya existente, se hace detentación para cerrar el bloque
                        while len(self.pila) > 1 and nivelId < self.pila[-1]:
                            self.tokens.append({
                                "lexema":"<DEDENT>",
                                "tipo":"DEDENT",
                                "linea":linea,
                                "columna":columna,
                                "identacion":0
                            })
                            self.pila.pop()

                        #si no hay en la pila
                        if nivelId not in self.pila:
                            self.errores.append({
                                "lexema":"<ERROR INDENT>",
                                "tipo":"ERROR",
                                "linea":linea,
                                "columna":columna,
                                "identacion":nivelId,
                                "Desc":"Indentación inválida"
                            })

                    inicioLinea = False
                    continue

                #Nueva línea
                if c == '\n':

                    #Primero validar si hay comentario
                    if self.lexemaAC: 
                        if re.fullmatch(self.token["coment"], self.lexemaAC):
                            self.tokens.append({
                                "lexema": self.lexemaAC,
                                "tipo": "coment",
                                "linea": linea,
                                "columna" : columna,
                                "identacion": nivelId
                            })
                            self.lexemaAC = ""
                        else:
                            self.errores.append({
                                "lexema": self.lexemaAC,
                                "tipo": "ERROR",
                                "linea": linea,
                                "columna" : columna,
                                "identacion": nivelId,
                                "Desc" : "Comentario No Valido"
                            })
                            self.lexemaAC = ""

                    linea += 1
                    columna = 1
                    inicioLinea = True
                    nivelId = 0
                    i += 1
                    continue

                #Saltar espacios
                if c == ' ':
                    columna += 1
                    i += 1
                    continue
                
                #Construir lexema
                lexema = ""
                
                # Manejar caracteres especiales que inician tokens
                if i < len(self.archivo) and self.archivo[i] in ['(', ')']:
                    lexema = self.archivo[i]
                    columna += 1
                    i += 1
                    self.clasificarToken(lexema, linea, columna, nivelId)
                    continue

                #Manejar cadenas de texto con comillas dobles
                if i < len(self.archivo) and self.archivo[i] == '"':
                    lexema = self.archivo[i]
                    columna += 1
                    i += 1
                    while i < len(self.archivo) and self.archivo[i] != '"' and self.archivo[i] != '\n': #Colocar la última validación para evitar bucle infinito
                        lexema += self.archivo[i]
                        columna += 1
                        i += 1
                    if i < len(self.archivo) and self.archivo[i] == '"':  # Agregar comilla de cierre solo si la encuentra
                        lexema += self.archivo[i]
                        columna += 1
                        i += 1
                    self.clasificarToken(lexema, linea, columna, nivelId)
                    continue

                #Manejo de comillas simples
                if i < len(self.archivo) and self.archivo[i] == "'":
                    lexema = self.archivo[i]
                    columna += 1
                    i += 1
                    while i < len(self.archivo) and self.archivo[i] != "'" and self.archivo[i] != '\n':
                        lexema += self.archivo[i]
                        columna += 1
                        i += 1
                    if i < len(self.archivo) and self.archivo[i] == "'":
                        lexema += self.archivo[i]
                        columna += 1
                        i += 1
                    # Marcar como error
                    self.errores.append({
                        "lexema": lexema,
                        "tipo": "ERROR",
                        "linea": linea,
                        "columna": columna,
                        "identacion": nivelId,
                        "Desc": "Comillas simples no permitidas"
                    })
                    continue

                # Manejar comentarios
                if i < len(self.archivo) and self.archivo[i] == '#':
                    lexema = ""
                    while i < len(self.archivo) and self.archivo[i] != '\n':
                        lexema += self.archivo[i]
                        columna += 1
                        i += 1
                    #self.clasificarToken(lexema, linea, columna, nivelId)
                    #print("Se ignoro comentario")
                    continue

                #Construir un lexema normal
                while i < len(self.archivo) and self.archivo[i] not in [' ', '\n', '\t', '"', "'", '#', '(', ')']:
                    lexema += self.archivo[i] #Se arma lexema hasta espacio en blanco, tabulación o salto de línea
                    columna += 1
                    i += 1

                if lexema:
                    self.clasificarToken(lexema, linea, columna, nivelId)

    def clasificarToken(self, lexema, linea, columna, identacion):
        
        # Si el lexema empieza con comilla, es texto
        if lexema and lexema[0] == '"':
            if re.fullmatch(self.token["txt"], lexema):
                self.tokens.append({
                    "lexema": lexema,
                    "tipo": "txt",
                    "linea": linea,
                    "columna": columna,
                    "identacion": identacion
                })
            else:
                self.errores.append({
                    "lexema": lexema,
                    "tipo": "ERROR",
                    "linea": linea,
                    "columna": columna,
                    "identacion": identacion,
                    "Desc": "Texto No Valido"
                })
            return
        
        # Si el lexema empieza con #, es comentario
        if lexema and lexema[0] == '#':
            if re.fullmatch(self.token["coment"], lexema):
                self.tokens.append({
                    "lexema": lexema,
                    "tipo": "coment",
                    "linea": linea,
                    "columna": columna,
                    "identacion": identacion
                })
            else:
                self.errores.append({
                    "lexema": lexema,
                    "tipo": "ERROR",
                    "linea": linea,
                    "columna": columna,
                    "identacion": identacion,
                    "Desc": "Comentario No Valido"
                })
            return

        #Análisis si solo es un caracter
        if len(lexema) == 1:
            self.leerCaracterI(lexema, linea, columna, identacion)
        #Análisis caracter a caracter dentro del lexema
        elif len(lexema) > 1:
            self.leerLexema(lexema, linea, columna, identacion)

    def leerCaracterI(self, c, linea, columna, identacion):
        #Es número
        if re.fullmatch(self.token["int"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "int",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        #Es identificador
        elif re.fullmatch(self.token["id"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "id",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            }) 
        #Es símbolo
        elif re.fullmatch(self.token["esp"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "esp",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
            
        #Es operador
        elif re.fullmatch(self.token["op"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "op",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
            
        #Es puntuación
        elif re.fullmatch(self.token["punt"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "punt",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        #Es comentario
        elif re.fullmatch(self.token["coment"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "coment",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        #Es comparador
        elif re.fullmatch(self.token["comp"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "comp",
                "linea": linea,
                "columna": columna,
                "identacion": identacion
            })
        #Es símbolo especial
        elif re.fullmatch(self.token["esp"], c):
            self.tokens.append({
                "lexema": c,
                "tipo": "esp",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        #No es nada XD
        else:
            self.errores.append({
                "lexema": c,
                "tipo": "Error",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion,
                "desc" : "Caracter no reconocido"
            })

    def leerLexema(self, lexema, linea, columna, identacion):
        sublexema = ""
        i = 0
        while i < len(lexema):

            #Ver si es especial al inicio
            if lexema[i] in ['(', '{'] and lexema[i] == lexema[0]: #Si el caracter está en primer lugar
                self.tokens.append({
                    "lexema": lexema[i],
                    "tipo": "esp",
                    "linea": linea,
                    "columna" : columna,
                    "identacion": identacion
                })

            #Ver si es especial al final
            elif lexema[i] in [')', '}'] and lexema[i] == lexema[len(lexema) - 1]:
                self.tokens.append({
                    "lexema": lexema[i],
                    "tipo": "esp",
                    "linea": linea,
                    "columna" : columna,
                    "identacion": identacion
                })
            #Operador o comparador
            elif lexema[i] in ['=', '!', '+', '-', '/', '*', '>', '<']:

                #Validar el error de operadores
                if i+1 < len(lexema) and lexema[i+1] in ['=', '!', '+', '-', '/', '*', '>', '<']:
                    comparador = lexema[i] + lexema[i+1]
                    if i+2 < len(lexema) and lexema[i+2] in ['=', '!', '+', '-', '/', '*', '>', '<']:
                        comparador += lexema[i+2]
                        i += 3 #Para que se pase directamente al tercer caracter
                        #Recolectar todo los operadores
                        while i < len(lexema) and lexema[i] in  ['=', '!', '+', '-', '/', '*', '>', '<']:
                            comparador += lexema[i]
                            i += 1
                        
                        self.errores.append({
                            "lexema": comparador,
                            "tipo": "ERROR",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion,
                            "Desc" : "Comparador con caractares excesivos"
                        })
                        i -= 1  # Decrementar porque el i += 1 del final lo incrementará
                        continue

                    elif re.fullmatch(self.token["comp"], comparador):
                        self.tokens.append({
                            "lexema": comparador,
                            "tipo": "comp",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion,
                        })
                        i += 1 #Aumentar para que comience correctamente
                    else:
                        self.errores.append({
                            "lexema": comparador,
                            "tipo": "ERROR",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion,
                            "Desc" : "Comparador no valido"
                        })
                        i += 1
                
                #Caso para ver si es operador
                elif lexema[i] in ['+', '-', '/', '*']:

                    if re.fullmatch(self.token["op"], lexema[i]):
                        self.tokens.append({
                            "lexema": lexema[i],
                            "tipo": "op",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion,
                        })
                elif lexema[i] in ['<', '>']:

                    if i+1 < len(lexema) and lexema[i+1] in ['=',  '!', '+', '-', '/', '*']: 
                        comparador += lexema[i+1] #Agrega el siguiente

                        if re.fullmatch(self.token["comp"], comparador):
                            self.tokens.append({
                                "lexema": comparador,
                                "tipo": "comp",
                                "linea": linea,
                                "columna" : columna,
                                "identacion": identacion,
                            })
                            i += 1 #Aumentar para que comience correctamente
                        else:
                            self.errores.append({
                                "lexema": comparador,
                                "tipo": "ERROR",
                                "linea": linea,
                                "columna" : columna,
                                "identacion": identacion,
                                "Desc" : "Comparador no valido"
                            })
                            i += 1

                    elif re.fullmatch(self.token["comp"], lexema[i]):
                        self.tokens.append({
                            "lexema": lexema[i],
                            "tipo": "comp",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion,
                        })
            #Puntuación
            elif lexema[i] in [',', ':', ';']:
                if re.fullmatch(self.token["punt"], lexema[i]):
                    self.tokens.append({
                        "lexema": lexema[i],
                        "tipo": "punt",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion
                    })
                else:
                    self.errores.append({
                        "lexema": lexema[i],
                        "tipo": "esp",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion
                    })
            #Ver si es comentario
            elif lexema[i] == '#':
                lexemaComent = ""

                while i < len(lexema): #Construye todo el comentario en ese lexema
                    lexemaComent += lexema[i]
                    i += 1

                self.lexemaAC += lexemaComent #Construir totalmente para la validación final

                #Por si todo está junto - Si se quiere tokenizar 👻
                '''if re.fullmatch(self.token["coment"], lexemaComent):
                    self.tokens.append({
                        "lexema": lexemaComent,
                        "tipo": "coment",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion
                    })
                    self.lexemaAC = ""'''
                
                #Agregar un espacio para construir todo el comentario
                self.lexemaAC += ' '

            #Ver si es texto
            elif lexema[i] in ['"', '\'']:
                lexemaCadena = lexema[i]

                if lexema[i] == '"':
                    i += 1
                    #Construir todo el texto
                    while i < len(lexema):
                        if lexema[i] == '"':
                            lexemaCadena += lexema[i]
                            break
                        lexemaCadena += lexema[i]
                        i += 1

                    #Validar de que lo que resta del lexema se tokenice
                    if i+1 < len(lexema):
                        i+=1
                        while i < len(lexema):
                            self.lexemaAux += lexema[i]
                        self.clasificarToken(self.lexemaAux, linea, columna, identacion)
                        self.lexemaAux = ""

                    self.lexemaAuxiliar += lexemaCadena #Para hacer la validación final

                    #En caso de que todo esté junto
                    if re.fullmatch(self.token["txt"], lexemaCadena):
                        self.tokens.append({
                            "lexema": lexemaCadena,
                            "tipo": "txt",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion
                        })
                        self.lexemaAuxiliar = ""
                    
                    #Agregar un espacio para construir el texto
                    self.lexemaAuxiliar += ' '

                elif lexema[i] == '\'':
                    #Construir todo el texto
                    while i < len(lexema):
                        if lexema[i] == '\'':
                            lexemaCadena += lexema[i]
                            i += 1
                            break
                        lexemaCadena += lexema[i]
                        i += 1
                    
                    #Validar de que lo que resta del lexema se tokenice
                    if i+1 < len(lexema):
                        i+=1 #Avanzar 1, para que no tome el '
                        while i < len(lexema):
                            self.lexemaAux += lexema[i]
                        self.clasificarToken(self.lexemaAux, linea, columna, identacion)
                        self.lexemaAux = ""

                    self.lexemaAuxiliar += lexemaCadena #Para hacer la validación final

                    #Agregar un espacio para construir el texto
                    self.lexemaAuxiliar += ' '

            #Todo pertenece a números y letras o solo números
            else:
                sublexema += lexema[i]

                if i+1 < len(lexema) and lexema[i+1] in ['(', '{', ')', '}', '=', '!', '+', '-', '/', '*', '>', '<', ',', ':', ';']:

                    #Tiene que ser key el sublexema para validar que el paréntesis pertenezca
                    if re.fullmatch(self.token["key"], sublexema):
                        if lexema[i+1] in ['(', '{']:
                            self.validarNI(sublexema, linea, columna, identacion)
                            self.leerCaracterI(lexema[i+1], linea, columna, identacion)
                            i+=1
                            sublexema = ""
                        else:
                            sublexema += lexema[i+1]
                    else:
                        #Validar sublexema antes de continuar a ver lo demás (símbolos)
                        self.validarNI(sublexema, linea, columna, identacion)
                        sublexema = ""

                elif i == len(lexema) - 1:
                    self.validarNI(sublexema, linea, columna, identacion)
                    sublexema = ""
            #Aumentar el contador
            i += 1
    
    #Ver si es identificador o números
    def validarNI(self, sublexema, linea, columna, identacion):
        # Validar que no sea número inválido (empieza con 0 o tiene letras después de números)
        if sublexema and sublexema[0].isdigit():
            if sublexema[0] == '0' and len(sublexema) > 1 and sublexema[1].isdigit():
                self.errores.append({
                    "lexema": sublexema,
                    "tipo": "ERROR",
                    "linea": linea,
                    "columna": columna,
                    "identacion": identacion,
                    "Desc": "Número inválido: no puede empezar con 0"
                })
                return
            # Si empieza con número pero tiene letras, es error
            if any(c.isalpha() for c in sublexema):
                self.errores.append({
                    "lexema": sublexema,
                    "tipo": "ERROR",
                    "linea": linea,
                    "columna": columna,
                    "identacion": identacion,
                    "Desc": "Identificador inválido: no puede empezar con número"
                })
                return
            
        # Validar longitud de identificador (truncar si es mayor a 31)
        if len(sublexema) > 31 and re.match(r"^[A-Za-z0-9_]", sublexema):
            self.errores.append({
                "lexema": sublexema[:31],  # Truncar a 31 caracteres
                "tipo": "ERROR",
                "linea": linea,
                "columna": columna,
                "identacion": identacion,
                "Desc": f"Identificador muy largo (original: {len(sublexema)} caracteres, truncado a 31)"
            })
            return
            
        if re.fullmatch(self.token["float"], sublexema):
            self.tokens.append({
                "lexema": sublexema,
                "tipo": "float",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        elif re.fullmatch(self.token["int"], sublexema):
            self.tokens.append({
                "lexema": sublexema,
                "tipo": "int",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        elif re.fullmatch(self.token["key"], sublexema):
            self.tokens.append({
                "lexema": sublexema,
                "tipo": "key",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        elif re.fullmatch(self.token["id"], sublexema):
            self.tokens.append({
                "lexema": sublexema,
                "tipo": "id",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion
            })
        else:
            self.errores.append({
                "lexema": sublexema,
                "tipo": "ERROR",
                "linea": linea,
                "columna" : columna,
                "identacion": identacion,
                "Desc" : "Lexema no valido, no sea burro"
            })

    def imprimirTokens(self):

        if len(self.tokens) != 0:
            print("Tokens capturados:")
            for token in self.tokens:
                print(f"Lexema - {token['lexema']}, tipo - {token['tipo']}, linea - {token['linea']}, columna - {token['columna']}, identacion - {token['identacion']}")

        if len(self.errores) != 0:
            print("\nErrores capturados:")
            for token in self.errores:
                print(f"Lexema - {token['lexema']}, tipo - {token['tipo']}, linea - {token['linea']}, columna - {token['columna']}, identacion - {token['identacion']}, Descripcion - {token['Desc']}")             