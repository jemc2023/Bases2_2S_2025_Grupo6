import pandas as pd
import os

print("=" * 80)
print("NORMALIZACIÓN DE JUGADOR_PLANTEL.CSV")
print("=" * 80)

# Lista de codificaciones a probar
codificaciones = ['latin-1', 'ISO-8859-1', 'cp1252', 'utf-8', 'utf-8-sig']

# 1. CARGAR ARCHIVOS CON MANEJO DE ERRORES DE CODIFICACIÓN
print("\n📂 CARGANDO ARCHIVOS...")

# Función para leer CSV con diferentes codificaciones
def leer_csv_con_codificacion(nombre_archivo):
    for codif in codificaciones:
        try:
            print(f"  Probando {nombre_archivo} con codificación: {codif}")
            df = pd.read_csv(nombre_archivo, sep=';', encoding=codif)
            
            # Limpiar nombres de columnas (eliminar caracteres raros)
            df.columns = [col.replace('ï»¿', '').replace('Ã±', 'ñ').strip() for col in df.columns]
            
            print(f"  ✅ {nombre_archivo} leído correctamente con {codif}")
            print(f"     {len(df)} filas cargadas")
            print(f"     Columnas: {list(df.columns)}")
            return df, codif
        except UnicodeDecodeError:
            print(f"     ❌ Falló con {codif}")
            continue
        except Exception as e:
            print(f"     ❌ Otro error con {codif}: {e}")
            continue
    raise Exception(f"No se pudo leer {nombre_archivo} con ninguna codificación")

# Cargar jugador_plantel.csv
print("- Leyendo jugador_plantel.csv...")
df_jugador_plantel, codif_usada = leer_csv_con_codificacion('jugador_plantel.csv')
print(f"  ✅ Usando codificación: {codif_usada}")

# Cargar Mundial.csv
print("\n- Leyendo Mundial.csv...")
df_mundial, _ = leer_csv_con_codificacion('Mundial.csv')

# Cargar Plantel.csv
print("\n- Leyendo Plantel.csv...")
df_plantel, _ = leer_csv_con_codificacion('Plantel.csv')

# Cargar Jugador.csv
print("\n- Leyendo Jugador.csv...")
df_jugador, _ = leer_csv_con_codificacion('Jugador.csv')

# Mostrar las primeras filas para verificar
print("\n👀 Verificando datos cargados:")
print("Primeras 3 filas de jugador_plantel.csv:")
print(df_jugador_plantel.head(3))
print("\nPrimeras 3 filas de Mundial.csv:")
print(df_mundial.head(3))
print("\nPrimeras 3 filas de Plantel.csv:")
print(df_plantel.head(3))
print("\nPrimeras 3 filas de Jugador.csv:")
print(df_jugador.head(3))

# 2. IDENTIFICAR NOMBRES DE COLUMNAS CORRECTOS
print("\n🔍 IDENTIFICANDO COLUMNAS...")

# Para Mundial.csv
print(f"Columnas en Mundial.csv: {df_mundial.columns.tolist()}")
# Renombrar columnas de Mundial.csv si es necesario
df_mundial.columns = ['id', 'año', 'id_pais_organizador', 'id_pais_campeon']
print(f"  ✅ Columnas renombradas en Mundial.csv: {df_mundial.columns.tolist()}")

# Para Plantel.csv
print(f"Columnas en Plantel.csv: {df_plantel.columns.tolist()}")
# Renombrar columnas de Plantel.csv
df_plantel.columns = ['id', 'id_mundial', 'id_pais', 'grupo']
print(f"  ✅ Columnas renombradas en Plantel.csv: {df_plantel.columns.tolist()}")

# Para Jugador.csv
print(f"Columnas en Jugador.csv: {df_jugador.columns.tolist()}")
# Renombrar columnas de Jugador.csv
df_jugador.columns = ['id', 'referencia', 'nombre', 'birthday', 'height']
print(f"  ✅ Columnas renombradas en Jugador.csv: {df_jugador.columns.tolist()}")

# 3. CREAR DICCIONARIOS DE BÚSQUEDA
print("\n🔍 CREANDO DICCIONARIOS DE BÚSQUEDA...")

# Diccionario 1: año → id_mundial
df_mundial['año'] = df_mundial['año'].astype(str)
dict_mundial = dict(zip(df_mundial['año'], df_mundial['id']))
print(f"  ✅ Mundial: año → id ({len(dict_mundial)} entradas)")
print(f"     Ejemplo: 2022 → {dict_mundial.get('2022')}")

# Diccionario 2: (id_mundial + grupo) → lista de id_plantel
dict_plantel = {}
for _, row in df_plantel.iterrows():
    clave = f"{row['id_mundial']}_{row['grupo']}"
    if clave not in dict_plantel:
        dict_plantel[clave] = []
    dict_plantel[clave].append({
        'id_plantel': row['id'],
        'id_pais': row['id_pais']
    })
print(f"  ✅ Plantel: (id_mundial+grupo) → lista de planteles ({len(dict_plantel)} claves únicas)")

# Diccionario 3: referencia → id_jugador
df_jugador['referencia'] = df_jugador['referencia'].astype(str)
df_jugador['ref_lower'] = df_jugador['referencia'].str.lower().str.strip()
dict_jugador = dict(zip(df_jugador['ref_lower'], df_jugador['id']))
print(f"  ✅ Jugador: referencia → id_jugador ({len(dict_jugador)} entradas)")
print(f"     Ejemplo: karim adeyemi → {dict_jugador.get('karim adeyemi')}")

# 4. PROCESAR FILA POR FILA
print("\n🔄 TRANSFORMANDO DATOS...")

resultados = []
errores = {
    'mundial': [],
    'plantel': [],
    'jugador': [],
    'multiple_plantel': [],
    'otros': []
}

total_filas = len(df_jugador_plantel)

for idx, row in df_jugador_plantel.iterrows():
    try:
        # PASO 1: Obtener id_mundial desde el año
        año = str(row['mundial']).strip()
        id_mundial = dict_mundial.get(año)
        
        if id_mundial is None:
            errores['mundial'].append(f"Fila {idx+1}: Año {año} no encontrado en Mundial.csv")
            continue
        
        # PASO 2: Buscar posibles planteles por (id_mundial + grupo)
        clave_plantel = f"{id_mundial}_{row['grupo']}"
        posibles_planteles = dict_plantel.get(clave_plantel, [])
        
        if not posibles_planteles:
            errores['plantel'].append(f"Fila {idx+1}: No hay plantel para mundial {año} (ID:{id_mundial}), grupo {row['grupo']}")
            continue
        
        # PASO 3: Si hay múltiples planteles, necesitamos el país para discriminar
        # Como no tenemos el país en jugador_plantel, intentamos inferir por el nombre del país
        if len(posibles_planteles) > 1:
            # Intentar encontrar el país correcto por el nombre
            pais_nombre = str(row['pais']).strip().lower()
            
            # Por ahora, tomamos el primero y registramos el problema
            id_plantel = posibles_planteles[0]['id_plantel']
            errores['multiple_plantel'].append(
                f"Fila {idx+1}: Múltiples planteles para {clave_plantel} (país: {pais_nombre}), usando ID:{id_plantel}"
            )
        else:
            id_plantel = posibles_planteles[0]['id_plantel']
        
        # PASO 4: Obtener id_jugador por referencia
        referencia = str(row['referencia']).strip().lower()
        id_jugador = dict_jugador.get(referencia)
        
        if id_jugador is None:
            errores['jugador'].append(f"Fila {idx+1}: Referencia '{row['referencia']}' no encontrada en Jugador.csv")
            continue
        
        # PASO 5: Crear registro normalizado
        # Manejar camiseta como número entero
        try:
            num_camisa = int(float(row['camiseta']))
        except:
            num_camisa = row['camiseta']
        
        resultados.append({
            'id_plantel': id_plantel,
            'id_jugador': id_jugador,
            'num_camisa': num_camisa,
            'posicion': row['posicion']
        })
        
        # Mostrar progreso
        if (idx + 1) % 500 == 0:
            print(f"  Procesadas {idx + 1}/{total_filas} filas...")
            
    except Exception as e:
        errores['otros'].append(f"Fila {idx+1}: Error - {str(e)}")

# 5. MOSTRAR ESTADÍSTICAS
print("\n📊 ESTADÍSTICAS DEL PROCESAMIENTO:")
print(f"  Total filas procesadas: {total_filas}")
print(f"  ✅ Transformaciones exitosas: {len(resultados)}")
print(f"  ❌ Errores totales: {sum(len(v) for v in errores.values())}")
print(f"     - Sin match en Mundial.csv: {len(errores['mundial'])}")
print(f"     - Sin match en Plantel.csv: {len(errores['plantel'])}")
print(f"     - Sin match en Jugador.csv: {len(errores['jugador'])}")
print(f"     - Múltiples planteles (usado primero): {len(errores['multiple_plantel'])}")
print(f"     - Otros errores: {len(errores['otros'])}")

# Mostrar ejemplos de errores
for tipo, lista in errores.items():
    if lista and len(lista) > 0:
        print(f"\n⚠️  EJEMPLOS DE ERRORES ({tipo}):")
        for e in lista[:3]:
            print(f"     {e}")

# 6. CREAR DATAFRAME FINAL
print("\n📝 CREANDO ARCHIVO NORMALIZADO...")
df_final = pd.DataFrame(resultados)

if len(df_final) > 0:
    # Asegurar el orden correcto de columnas
    df_final = df_final[['id_plantel', 'id_jugador', 'num_camisa', 'posicion']]
    
    # 7. GUARDAR ARCHIVO
    nombre_salida = 'jugador_plantel_normalizado.csv'
    df_final.to_csv(nombre_salida, sep=';', index=False, encoding='utf-8')
    print(f"  ✅ Archivo guardado: {nombre_salida}")
    print(f"  📊 Filas guardadas: {len(df_final)}")
    
    # 8. MOSTRAR MUESTRA
    print("\n👀 PRIMERAS 20 FILAS DEL RESULTADO:")
    print(df_final.head(20))
    
    # 9. VERIFICACIONES
    print("\n🔍 VERIFICACIONES DE INTEGRIDAD:")
    print(f"  - IDs de plantel únicos: {df_final['id_plantel'].nunique()}")
    print(f"  - IDs de jugador únicos: {df_final['id_jugador'].nunique()}")
    print(f"  - Rango de números de camiseta: {df_final['num_camisa'].min()} - {df_final['num_camisa'].max()}")
    print(f"  - Posiciones únicas: {df_final['posicion'].unique()}")
    
    # 10. VERIFICAR ALGUNOS REGISTROS ESPECÍFICOS
    print("\n🎯 VERIFICANDO PRIMEROS REGISTROS:")
    for i in range(min(5, len(df_final))):
        print(f"  Registro {i+1}: Plantel ID {df_final.iloc[i]['id_plantel']}, "
              f"Jugador ID {df_final.iloc[i]['id_jugador']}, "
              f"Camiseta #{df_final.iloc[i]['num_camisa']}, "
              f"{df_final.iloc[i]['posicion']}")
else:
    print("\n❌ No se generaron resultados. Revisa los errores arriba.")

print("\n" + "=" * 80)
print("✅ PROCESO COMPLETADO")
print("=" * 80)