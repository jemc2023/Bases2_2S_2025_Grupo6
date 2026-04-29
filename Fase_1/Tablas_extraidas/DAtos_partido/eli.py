import pandas as pd
import os

def eliminar_duplicados_por_url(archivo_entrada, archivo_salida=None):
    """
    Elimina filas duplicadas basándose en la columna 'url'
    
    Args:
        archivo_entrada (str): Ruta del archivo CSV de entrada
        archivo_salida (str): Ruta del archivo CSV de salida (opcional)
    
    Returns:
        pandas.DataFrame: DataFrame sin duplicados
    """
    
    # Leer el archivo CSV
    print(f"Leyendo archivo: {archivo_entrada}")
    df = pd.read_csv(archivo_entrada)
    
    # Mostrar información inicial
    print(f"\nInformación inicial:")
    print(f"Total de filas: {len(df)}")
    print(f"URLs únicas: {df['url'].nunique()}")
    
    # Detectar duplicados basados en la columna 'url'
    duplicados = df[df.duplicated('url', keep=False)]
    
    if len(duplicados) > 0:
        print(f"\n🔍 Se encontraron {len(duplicados)} filas con URLs duplicadas")
        print("\nFilas duplicadas encontradas:")
        
        # Agrupar por URL para mostrar los duplicados
        for url, grupo in duplicados.groupby('url'):
            print(f"\nURL: {url}")
            print(f"Número de repeticiones: {len(grupo)}")
            print("Índices:", grupo.index.tolist())
            print("Países:", list(zip(grupo['pais1'], grupo['pais2'])))
    else:
        print("\n✅ No se encontraron filas duplicadas basadas en la URL")
    
    # Eliminar duplicados (keep='first' mantiene la primera ocurrencia)
    df_sin_duplicados = df.drop_duplicates(subset=['url'], keep='first')
    
    # Mostrar información final
    print(f"\n📊 Resumen:")
    print(f"Filas originales: {len(df)}")
    print(f"Filas después de eliminar duplicados: {len(df_sin_duplicados)}")
    print(f"Filas eliminadas: {len(df) - len(df_sin_duplicados)}")
    
    # Guardar el resultado
    if archivo_salida is None:
        # Si no se especifica archivo de salida, crear uno con sufijo '_sin_duplicados'
        nombre, extension = os.path.splitext(archivo_entrada)
        archivo_salida = f"{nombre}_sin_duplicados{extension}"
    
    df_sin_duplicados.to_csv(archivo_salida, index=False)
    print(f"\n💾 Archivo guardado como: {archivo_salida}")
    
    return df_sin_duplicados

def verificar_duplicados_detallado(df):
    """
    Verificación detallada de duplicados en diferentes columnas
    """
    print("\n" + "="*50)
    print("VERIFICACIÓN DETALLADA DE DUPLICADOS")
    print("="*50)
    
    # Verificar duplicados exactos en todas las columnas
    duplicados_completos = df[df.duplicated(keep=False)]
    print(f"\n📋 Duplicados exactos (todas las columnas): {len(duplicados_completos)}")
    
    # Verificar duplicados solo por URL
    duplicados_url = df[df.duplicated('url', keep=False)]
    print(f"🔗 Duplicados por URL: {len(duplicados_url)}")
    
    # Verificar duplicados por combinación de países
    duplicados_paises = df[df.duplicated(['pais1', 'pais2'], keep=False)]
    print(f"🌍 Duplicados por combinación de países: {len(duplicados_paises)}")
    
    # Verificar duplicados por mundial y grupos
    duplicados_mundial_grupo = df[df.duplicated(['mundial', 'grupo'], keep=False)]
    print(f"🏆 Duplicados por mundial y grupo: {len(duplicados_mundial_grupo)}")
    
    return {
        'completos': len(duplicados_completos),
        'url': len(duplicados_url),
        'paises': len(duplicados_paises),
        'mundial_grupo': len(duplicados_mundial_grupo)
    }

# Ejemplo de uso
if __name__ == "__main__":
    archivo = "todos_los_partidos.csv"
    
    try:
        # Primero verificar duplicados detalladamente
        df_original = pd.read_csv(archivo)
        estadisticas = verificar_duplicados_detallado(df_original)
        
        # Eliminar duplicados por URL
        df_limpio = eliminar_duplicados_por_url(archivo)
        
        print("\n" + "="*50)
        print("✅ PROCESO COMPLETADO")
        print("="*50)
        
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{archivo}'")
        print("Asegúrate de que el archivo está en el directorio correcto")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")