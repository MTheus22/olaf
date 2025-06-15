import os
import re

# Em src/main.py, substitua a função antiga por esta:

def parse_photographer_name(filename: str) -> str | None:
    """
    Extrai de forma inteligente o nome da pessoa do nome do arquivo,
    aplicando regras de validação para evitar falsos positivos.
    """
    # 1. Remove a extensão do arquivo para trabalhar apenas com o nome base
    name_base, _ = os.path.splitext(filename)

    # 2. Se não houver um underscore, não há como extrair o nome.
    if '_' not in name_base:
        return None

    # 3. Divide a string a partir da direita, no último underscore
    potential_name, _ = name_base.rsplit('_', 1)
    
    # 4. Limpa espaços em branco no início ou fim
    cleaned_name = potential_name.strip()

    # --- INÍCIO DAS NOVAS REGRAS DE VALIDAÇÃO ---

    # Regra A: Se o nome limpo for vazio, é inválido.
    if not cleaned_name:
        return None

    # Regra B: Se o nome começar com um dígito, provavelmente é uma data. Inválido.
    if cleaned_name[0].isdigit():
        return None
        
    # Regra C: Se o nome tiver menos de 3 caracteres, é improvável que seja um nome. Inválido.
    if len(cleaned_name) < 3:
        return None

    # Regra D: Se não houver nenhuma letra no nome (ex: "123-456"), é inválido.
    # Usamos uma expressão regular para verificar a existência de qualquer letra.
    if not re.search(r'[a-zA-Z]', cleaned_name):
        return None

    # --- FIM DAS REGRAS DE VALIDAÇÃO ---

    # 5. Se passou em todas as validações, formata (troca '_' por ' ') e retorna o nome.
    return cleaned_name.replace('_', ' ')

def sanitize_for_filename(name: str) -> str:
    """
    Limpa um nome para ser seguro para uso em um nome de arquivo.
    Substitui espaços por hífens e remove caracteres inválidos.
    """
    import re
    # Substitui espaços e underscores por hífen
    name = re.sub(r'[\s_]+', '-', name)
    # Remove acentos (uma abordagem simples)
    name = re.sub(r'[áàâãä]', 'a', name, flags=re.IGNORECASE)
    name = re.sub(r'[éèêë]', 'e', name, flags=re.IGNORECASE)
    name = re.sub(r'[íìîï]', 'i', name, flags=re.IGNORECASE)
    name = re.sub(r'[óòôõö]', 'o', name, flags=re.IGNORECASE)
    name = re.sub(r'[úùûü]', 'u', name, flags=re.IGNORECASE)
    name = re.sub(r'[ç]', 'c', name, flags=re.IGNORECASE)
    # Remove quaisquer caracteres restantes que não sejam letras, números ou hífen
    name = re.sub(r'[^a-zA-Z0-9-]', '', name)
    return name