# Archivo de prueba para verificar que las herramientas funcionan

# 1. isort - imports desordenados
import os
import sys
from pathlib import Path

from django.conf import settings


# 2. black - formato inconsistente =====
def hello(name):  # Espacios innecesarios
    return "Hello " + name  # Espacios inconsistentes


# 3. flake8 - código suelto
unused_variable = 42  # Variable no utilizada
very_long_line_that_exceeds_100_characters_limit_and_should_trigger_flake8_error = True


# 4. mypy - tipos de datos incorrectos
def add_numbers(x: int, y: int) -> int:
    return x + y


result: int = add_numbers(5, "10")  # Error: "10" es string, no int


def process_data(data):  # Sin type hints
    print(data)
