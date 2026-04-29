import pandas as pd
import os

print("=" * 80)
print("NORMALIZACIÓN DE EQUIPO_IDEAL.CSV")
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
print("- Leyendo equipo_ideal.csv...")
df_equipo, _, _ = leer_csv_con_codificacion('equipo_ideal.csv', separadores=[','])

print("\n- Leyendo Mundial.csv...")
df_mundial, _, _ = leer_csv_con_codificacion('Mundial.csv', separadores=[';', ','])

print("\n- Leyendo Jugador.csv...")
df_jugador, _, _ = leer_csv_con_codificacion('Jugador.csv', separadores=[';', ','])

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
print(f"     Ejemplo: 2018 → {dict_mundial.get('2018')}")

# 3. PROCESAR JUGADOR.CSV
print("\n🔍 PROCESANDO JUGADOR.CSV...")
if len(df_jugador.columns) == 1 and ';' in df_jugador.columns[0]:
    df_jugador = df_jugador.iloc[:, 0].str.split(';', expand=True)
    df_jugador.columns = ['id', 'referencia', 'nombre', 'birthday', 'height']
else:
    df_jugador.columns = ['id', 'referencia', 'nombre', 'birthday', 'height']

df_jugador['referencia'] = df_jugador['referencia'].astype(str)

# Crear formatos de búsqueda
df_jugador['ref_original'] = df_jugador['referencia'].str.lower().str.strip()
df_jugador['ref_con_guiones'] = df_jugador['ref_original'].str.replace(' ', '_')
df_jugador['ref_php'] = df_jugador['ref_con_guiones'] + '.php'

dict_jugador_php = dict(zip(df_jugador['ref_php'], df_jugador['id'].astype(int)))
dict_jugador_guiones = dict(zip(df_jugador['ref_con_guiones'], df_jugador['id'].astype(int)))
dict_jugador_original = dict(zip(df_jugador['ref_original'], df_jugador['id'].astype(int)))

print(f"  ✅ Diccionario jugadores: {len(dict_jugador_php)} entradas")
print(f"     Ejemplo: lionel_messi.php → {dict_jugador_php.get('lionel_messi.php')}")

# 4. FUNCIÓN PARA BUSCAR JUGADOR
def buscar_jugador(referencia):
    if pd.isna(referencia) or referencia == '':
        return None
    
    ref = str(referencia).strip().lower()
    
    # Intentar búsqueda en diferentes formatos
    if ref in dict_jugador_php:
        return dict_jugador_php[ref]
    
    if ref.endswith('.php'):
        sin_php = ref.replace('.php', '')
        if sin_php in dict_jugador_guiones:
            return dict_jugador_guiones[sin_php]
    
    if '_' in ref:
        con_espacios = ref.replace('_', ' ').replace('.php', '')
        if con_espacios in dict_jugador_original:
            return dict_jugador_original[con_espacios]
    
    return None

# 5. TRANSFORMAR DATOS
print("\n🔄 TRANSFORMANDO DATOS (MANTENIENDO ORDEN)...")

# Crear copia para resultados
df_resultado = df_equipo.copy()
df_resultado['id_mundial'] = None
df_resultado['id_jugador'] = None

stats = {
    'total': len(df_equipo),
    'mundial_ok': 0,
    'jugador_ok': 0,
    'mundial_no_encontrado': 0,
    'jugador_no_encontrado': 0
}

errores_detalle = []
ejemplos_exitosos = []

for idx, row in df_equipo.iterrows():
    try:
        # PASO 1: Convertir mundial
        año = str(row['mundial']).strip()
        id_mundial = dict_mundial.get(año)
        
        if id_mundial is None:
            stats['mundial_no_encontrado'] += 1
            errores_detalle.append(f"Fila {idx+1}: Año {año} no encontrado")
            continue
        
        df_resultado.at[idx, 'id_mundial'] = id_mundial
        stats['mundial_ok'] += 1
        
        # PASO 2: Convertir jugador
        jugador_val = str(row['jugador']).strip() if pd.notna(row['jugador']) else ''
        
        if jugador_val:
            id_jugador = buscar_jugador(jugador_val)
            if id_jugador is not None:
                df_resultado.at[idx, 'id_jugador'] = id_jugador
                stats['jugador_ok'] += 1
                if len(ejemplos_exitosos) < 5:
                    ejemplos_exitosos.append((jugador_val, id_jugador))
            else:
                stats['jugador_no_encontrado'] += 1
                errores_detalle.append(f"Fila {idx+1}: Jugador '{jugador_val}' no encontrado")
        
        # Mostrar progreso
        if (idx + 1) % 25 == 0:
            print(f"  Procesadas {idx + 1}/{stats['total']} filas...")
            
    except Exception as e:
        errores_detalle.append(f"Fila {idx+1}: Error - {str(e)}")

# 6. MOSTRAR EJEMPLOS DE ÉXITO
print("\n✨ EJEMPLOS DE JUGADORES ENCONTRADOS:")
for ref, id_jug in ejemplos_exitosos[:5]:
    print(f"  ✓ '{ref}' → ID: {id_jug}")

# 7. SELECCIONAR SOLO LAS COLUMNAS DESEADAS
print("\n📝 SELECCIONANDO COLUMNAS FINALES...")
df_final = df_resultado[['id_mundial', 'id_jugador']].copy()

# 8. ESTADÍSTICAS
print("\n📊 ESTADÍSTICAS DEL PROCESAMIENTO:")
print(f"  Total filas originales: {stats['total']}")
print(f"  ✅ Mundiales convertidos: {stats['mundial_ok']}")
print(f"  ✅ Jugadores encontrados: {stats['jugador_ok']}")
print(f"  ❌ Mundiales no encontrados: {stats['mundial_no_encontrado']}")
print(f"  ❌ Jugadores no encontrados: {stats['jugador_no_encontrado']}")

# Mostrar errores
if errores_detalle:
    print(f"\n⚠️  PRIMEROS 5 ERRORES:")
    for e in errores_detalle[:5]:
        print(f"     {e}")

# 9. GUARDAR ARCHIVO
print("\n💾 GUARDANDO ARCHIVO...")
nombre_salida = 'equipo_ideal_normalizado.csv'
df_final.to_csv(nombre_salida, sep=';', index=False, encoding='utf-8')
print(f"  ✅ Archivo guardado: {nombre_salida}")
print(f"  📊 Filas guardadas: {len(df_final)}")

# 10. MOSTRAR MUESTRA (MANTENIENDO ORDEN)
print("\n👀 PRIMERAS 20 FILAS DEL RESULTADO (mismo orden):")
print(df_final.head(20))

# 11. VERIFICACIÓN CON ORIGINAL
print("\n📋 VERIFICACIÓN DE LOS PRIMEROS 10 REGISTROS:")
print("-" * 60)
print(f"{'ID Orig':<6} | {'Año':<6} | {'id_mundial':<5} | {'Jugador':<25} | {'id_jugador':<8}")
print("-" * 60)

for i in range(min(10, len(df_equipo))):
    orig = df_equipo.iloc[i]
    final = df_final.iloc[i]
    
    print(f"{orig['id']:<6} | {orig['mundial']:<6} | {final['id_mundial']:<5} | "
          f"{str(orig['jugador'])[:23]:<25} | {final['id_jugador']:<8}")

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO - SE MANTUVO EL ORDEN ORIGINAL")
print("=" * 80)