# src/time_service.py

import re
from datetime import timedelta
from typing import Optional

def parse_offset_to_timedelta(offset_str: str) -> Optional[timedelta]:
    """
    Analisa uma string de offset de horário e a converte em um objeto timedelta.

    A string de entrada deve estar em um formato como "+1h", "-30m", "+2h15m",
    "-1h30m10s", etc. Suporta horas (h), minutos (m) e segundos (s).
    O sinal (+ ou -) no início é opcional; se omitido, assume-se positivo.

    Args:
        offset_str: A string que representa o offset de horário.

    Returns:
        Um objeto timedelta correspondente ao offset. Retorna None se a string
        for inválida ou não contiver nenhuma unidade de tempo válida.
    """
    # Expressão regular para capturar o sinal, horas, minutos e segundos
    # Cada parte é opcional, mas pelo menos uma deve estar presente.
    pattern = re.compile(
        r"^(?P<sign>[+-])?"
        r"((?P<hours>\d+)h)?"
        r"((?P<minutes>\d+)m)?"
        r"((?P<seconds>\d+)s)?$"
    )
    
    match = pattern.match(offset_str.strip())

    if not match:
        return None

    parts = match.groupdict()
    
    # Se nenhuma unidade de tempo foi encontrada, o formato é inválido
    if not (parts['hours'] or parts['minutes'] or parts['seconds']):
        return None

    # Converte as partes para inteiros, com 0 como padrão se ausente
    hours = int(parts['hours'] or 0)
    minutes = int(parts['minutes'] or 0)
    seconds = int(parts['seconds'] or 0)

    # Determina o multiplicador com base no sinal
    multiplier = -1 if parts['sign'] == '-' else 1

    return timedelta(
        hours=multiplier * hours,
        minutes=multiplier * minutes,
        seconds=multiplier * seconds
    )

# Bloco para testes e demonstração
if __name__ == "__main__":
    test_cases = [
        "+2h30m",
        "-1h",
        "45m",
        "-10s",
        "+1h15m30s",
        "-0h0m5s",
        "invalid",
        "1h-30m",
        "+h"
    ]

    print("--- Testando parse_offset_to_timedelta ---")
    for case in test_cases:
        result = parse_offset_to_timedelta(case)
        print(f"Input: '{case}' -> Output: {result}")