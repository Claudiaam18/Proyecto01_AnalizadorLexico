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
                    "txt" : r"^[A-Za-z0-9_\-@%¿?¡!'\(\);\.]*$",
                    "op" : r"^[+\-*/]$",
                    "key" : r"^(int|float|if|else|while|return|and|switch|do|not|for|default|case|boolean|try|catch|or|main|elif|print)$",
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

    def leerArchivo(self, fileName):
        lec = Lector(fileName)
        self.archivo  = lec.readFile()
        #lexemas = self.archivo.split() #División por espacios/saltos

        i = 0
        columna = 0 
        linea = 0 
        nivelId = 0
        inicioLinea = True

        while i < len(self.archivo):
            c = self.archivo[i]

            #Contar tabs al inicio de línea
            if inicioLinea and c == '\t':
                nivelId += 1
                #lexema = (f"Linea - {linea}", f"col - {columna}", f"salt <Salto de linea>")
                #self.tokens.append(lexema) #Se agrega el lexema de salto de línea
                columna += 1
                i += 1
                continue
            
            #Si encontramos algo que no es tab
            if inicioLinea and c not in ['\t', ' ', '\n']:
                inicioLinea = False
                #Ver flujo para controlar salto de línea !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            #Nueva línea
            if c == '\n':

                #Primero validar si hay comentario
                if len(self.lexemaAC) != 0 and re.fullmatch(self.token["coment"], self.lexemaAC):
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
            if i < len(self.archivo) and self.archivo[i] in ['"', "'", '#', '(', ')']:
                lexema = self.archivo[i]
                columna += 1
                i += 1
                self.clasificarToken(lexema, linea, columna, nivelId)
                continue

            while i < len(self.archivo) and self.archivo[i] not in [' ', '\n', '\t', '"', "'", '#', '(', ')']:
                lexema += self.archivo[i] #Se arma lexema hasta espacio en blanco, tabulación o salto de línea
                columna += 1
                i += 1

            if lexema:
                self.clasificarToken(lexema, linea, columna, nivelId)

    def clasificarToken(self, lexema, linea, columna, identacion):
        
        #Ver si es comentario o cadena de texto
        if len(self.lexemaAuxiliar) != 0:
            #Cadena
            if self.lexemaAuxiliar[0] == '"' or self.lexemaAuxiliar[0] == '\'':
                i = 0
                lexemaCadena = ""

                #Construir todo el texto
                while i < len(lexema):

                    if lexema[i] == '"':
                        lexemaCadena += lexema[i]
                        i += 1

                        #Terminar de leer lo que resta (si hay más)
                        if i < len(lexema):
                            while i < len(lexema):
                                self.lexemaAux += lexema[i]
                                i += 1
                            self.clasificarToken(self.lexemaAux,linea, columna, identacion)
                            self.lexemaAux = ""
                        break

                    lexemaCadena += lexema[i]
                    i += 1
                    
                    self.lexemaAuxiliar += lexemaCadena #Para hacer la validación final

            if self.lexemaAuxiliar[len(self.lexemaAuxiliar) - 1] == '"':
                if re.fullmatch(self.token["txt"], self.lexemaAuxiliar):
                    self.tokens.append({
                        "lexema": self.lexemaAuxiliar,
                        "tipo": "txt",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion
                    })
                    self.lexemaAuxiliar = ""
                else:
                    self.errores.append({
                        "lexema": self.lexemaAuxiliar,
                        "tipo": "ERROR",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion,
                        "Desc" : "Texto No Valido"
                    })
                    self.lexemaAuxiliar = ""
            elif self.lexemaAuxiliar[len(self.lexemaAuxiliar) - 1] == '\'':
                self.errores.append({
                        "lexema": self.lexemaAuxiliar,
                        "tipo": "ERROR",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion,
                        "Desc" : "Texto No Valido por comillas simples"
                    })
                self.lexemaAuxiliar = ""
        
        #comentario
        if len(self.lexemaAC) != 0 and self.lexemaAC[0] == '#':
            i = 0
            lexemaCadena = ""
            #Construir todo el comentario
            while i < len(lexema):        
                lexemaCadena += lexema[i]
                i += 1                    
            self.lexemaAC += lexemaCadena #Para hacer la validación final

        #Análisis si solo es un caracter
        if len(lexema) == 1:
            self.leerCaracterI(lexema, linea, columna, identacion)
        #Análisis caracter a caracter dentro del lexema
        elif len(lexema) > 1:
            self.leerLexema(lexema, linea, columna, identacion)

    def leerCaracterI(self, c, linea, columna, identacion):
        #Es identificador
        if re.fullmatch(self.token["id"], c):
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
            self.tokens.append({
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

                #Caso para ver si es comparador (doble)
                comparador = lexema[i] #Variable de apoyo
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

                #Por si todo está junto
                if re.fullmatch(self.token["coment"], lexemaComent):
                    self.tokens.append({
                        "lexema": lexemaComent,
                        "tipo": "coment",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion
                    })
                    self.lexemaAC = ""
                
                #Agregar un espacio para construir todo el comentario
                self.lexemaAC += ' '
                '''else:
                    self.errores.append({
                        "lexema": lexemaComent,
                        "tipo": "ERROR",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion,
                        "Desc" : "Comentario No Valido"
                    })'''
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
                    '''else:
                        self.errores.append({
                            "lexema": lexemaCadena,
                            "tipo": "ERROR",
                            "linea": linea,
                            "columna" : columna,
                            "identacion": identacion,
                            "Desc" : "Texto No Valido"
                        })'''
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

                    #Error
                    '''self.errores.append({
                        "lexema": lexemaCadena,
                        "tipo": "ERROR",
                        "linea": linea,
                        "columna" : columna,
                        "identacion": identacion,
                        "Desc" : "Texto No Valido por comillas simples"
                    })'''
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
                "desc" : "Lexema no valido, no sea burro"
            })

    def imprimirTokens(self):
        print("Tokens capturados:")
        for token in self.tokens:
            print(f"Lexema - {token['lexema']}, tipo - {token['tipo']}, linea - {token['linea']}, columna - {token['columna']}, identacion - {token['identacion']}")

        print("\nErrores capturados:")
        for token in self.errores:
            print(f"Lexema - {token['lexema']}, tipo - {token['tipo']}, linea - {token['linea']}, columna - {token['columna']}, identacion - {token['identacion']}, Descripcion - {token['Desc']}")             