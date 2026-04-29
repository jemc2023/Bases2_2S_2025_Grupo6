import pyodbc
import json
from decimal import Decimal
from datetime import date, datetime
import re

# ==================== CONFIGURACIÓN PARA DOCKER ====================
SQL_CONFIG = {
    'server': 'localhost',
    'port': 1433,
    'database': 'MundialDB',
    'username': 'SA',
    'password': 'Mundial.123',
    'driver': '{SQL Server}'
}

def limpiar_string_final(texto):
    """Eliminar \\r, \\n y espacios extras - SOLO para el JSON final"""
    if texto is None:
        return None
    if isinstance(texto, str):
        texto = texto.replace('\r', '').replace('\n', '').strip()
        return texto if texto else None
    return texto

def limpiar_json(data):
    """Limpiar strings y eliminar nulls - SOLO al final del proceso"""
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            if v is not None and v != '' and v != []:
                k_clean = limpiar_string_final(k) if isinstance(k, str) else k
                v_clean = limpiar_json(v)
                if v_clean is not None and v_clean != '' and v_clean != []:
                    cleaned[k_clean] = v_clean
        return cleaned
    elif isinstance(data, list):
        cleaned_list = []
        for item in data:
            if item is not None and item != []:
                item_clean = limpiar_json(item)
                if item_clean is not None and item_clean != []:
                    cleaned_list.append(item_clean)
        return cleaned_list
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    elif isinstance(data, str):
        return limpiar_string_final(data)
    return data

def get_sql_connection():
    """Conectar a SQL Server en Docker"""
    try:
        conn_str = (
            f"DRIVER={SQL_CONFIG['driver']};"
            f"SERVER={SQL_CONFIG['server']},{SQL_CONFIG['port']};"
            f"DATABASE={SQL_CONFIG['database']};"
            f"UID={SQL_CONFIG['username']};"
            f"PWD={SQL_CONFIG['password']}"
        )
        print(f" Conectando a {SQL_CONFIG['server']}:{SQL_CONFIG['port']}...")
        conn = pyodbc.connect(conn_str, timeout=30)
        print(" Conexión exitosa!")
        return conn
    except Exception as e:
        print(f" Error de conexión: {e}")
        raise

def execute_stored_procedure(sp_name, params):
    """Ejecutar SP y retornar todos los resultados (SIN limpiar nada)"""
    conn = get_sql_connection()
    cursor = conn.cursor()
    
    try:
        placeholders = ','.join(['?' for _ in params])
        query = f"EXEC {sp_name} {placeholders}"
        print(f"   Ejecutando: {sp_name}")
        cursor.execute(query, params)
        
        all_results = []
        while True:
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                for row in rows:
                    row_dict = {}
                    for idx, col in enumerate(columns):
                        value = row[idx]
                        if isinstance(value, Decimal):
                            value = float(value)
                        elif isinstance(value, date):
                            value = value.isoformat()
                        # NO limpiar strings aquí, mantener los \r originales
                        row_dict[col] = value
                    all_results.append(row_dict)
            if not cursor.nextset():
                break
        
        print(f"     → {len(all_results)} registros obtenidos")
        return all_results
    except Exception as e:
        print(f"      Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def extraer_mundial_2022():
    """Extraer datos del Mundial 2022 usando los SPs"""
    
    anio = 2022
    print(f"\n Extrayendo datos del Mundial {anio}...")
    print("=" * 50)
    
    mundial_data = {
        "anio": anio,
        "planteles": [],
        "partidos": []
    }
    
    # ==================== PASO 1: PLANTELES ====================
    print("\n PASO 1: Obteniendo planteles...")
    try:
        planteles_raw = execute_stored_procedure('sp_info_mundial', [anio, 'grupos y planteles', None, None, None])
        
        if planteles_raw:
            # Agrupar por país (usando el nombre CON \r incluido para la clave)
            paises_dict = {}
            for p in planteles_raw:
                pais = p['pais']  # Mantener el \r original
                if pais not in paises_dict:
                    paises_dict[pais] = {
                        'pais': pais,
                        'grupo': p.get('grupo'),
                        'jugadores': []
                    }
            
            # Obtener jugadores por país (usando el nombre CON \r para el SP)
            for pais_con_r in paises_dict.keys():
                print(f"    Obteniendo jugadores de {pais_con_r}...")
                # Usar el nombre exacto como viene de la BD (con \r)
                jugadores_raw = execute_stored_procedure('sp_info_pais', [pais_con_r, 'planteles', None, anio])
                
                for j in jugadores_raw:
                    if j.get('jugador'):
                        jugador_data = {'jugador': j['jugador']}
                        if j.get('num_camisa'):
                            jugador_data['num_camisa'] = int(j['num_camisa'])
                        if j.get('posicion'):
                            jugador_data['posicion'] = j['posicion']
                        paises_dict[pais_con_r]['jugadores'].append(jugador_data)
                
                print(f"     → {len(paises_dict[pais_con_r]['jugadores'])} jugadores")
            
            mundial_data['planteles'] = list(paises_dict.values())
            print(f"\n   Total equipos procesados: {len(mundial_data['planteles'])}")
        else:
            print("   No se encontraron planteles")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # ==================== PASO 2: TODOS LOS PARTIDOS ====================
    print("\n PASO 2: Obteniendo TODOS los partidos...")
    try:
        calendario = execute_stored_procedure('sp_info_mundial', [anio, 'calendario', None, None, None])
        
        if calendario:
            total_partidos = len(calendario)
            print(f"   Total partidos encontrados: {total_partidos}\n")
            
            for idx, partido in enumerate(calendario, 1):
                print(f"   Partido {idx}/{total_partidos}: {partido.get('Pais_1', '?')} vs {partido.get('Pais_2', '?')}")
                
                # Crear estructura básica del partido
                partido_data = {
                    "fecha": partido['fecha'].isoformat() if isinstance(partido['fecha'], date) else str(partido['fecha']),
                    "tipo_fase": partido.get('etapa', '').split(',')[0],
                    "hubo_t_extra": False,
                    "hubo_penales": False,
                    "equipo1": {"pais": partido.get('Pais_1', '').lower()},
                    "equipo2": {"pais": partido.get('Pais_2', '').lower()}
                }
                
                # Obtener ID del partido
                if 'id_partido' in partido:
                    id_partido = partido['id_partido']
                    
                    # Obtener información del partido (hubo_t_extra, hubo_penales)
                    partido_info = execute_stored_procedure('sp_info_partido', [id_partido, 'all'])
                    for info in partido_info:
                        if 'hubo_t_extra' in info and info['hubo_t_extra'] == 1:
                            partido_data['hubo_t_extra'] = True
                        if 'hubo_penales' in info and info['hubo_penales'] == 1:
                            partido_data['hubo_penales'] = True
                    
                    # Goles
                    goles = execute_stored_procedure('sp_info_partido', [id_partido, 'goles'])
                    for gol in goles:
                        pais_gol = gol['pais'].lower()
                        gol_data = {
                            'jugador': gol['jugador'],
                            'min_marcado': gol['min_marcado']
                        }
                        if pais_gol == partido_data['equipo1']['pais']:
                            if 'goles' not in partido_data['equipo1']:
                                partido_data['equipo1']['goles'] = []
                            partido_data['equipo1']['goles'].append(gol_data)
                        else:
                            if 'goles' not in partido_data['equipo2']:
                                partido_data['equipo2']['goles'] = []
                            partido_data['equipo2']['goles'].append(gol_data)
                    
                    # Tarjetas
                    tarjetas = execute_stored_procedure('sp_info_partido', [id_partido, 'tarjetas'])
                    for tarjeta in tarjetas:
                        pais_tarjeta = tarjeta['pais'].lower()
                        tarjeta_data = {
                            'jugador': tarjeta['jugador'],
                            'tipo_tarjeta': tarjeta['tipo_tarjeta'].lower(),
                            'min_tarjeta': tarjeta['min_tarjeta']
                        }
                        if pais_tarjeta == partido_data['equipo1']['pais']:
                            if 'tarjetas' not in partido_data['equipo1']:
                                partido_data['equipo1']['tarjetas'] = []
                            partido_data['equipo1']['tarjetas'].append(tarjeta_data)
                        else:
                            if 'tarjetas' not in partido_data['equipo2']:
                                partido_data['equipo2']['tarjetas'] = []
                            partido_data['equipo2']['tarjetas'].append(tarjeta_data)
                    
                    # Cambios
                    cambios = execute_stored_procedure('sp_info_partido', [id_partido, 'cambios'])
                    for cambio in cambios:
                        pais_cambio = cambio['pais'].lower()
                        cambio_data = {
                            'entra': cambio['entra'].lower(),
                            'sale': cambio['sale'].lower(),
                            'minuto_cambio': cambio['minuto_cambio']
                        }
                        if cambio.get('ET') == 1:
                            cambio_data['et'] = True
                        
                        if pais_cambio == partido_data['equipo1']['pais']:
                            if 'cambios' not in partido_data['equipo1']:
                                partido_data['equipo1']['cambios'] = []
                            partido_data['equipo1']['cambios'].append(cambio_data)
                        else:
                            if 'cambios' not in partido_data['equipo2']:
                                partido_data['equipo2']['cambios'] = []
                            partido_data['equipo2']['cambios'].append(cambio_data)
                    
                    # Penales
                    penales = execute_stored_procedure('sp_info_partido', [id_partido, 'penales'])
                    for penal in penales:
                        pais_penal = penal['pais'].lower()
                        penal_data = {
                            'jugador': penal['jugador'],
                            'fue_metido': penal['fue_metido']
                        }
                        if pais_penal == partido_data['equipo1']['pais']:
                            if 'penaless' not in partido_data['equipo1']:
                                partido_data['equipo1']['penaless'] = []
                            partido_data['equipo1']['penaless'].append(penal_data)
                        else:
                            if 'penaless' not in partido_data['equipo2']:
                                partido_data['equipo2']['penaless'] = []
                            partido_data['equipo2']['penaless'].append(penal_data)
                    
                    # Jugadores (asistencias)
                    jugadores = execute_stored_procedure('sp_info_partido', [id_partido, 'jugadores'])
                    for jug in jugadores:
                        pais_jug = jug['pais'].lower()
                        asistencia = {
                            'jugador': jug['jugador'],
                            'posicion': jug['posicion'],
                            'num_camisa': jug['num_camisa'],
                            'estado': jug['estado']
                        }
                        if jug.get('capitan', 0) == 1:
                            asistencia['capitan'] = True
                        
                        if pais_jug == partido_data['equipo1']['pais']:
                            if 'asistencias' not in partido_data['equipo1']:
                                partido_data['equipo1']['asistencias'] = []
                            partido_data['equipo1']['asistencias'].append(asistencia)
                        else:
                            if 'asistencias' not in partido_data['equipo2']:
                                partido_data['equipo2']['asistencias'] = []
                            partido_data['equipo2']['asistencias'].append(asistencia)
                
                mundial_data['partidos'].append(partido_data)
            
            print(f"\n   Procesados {len(mundial_data['partidos'])} partidos exitosamente!")
        else:
            print("   No se encontraron partidos")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # ==================== LIMPIAR EL JSON FINAL ====================
    print("\n Limpiando JSON (eliminando \\r y nulls)...")
    mundial_data = limpiar_json(mundial_data)
    
    return mundial_data

# ==================== MAIN ====================
def main():
    print("=" * 60)
    print("🏆 MIGRACIÓN MUNDIAL 2022 - SQL DOCKER → JSON")
    print("=" * 60)
    
    # Verificar conexión primero
    try:
        test_conn = get_sql_connection()
        test_conn.close()
        print("\n Conexión a Docker verificada!")
    except Exception as e:
        print("\n No se pudo conectar a la base de datos")
        return
    
    # Extraer datos
    mundial_2022 = extraer_mundial_2022()
    
    # Guardar a JSON
    output_file = 'mundial_2022_completo.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mundial_2022, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f" ¡ÉXITO! Datos guardados en '{output_file}'")
    print("=" * 60)
    print(f"\n RESUMEN FINAL:")
    print(f"    Año: {mundial_2022.get('anio', 'N/A')}")
    print(f"     Equipos: {len(mundial_2022.get('planteles', []))}")
    
    total_jugadores = sum(len(equipo.get('jugadores', [])) for equipo in mundial_2022.get('planteles', []))
    print(f"    Jugadores totales: {total_jugadores}")
    print(f"    Partidos: {len(mundial_2022.get('partidos', []))}")
    
    print(f"\n Archivo: {output_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()