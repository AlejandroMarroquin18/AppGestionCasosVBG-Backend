





def buscar(index, elemento, lista):
    if len(lista) == 0:
        return -1
    if lista[0] == elemento:
        return index
    return buscar(index + 1, elemento, lista[1:])

print(buscar(0,"hola",["","","hola","adios"]))
    