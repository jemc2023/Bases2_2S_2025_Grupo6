import pandas as pd
import os

# Nombre del archivo
archivo = "Jugador.csv"

# 1. Leer el archivo CSV
print(f"Leyendo el archivo: {archivo}")
try:
    # Especificamos el separador correcto que es ';' y que los encabezados están en la primera fila
    df = pd.read_csv(archivo, sep=';', encoding='utf-8')
    print(f"Archivo leído correctamente. Total de filas iniciales: {len(df)}")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo {archivo}. Asegúrate de que esté en la misma carpeta que este script.")
    exit()
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    exit()

# Mostrar las primeras filas para verificar la lectura
print("\nPrimeras 5 filas del archivo original:")
print(df.head())

# 2. Eliminar filas duplicadas exactas
# El parámetro keep='first' conserva la primera ocurrencia y elimina las siguientes.
# inplace=True modifica el DataFrame directamente.
print("\nEliminando filas duplicadas exactas...")
filas_antes = len(df)
df.drop_duplicates(keep='first', inplace=True)
filas_despues = len(df)
duplicados_eliminados = filas_antes - filas_despues

print(f"Filas antes: {filas_antes}")
print(f"Filas después: {filas_despues}")
print(f"Total de filas duplicadas exactas eliminadas: {duplicados_eliminados}")

# 3. Guardar el resultado en un archivo nuevo
nombre_archivo_limpio = "Jugador_sin_duplicados.csv"
df.to_csv(nombre_archivo_limpio, sep=';', index=False, encoding='utf-8')
print(f"\nArchivo limpio guardado como: {nombre_archivo_limpio}")

# 4. (Opcional) Mostrar el resultado
print("\nPrimeras 5 filas del archivo limpio:")
print(df.head())

# 5. (Opcional) Si quieres sobrescribir el archivo original, descomenta la siguiente línea
# df.to_csv(archivo, sep=';', index=False, encoding='utf-8')
# print(f"\nArchivo original sobrescrito con los datos limpios.")