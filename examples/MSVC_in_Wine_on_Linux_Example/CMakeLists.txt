cmake_minimum_required(VERSION 3.10)

# Nombre del proyecto
project(RandomNumberGenerator C)

# Agregar el archivo fuente
add_executable(cprogram cprogram.c)

# Configurar el estándar de C
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED True)
