#Instancias
from lexer import Lexer

def main():
    #implementar lógica
    archivo = "texto1.txt"
    lec = Lexer()
    lec.leerArchivo(archivo)
    lec.imprimirTokens()

if __name__ == "__main__":
    main()
    