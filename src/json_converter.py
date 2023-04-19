import json

def from_dict(obj):
    # Se for um objeto, transforma num dict
    if hasattr(obj, '__dict__'):
        obj = obj.__dict__

    # Se for um dict, lê chaves e valores; converte valores
    if isinstance(obj, dict):
        return { k:from_dict(v) for k,v in obj.items() }
    # Se for uma lista ou tupla, lê elementos; também converte
    elif isinstance(obj, list) or isinstance(obj, tuple):
        return [from_dict(e) for e in obj]
    # Se for qualquer outra coisa, usa sem conversão
    else: 
        return obj