import pandas as pd
import os
import re

print("=" * 80)
print("NORMALIZACIÓN DE PREMIOS.CSV")
print("=" * 80)

# Lista de codificaciones a probar
codificaciones = ['latin-1', 'ISO-8859-1', 'cp1252', 'utf-8', 'utf-8-sig']

# 1. CARGAR ARCHIVOS
print("\n📂 CARGANDO ARCHIVOS...")

# Función para leer CSV
def leer_csv_con_codificacion(nombre_archivo, separadores=[',', ';']):
    for sep in separadores:
        for codif in codificaciones:
            try:
                print(f"  Probando {nombre_archivo} con separador '{sep}' y codificación: {codif}")
                df = pd.read_csv(nombre_archivo, sep=sep, encoding=codif)
                df.columns = [col.replace('ï»¿', '').replace('Ã±', 'ñ').strip() for col in df.columns]
                print(f"  ✅ {nombre_archivo} leído correctamente")
                print(f"     {len(df)} filas cargadas")
                print(f"     Columnas: {list(df.columns)}")
                return df, codif, sep
            except Exception as e:
                print(f"     ❌ Falló: {str(e)[:50]}...")
                continue
    raise Exception(f"No se pudo leer {nombre_archivo}")

# Cargar archivos
print("- Leyendo premios.csv...")
df_premios, _, _ = leer_csv_con_codificacion('premios.csv', separadores=[','])

print("\n- Leyendo Mundial.csv...")
df_mundial, _, _ = leer_csv_con_codificacion('Mundial.csv', separadores=[';', ','])

print("\n- Leyendo Jugador.csv...")
df_jugador, _, _ = leer_csv_con_codificacion('Jugador.csv', separadores=[';', ','])

print("\n- Leyendo Pais.csv...")
df_pais, _, _ = leer_csv_con_codificacion('Pais.csv', separadores=[',', ';'])

# 2. PROCESAR MUNDIAL.CSV
print("\n🔍 PROCESANDO MUNDIAL.CSV...")
if len(df_mundial.columns) == 1 and ';' in df_mundial.columns[0]:
    df_mundial = df_mundial.iloc[:, 0].str.split(';', expand=True)
    df_mundial.columns = ['id', 'año', 'id_pais_organizador', 'id_pais_campeon']
else:
    df_mundial.columns = ['id', 'año', 'id_pais_organizador', 'id_pais_campeon']

df_mundial['año'] = df_mundial['año'].astype(str)
dict_mundial = dict(zip(df_mundial['año'], df_mundial['id'].astype(int)))
print(f"  ✅ Diccionario mundial: año → id_mundial ({len(dict_mundial)} entradas)")

# 3. PROCESAR JUGADOR.CSV - CREAR MÚLTIPLES FORMATOS DE BÚSQUEDA
print("\n🔍 PROCESANDO JUGADOR.CSV...")
if len(df_jugador.columns) == 1 and ';' in df_jugador.columns[0]:
    df_jugador = df_jugador.iloc[:, 0].str.split(';', expand=True)
    df_jugador.columns = ['id', 'referencia', 'nombre', 'birthday', 'height']
else:
    df_jugador.columns = ['id', 'referencia', 'nombre', 'birthday', 'height']

df_jugador['referencia'] = df_jugador['referencia'].astype(str)

# Crear diferentes formatos de búsqueda
print("\n  Creando múltiples formatos de referencia...")

# Formato 1: Original (con espacios) - ej: "lionel messi"
df_jugador['ref_original'] = df_jugador['referencia'].str.lower().str.strip()

# Formato 2: Con guiones bajos (formato PHP) - ej: "lionel_messi"
df_jugador['ref_con_guiones'] = df_jugador['ref_original'].str.replace(' ', '_')

# Formato 3: Con .php - ej: "lionel_messi.php"
df_jugador['ref_php'] = df_jugador['ref_con_guiones'] + '.php'

# Formato 4: Sin espacios ni guiones - ej: "lionelmessi"
df_jugador['ref_sin_espacios'] = df_jugador['ref_original'].str.replace(' ', '')

# Crear diccionarios para cada formato
dict_jugador_original = dict(zip(df_jugador['ref_original'], df_jugador['id'].astype(int)))
dict_jugador_guiones = dict(zip(df_jugador['ref_con_guiones'], df_jugador['id'].astype(int)))
dict_jugador_php = dict(zip(df_jugador['ref_php'], df_jugador['id'].astype(int)))
dict_jugador_sin_espacios = dict(zip(df_jugador['ref_sin_espacios'], df_jugador['id'].astype(int)))

print(f"  ✅ Diccionario original (con espacios): {len(dict_jugador_original)} entradas")
print(f"  ✅ Diccionario con guiones: {len(dict_jugador_guiones)} entradas")
print(f"  ✅ Diccionario con .php: {len(dict_jugador_php)} entradas")
print(f"  ✅ Diccionario sin espacios: {len(dict_jugador_sin_espacios)} entradas")

print(f"\n  Ejemplo: 'lionel messi' → ID: {dict_jugador_original.get('lionel messi')}")
print(f"  Ejemplo: 'lionel_messi' → ID: {dict_jugador_guiones.get('lionel_messi')}")
print(f"  Ejemplo: 'lionel_messi.php' → ID: {dict_jugador_php.get('lionel_messi.php')}")

# 4. PROCESAR PAIS.CSV
print("\n🔍 PROCESANDO PAIS.CSV...")
if len(df_pais.columns) == 1 and ';' in df_pais.columns[0]:
    df_pais = df_pais.iloc[:, 0].str.split(';', expand=True)
    df_pais.columns = ['id', 'nombre']
else:
    df_pais.columns = ['id', 'nombre']

df_pais['nombre'] = df_pais['nombre'].astype(str).str.lower().str.strip()
dict_pais = dict(zip(df_pais['nombre'], df_pais['id'].astype(int)))
print(f"  ✅ Diccionario países: nombre → id_pais ({len(dict_pais)} entradas)")

# 5. FUNCIÓN PARA BUSCAR JUGADOR EN MÚLTIPLES FORMATOS
def buscar_jugador(referencia):
    if pd.isna(referencia) or referencia == '':
        return None
    
    ref = str(referencia).strip().lower()
    
    # Intento 1: Buscar exactamente como viene (.php)
    if ref in dict_jugador_php:
        return dict_jugador_php[ref]
    
    # Intento 2: Si tiene .php, quitar .php y buscar con guiones
    if ref.endswith('.php'):
        sin_php = ref.replace('.php', '')
        if sin_php in dict_jugador_guiones:
            return dict_jugador_guiones[sin_php]
    
    # Intento 3: Si tiene guiones, convertir a espacios
    if '_' in ref:
        con_espacios = ref.replace('_', ' ').replace('.php', '')
        if con_espacios in dict_jugador_original:
            return dict_jugador_original[con_espacios]
    
    # Intento 4: Buscar directamente en original (por si viene sin formato)
    if ref in dict_jugador_original:
        return dict_jugador_original[ref]
    
    # Intento 5: Buscar en guiones (por si viene sin .php)
    if ref in dict_jugador_guiones:
        return dict_jugador_guiones[ref]
    
    return None

# 6. CREAR NUEVAS COLUMNAS
print("\n🔄 TRANSFORMANDO DATOS...")

df_resultado = df_premios.copy()
df_resultado['id_mundial'] = None
df_resultado['id_jugador'] = None
df_resultado['id_pais'] = None

stats = {
    'total': len(df_premios),
    'mundial_ok': 0,
    'jugador_ok': 0,
    'pais_ok': 0,
    'mundial_no_encontrado': 0,
    'jugador_no_encontrado': 0,
    'pais_no_encontrado': 0
}

errores_detalle = []
ejemplos_exitosos = []

for idx, row in df_premios.iterrows():
    try:
        # PASO 1: Mundial
        año = str(row['mundial']).strip()
        id_mundial = dict_mundial.get(año)
        
        if id_mundial is None:
            stats['mundial_no_encontrado'] += 1
            errores_detalle.append(f"Fila {idx+1}: Año {año} no encontrado")
            continue
        
        df_resultado.at[idx, 'id_mundial'] = id_mundial
        stats['mundial_ok'] += 1
        
        # PASO 2: Jugador
        jugador_val = str(row['jugador']).strip() if pd.notna(row['jugador']) and row['jugador'] != '' else ''
        
        if jugador_val and jugador_val.lower() != 'nan':
            id_jugador = buscar_jugador(jugador_val)
            if id_jugador is not None:
                df_resultado.at[idx, 'id_jugador'] = id_jugador
                stats['jugador_ok'] += 1
                if len(ejemplos_exitosos) < 5:
                    ejemplos_exitosos.append((jugador_val, id_jugador))
            else:
                stats['jugador_no_encontrado'] += 1
                errores_detalle.append(f"Fila {idx+1}: Jugador '{jugador_val}' no encontrado")
        
        # PASO 3: País
        pais_val = str(row['pais']).strip() if pd.notna(row['pais']) and row['pais'] != '' else ''
        
        if pais_val and pais_val.lower() != 'nan':
            pais_lower = pais_val.lower().strip()
            id_pais = dict_pais.get(pais_lower)
            if id_pais is not None:
                df_resultado.at[idx, 'id_pais'] = id_pais
                stats['pais_ok'] += 1
            else:
                stats['pais_no_encontrado'] += 1
                errores_detalle.append(f"Fila {idx+1}: País '{pais_val}' no encontrado")
        
        # Mostrar progreso
        if (idx + 1) % 25 == 0:
            print(f"  Procesadas {idx + 1}/{stats['total']} filas...")
            
    except Exception as e:
        errores_detalle.append(f"Fila {idx+1}: Error - {str(e)}")

# 7. MOSTRAR EJEMPLOS DE ÉXITO
print("\n✨ EJEMPLOS DE JUGADORES ENCONTRADOS:")
for ref, id_jug in ejemplos_exitosos:
    print(f"  ✓ '{ref}' → ID: {id_jug}")

# 8. SELECCIONAR COLUMNAS FINALES
print("\n📝 SELECCIONANDO COLUMNAS FINALES...")
df_final = df_resultado[['id_mundial', 'id_premio', 'id_jugador', 'id_pais']].copy()

# 9. ESTADÍSTICAS
print("\n📊 ESTADÍSTICAS DEL PROCESAMIENTO:")
print(f"  Total filas originales: {stats['total']}")
print(f"  ✅ Mundiales convertidos: {stats['mundial_ok']}")
print(f"  ✅ Jugadores encontrados: {stats['jugador_ok']}")
print(f"  ✅ Países encontrados: {stats['pais_ok']}")
print(f"  ❌ Mundiales no encontrados: {stats['mundial_no_encontrado']}")
print(f"  ❌ Jugadores no encontrados: {stats['jugador_no_encontrado']}")
print(f"  ❌ Países no encontrados: {stats['pais_no_encontrado']}")

# 10. GUARDAR ARCHIVO
print("\n💾 GUARDANDO ARCHIVO...")
nombre_salida = 'premios_normalizado.csv'
df_final.to_csv(nombre_salida, sep=';', index=False, encoding='utf-8')
print(f"  ✅ Archivo guardado: {nombre_salida}")
print(f"  📊 Filas guardadas: {len(df_final)}")

# 11. MOSTRAR MUESTRA
print("\n👀 PRIMERAS 20 FILAS DEL RESULTADO:")
print(df_final.head(20))

# 12. VERIFICACIÓN DETALLADA
print("\n📋 VERIFICACIÓN DE LOS PRIMEROS 10 REGISTROS:")
print("-" * 100)
print(f"{'ID':<4} | {'Año':<6} | {'id_mundial':<5} | {'Premio':<5} | {'Jugador':<25} | {'id_jugador':<8} | {'País':<12} | {'id_pais':<5}")
print("-" * 100)

for i in range(min(10, len(df_premios))):
    orig = df_premios.iloc[i]
    final = df_final.iloc[i]
    
    print(f"{orig['id']:<4} | {orig['mundial']:<6} | {final['id_mundial']:<5} | {final['id_premio']:<5} | "
          f"{str(orig['jugador'])[:23]:<25} | {str(final['id_jugador']):<8} | "
          f"{str(orig['pais'])[:10]:<12} | {str(final['id_pais']):<5}")

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print("=" * 80)