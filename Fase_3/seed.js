import sql from "mssql";
import fs from "fs";
import { pool } from "./config/mssql.js";
import { printJSON, client, db } from "./config/mongo.js";

function limpiarString(texto) {
    if (!texto) return null;
    if (typeof texto === 'string') {
        texto = texto.replace(/\r/g, '').replace(/\n/g, '').trim();
        return texto || null;
    }
    return texto;
}

function limpiarJson(data) {
    if (data === null || data === undefined) return null;
    
    if (Array.isArray(data)) {
        const cleaned = [];
        for (const item of data) {
            const cleanedItem = limpiarJson(item);
            if (cleanedItem !== null && cleanedItem !== undefined && 
                (typeof cleanedItem !== 'object' || Object.keys(cleanedItem).length > 0)) {
                cleaned.push(cleanedItem);
            }
        }
        return cleaned;
    }
    
    if (typeof data === 'object') {
        const cleaned = {};
        for (const [key, value] of Object.entries(data)) {
            if (value !== null && value !== undefined && value !== '') {
                const cleanedKey = limpiarString(key) || key;
                const cleanedValue = limpiarJson(value);
                if (cleanedValue !== null && cleanedValue !== undefined &&
                    (typeof cleanedValue !== 'object' || Object.keys(cleanedValue).length > 0)) {
                    cleaned[cleanedKey] = cleanedValue;
                }
            }
        }
        return cleaned;
    }
    
    if (typeof data === 'string') {
        return limpiarString(data);
    }
    
    return data;
}

async function executeStoredProcedure(spName, params) {
    try {
        const request = pool.request();
        params.forEach((param, index) => {
            request.input(`p${index}`, param);
        });
        const paramNames = params.map((_, index) => `@p${index}`).join(', ');
        const query = `EXEC ${spName} ${paramNames}`;
        const result = await request.query(query);
        return result.recordset || [];
    } catch (err) {
        console.error(`Error en SP ${spName}:`, err.message);
        return [];
    }
}

async function obtenerPlantelesConJugadores(anio) {
    try {
        const plantelesRaw = await executeStoredProcedure('sp_info_mundial', [anio, 'grupos y planteles', null, null, null]);
        
        if (!plantelesRaw || plantelesRaw.length === 0) {
            return [];
        }
        
        const paisesDict = {};
        
        for (const p of plantelesRaw) {
            const pais = p.pais;
            if (pais && !paisesDict[pais]) {
                paisesDict[pais] = {
                    pais: limpiarString(pais),
                    grupo: limpiarString(p.grupo),
                    jugadores: []
                };
            }
        }
        
        for (const paisOriginal of Object.keys(paisesDict)) {
            const jugadoresRaw = await executeStoredProcedure('sp_info_pais', [paisOriginal, 'planteles', null, anio]);
            
            for (const j of jugadoresRaw) {
                if (j.jugador) {
                    const jugadorData = { jugador: limpiarString(j.jugador) };
                    if (j.num_camisa) {
                        jugadorData.num_camisa = parseInt(j.num_camisa);
                    }
                    if (j.posicion) {
                        jugadorData.posicion = limpiarString(j.posicion);
                    }
                    paisesDict[paisOriginal].jugadores.push(jugadorData);
                }
            }
        }
        
        return Object.values(paisesDict);
        
    } catch (err) {
        console.error(`Error obteniendo planteles para ${anio}:`, err.message);
        return [];
    }
}

async function obtenerPartidos(anio) {
    try {
        const calendario = await executeStoredProcedure('sp_info_mundial', [anio, 'calendario', null, null, null]);
        
        if (!calendario || calendario.length === 0) {
            return [];
        }
        
        const partidos = [];
        
        for (let idx = 0; idx < calendario.length; idx++) {
            const partido = calendario[idx];
            
            // Crear estructura del partido con los atributos del calendario
            const partidoData = {
                fecha: partido.fecha instanceof Date ? partido.fecha.toISOString().split('T')[0] : partido.fecha,
                tipo_fase: limpiarString(partido.etapa || ''),
                puntaje_e1: partido.puntaje_e1 || null,
                puntaje_e2: partido.puntaje_e2 || null,
                hubo_t_extra: false,
                hubo_penales: false,
                equipo1: { pais: limpiarString(partido.Pais_1) },
                equipo2: { pais: limpiarString(partido.Pais_2) }
            };
            
            let idPartido = partido.id_partido;
            if (!idPartido && partido.Pais_1 && partido.Pais_2 && partido.fecha) {
                try {
                    const request = pool.request();
                    request.input('anio', anio);
                    request.input('pais1', partido.Pais_1);
                    request.input('pais2', partido.Pais_2);
                    request.input('fecha', partido.fecha);
                    const queryId = `
                        SELECT TOP 1 p.id_partido
                        FROM partido p
                        INNER JOIN plantel pl1 ON pl1.id_plantel = p.id_plantel_e1
                        INNER JOIN plantel pl2 ON pl2.id_plantel = p.id_plantel_e2
                        INNER JOIN pais pa1 ON pa1.id_pais = pl1.id_pais
                        INNER JOIN pais pa2 ON pa2.id_pais = pl2.id_pais
                        INNER JOIN mundial m ON m.id_mundial = p.id_mundial
                        WHERE m.anio = @anio 
                          AND LOWER(pa1.nombre) = LOWER(@pais1)
                          AND LOWER(pa2.nombre) = LOWER(@pais2)
                          AND CAST(p.fecha AS DATE) = CAST(@fecha AS DATE)
                    `;
                    const result = await request.query(queryId);
                    idPartido = result.recordset.length > 0 ? result.recordset[0].id_partido : null;
                } catch (err) {}
            }
            
            if (idPartido) {
                // Goles
                const goles = await executeStoredProcedure('sp_info_partido', [idPartido, 'goles']);
                for (const gol of goles) {
                    const paisGol = limpiarString(gol.pais);
                    const golData = {
                        jugador: limpiarString(gol.jugador),
                        min_marcado: limpiarString(gol.min_marcado)
                    };
                    if (paisGol === partidoData.equipo1.pais) {
                        if (!partidoData.equipo1.goles) partidoData.equipo1.goles = [];
                        partidoData.equipo1.goles.push(golData);
                    } else if (paisGol === partidoData.equipo2.pais) {
                        if (!partidoData.equipo2.goles) partidoData.equipo2.goles = [];
                        partidoData.equipo2.goles.push(golData);
                    }
                }
                
                // Tarjetas
                const tarjetas = await executeStoredProcedure('sp_info_partido', [idPartido, 'tarjetas']);
                for (const tarjeta of tarjetas) {
                    const paisTarjeta = limpiarString(tarjeta.pais);
                    const tarjetaData = {
                        jugador: limpiarString(tarjeta.jugador),
                        tipo_tarjeta: limpiarString(tarjeta.tipo_tarjeta),
                        min_tarjeta: tarjeta.min_tarjeta
                    };
                    if (paisTarjeta === partidoData.equipo1.pais) {
                        if (!partidoData.equipo1.tarjetas) partidoData.equipo1.tarjetas = [];
                        partidoData.equipo1.tarjetas.push(tarjetaData);
                    } else if (paisTarjeta === partidoData.equipo2.pais) {
                        if (!partidoData.equipo2.tarjetas) partidoData.equipo2.tarjetas = [];
                        partidoData.equipo2.tarjetas.push(tarjetaData);
                    }
                }
                
                // Cambios
                const cambios = await executeStoredProcedure('sp_info_partido', [idPartido, 'cambios']);
                for (const cambio of cambios) {
                    const paisCambio = limpiarString(cambio.pais);
                    const cambioData = {
                        entra: limpiarString(cambio.entra),
                        sale: limpiarString(cambio.sale),
                        minuto_cambio: cambio.minuto_cambio
                    };
                    if (cambio.ET === 1) cambioData.et = true;
                    
                    if (paisCambio === partidoData.equipo1.pais) {
                        if (!partidoData.equipo1.cambios) partidoData.equipo1.cambios = [];
                        partidoData.equipo1.cambios.push(cambioData);
                    } else if (paisCambio === partidoData.equipo2.pais) {
                        if (!partidoData.equipo2.cambios) partidoData.equipo2.cambios = [];
                        partidoData.equipo2.cambios.push(cambioData);
                    }
                }
                
                // Penales (corregido: penales en lugar de penaless)
                const penales = await executeStoredProcedure('sp_info_partido', [idPartido, 'penales']);
                for (const penal of penales) {
                    const paisPenal = limpiarString(penal.pais);
                    const penalData = {
                        jugador: limpiarString(penal.jugador),
                        fue_metido: limpiarString(penal.fue_metido)
                    };
                    if (paisPenal === partidoData.equipo1.pais) {
                        if (!partidoData.equipo1.penales) partidoData.equipo1.penales = [];
                        partidoData.equipo1.penales.push(penalData);
                    } else if (paisPenal === partidoData.equipo2.pais) {
                        if (!partidoData.equipo2.penales) partidoData.equipo2.penales = [];
                        partidoData.equipo2.penales.push(penalData);
                    }
                }
                
                // Asistencias (jugadores que participaron en el partido)
                const jugadores = await executeStoredProcedure('sp_info_partido', [idPartido, 'jugadores']);
                for (const jug of jugadores) {
                    const paisJug = limpiarString(jug.pais);
                    const asistencia = {
                        jugador: limpiarString(jug.jugador),
                        posicion: limpiarString(jug.posicion),
                        num_camisa: jug.num_camisa,
                        estado: limpiarString(jug.estado)
                    };
                    if (jug.capitan === 1) asistencia.capitan = true;
                    
                    if (paisJug === partidoData.equipo1.pais) {
                        if (!partidoData.equipo1.asistencias) partidoData.equipo1.asistencias = [];
                        partidoData.equipo1.asistencias.push(asistencia);
                    } else if (paisJug === partidoData.equipo2.pais) {
                        if (!partidoData.equipo2.asistencias) partidoData.equipo2.asistencias = [];
                        partidoData.equipo2.asistencias.push(asistencia);
                    }
                }
            }
            
            partidos.push(partidoData);
        }
        
        return partidos;
        
    } catch (err) {
        console.error(`Error obteniendo partidos para ${anio}:`, err.message);
        return [];
    }
}

async function extraerMundial(anio) {
    console.log(`\nExtrayendo datos del Mundial ${anio}...`);
    console.log("=".repeat(50));
    
    console.log("\nPASO 1: Obteniendo planteles...");
    const planteles = await obtenerPlantelesConJugadores(anio);
    console.log(`\n  Total equipos procesados: ${planteles.length}`);
    
    console.log("\nPASO 2: Obteniendo TODOS los partidos...");
    const partidos = await obtenerPartidos(anio);
    console.log(`\n  Procesados ${partidos.length} partidos exitosamente!`);
    
    const mundialData = {
        anio: anio,
        planteles: planteles,
        partidos: partidos
    };
    
    console.log("\nLimpiando JSON...");
    return limpiarJson(mundialData);
}

async function extraerMetricasMundial(anio) {
    const metricasData = {
        anio: anio,
        common_info: {
            campeon: null,
            organizador: null,
            selecciones: 0,
            partidos: 0,
            goles: 0
        },
        fase_final: [],
        goleadores: [],
        posiciones_finales: [],
        grupos_y_planteles: [],
        premios: []
    };
    
    try {
        const commonInfo = await executeStoredProcedure('sp_info_mundial', [anio, 'common info', null, null, null]);
        if (commonInfo && commonInfo.length > 0) {
            const info = commonInfo[0];
            metricasData.common_info = {
                campeon: limpiarString(info.campeon),
                organizador: limpiarString(info.organizador),
                selecciones: info.selecciones || 0,
                partidos: info.partidos || 0,
                goles: info.goles || 0
            };
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener common info para ${anio}`);
    }
    
    try {
        const faseFinal = await executeStoredProcedure('sp_info_mundial', [anio, 'fase final', null, null, null]);
        if (faseFinal && faseFinal.length > 0) {
            for (const ff of faseFinal) {
                metricasData.fase_final.push({
                    Pais_1: limpiarString(ff.Pais_1),
                    puntaje_e1: limpiarString(ff.puntaje_e1),
                    puntaje_e2: limpiarString(ff.puntaje_e2),
                    Pais_2: limpiarString(ff.Pais_2),
                    tipo_fase: limpiarString(ff.tipo_fase),
                    fecha: ff.fecha instanceof Date ? ff.fecha.toISOString().split('T')[0] : ff.fecha
                });
            }
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener fase final para ${anio}`);
    }
    
    try {
        const goleadores = await executeStoredProcedure('sp_info_mundial', [anio, 'goleadores', null, null, null]);
        if (goleadores && goleadores.length > 0) {
            for (const g of goleadores) {
                metricasData.goleadores.push({
                    jugador: limpiarString(g.jugador),
                    goles: g.goles || 0,
                    partidos: g.partidos || 0,
                    promedio_gol: g.promedio_gol ? parseFloat(g.promedio_gol).toFixed(2) : 0,
                    pais: limpiarString(g.pais)
                });
            }
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener goleadores para ${anio}`);
    }
    
    try {
        const posiciones = await executeStoredProcedure('sp_info_mundial', [anio, 'posiciones finales', null, null, null]);
        if (posiciones && posiciones.length > 0) {
            for (const p of posiciones) {
                metricasData.posiciones_finales.push({
                    pais: limpiarString(p.pais),
                    tipo_fase: limpiarString(p.tipo_fase),
                    PTS: p.PTS || 0,
                    PJ: p.PJ || 0,
                    PG: p.PG || 0,
                    PE: p.PE || 0,
                    PP: p.PP || 0,
                    GF: p.GF || 0,
                    GC: p.GC || 0,
                    Dif: p.Dif || 0
                });
            }
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener posiciones finales para ${anio}`);
    }
    
    try {
        const grupos = await executeStoredProcedure('sp_info_mundial', [anio, 'grupos y planteles', null, null, null]);
        if (grupos && grupos.length > 0) {
            for (const g of grupos) {
                metricasData.grupos_y_planteles.push({
                    pais: limpiarString(g.pais),
                    grupo: limpiarString(g.grupo),
                    PTS: g.PTS || 0,
                    PJ: g.PJ || 0,
                    PG: g.PG || 0,
                    PE: g.PE || 0,
                    PP: g.PP || 0,
                    GF: g.GF || 0,
                    GC: g.GC || 0,
                    Dif: g.Dif || 0
                });
            }
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener grupos y planteles para ${anio}`);
    }
    
    try {
        const premios = await executeStoredProcedure('sp_info_mundial', [anio, 'premios', null, null, null]);
        if (premios && premios.length > 0) {
            for (const pr of premios) {
                const premioData = {
                    premio: limpiarString(pr.premio)
                };
                if (pr.jugador) premioData.jugador = limpiarString(pr.jugador);
                if (pr.pais) premioData.pais = limpiarString(pr.pais);
                metricasData.premios.push(premioData);
            }
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener premios para ${anio}`);
    }
    
    try {
        const equipoIdeal = await executeStoredProcedure('sp_info_mundial', [anio, 'equipo ideal', null, null, null]);
        if (equipoIdeal && equipoIdeal.length > 0) {
            metricasData.equipo_ideal = [];
            for (const eq of equipoIdeal) {
                metricasData.equipo_ideal.push({
                    jugador: limpiarString(eq.jugador),
                    posicion: limpiarString(eq.posicion),
                    pais: limpiarString(eq.pais)
                });
            }
        }
    } catch (err) {
        console.log(`  Advertencia: No se pudo obtener equipo ideal para ${anio}`);
    }
    
    return metricasData;
}

async function coleccion_mundial() {
    try {
        const mundiales = [
            2022, 2018, 2014, 2010, 2006, 2002, 1998, 1994, 1990,
            1986, 1982, 1978, 1974, 1970, 1966, 1962, 1958, 1954,
            1950, 1938, 1934, 1930
        ];
        
        const collection = db.collection("mundiales");
        
        for (const anio of mundiales) {
            console.log("\n" + "=".repeat(60));
            console.log(`PROCESANDO MUNDIAL ${anio}`);
            console.log("=".repeat(60));
            
            try {
                const mundialData = await extraerMundial(anio);
                
                if (mundialData.planteles.length > 0) {
                    const result = await collection.insertOne(mundialData);
                    console.log(`\nMundial ${anio} guardado en MongoDB con ID: ${result.insertedId}`);
                    
                    const totalJugadores = mundialData.planteles.reduce((sum, equipo) => 
                        sum + (equipo.jugadores ? equipo.jugadores.length : 0), 0);
                    console.log(`Resumen ${anio}:`);
                    console.log(`  Equipos: ${mundialData.planteles.length}`);
                    console.log(`  Jugadores: ${totalJugadores}`);
                    console.log(`  Partidos: ${mundialData.partidos.length}`);
                } else {
                    console.log(`\nMundial ${anio} no tiene datos, omitiendo insercion`);
                }
                
            } catch (err) {
                console.error(`Error procesando mundial ${anio}:`, err.message);
            }
        }
        
        console.log("\n" + "=".repeat(60));
        console.log("TODOS LOS MUNDIALES PROCESADOS EXITOSAMENTE");
        console.log("=".repeat(60));
        
    } catch (err) {
        console.error("Error intentando llenar la coleccion del mundial:", err);
        throw err;
    }
}

async function coleccion_metricas_mundial() {
    try {
        const mundiales = [
            2022, 2018, 2014, 2010, 2006, 2002, 1998, 1994, 1990,
            1986, 1982, 1978, 1974, 1970, 1966, 1962, 1958, 1954,
            1950, 1938, 1934, 1930
        ];
        
        const collection = db.collection("mundial_metricas");
        
        console.log("\n" + "=".repeat(60));
        console.log("INICIANDO EXTRACCION DE METRICAS");
        console.log("=".repeat(60));
        
        for (const anio of mundiales) {
            console.log(`\nProcesando metricas del mundial ${anio}...`);
            
            try {
                const metricasData = await extraerMetricasMundial(anio);
                const metricasLimpio = limpiarJson(metricasData);
                
                if (!metricasLimpio) {
                    console.log(`  -> Mundial ${anio} no tiene datos validos`);
                    continue;
                }
                
                const result = await collection.updateOne(
                    { anio: anio },
                    { $set: metricasLimpio },
                    { upsert: true }
                );
                
                if (result.upsertedId) {
                    console.log(`  -> Mundial ${anio} metricas insertadas (ID: ${result.upsertedId})`);
                } else if (result.modifiedCount > 0) {
                    console.log(`  -> Mundial ${anio} metricas actualizadas`);
                } else {
                    console.log(`  -> Mundial ${anio} metricas ya existian`);
                }
                
                const campeon = metricasLimpio.common_info?.campeon || 'No disponible';
                const goleador = metricasLimpio.goleadores && metricasLimpio.goleadores.length > 0 
                    ? `${metricasLimpio.goleadores[0].jugador} (${metricasLimpio.goleadores[0].goles} goles)` 
                    : 'No disponible';
                const faseFinalCount = metricasLimpio.fase_final?.length || 0;
                const premiosCount = metricasLimpio.premios?.length || 0;
                
                console.log(`     - Campeon: ${campeon}`);
                console.log(`     - Goleador: ${goleador}`);
                console.log(`     - Partidos fase final: ${faseFinalCount}`);
                console.log(`     - Premios: ${premiosCount}`);
                
            } catch (err) {
                console.error(`  Error en mundial ${anio}:`, err.message);
            }
        }
        
        console.log("\n" + "=".repeat(60));
        console.log("EXTRACCION DE METRICAS COMPLETADA");
        console.log("=".repeat(60));
        
    } catch (err) {
        console.error("Error intentando llenar la coleccion metricas_mundial:", err);
    }
}

async function coleccion_paises() {
    try {
        const paisesResult = await pool.request().query("SELECT nombre FROM pais");
        const paises_a_procesar = paisesResult.recordset.map(row => row.nombre);

        const allPaisesData = [];

        for (const nombre_pais of paises_a_procesar) {
            try {
                const infoPaisResult = await pool.request()
                    .input('pais', sql.VarChar, nombre_pais)
                    .input('tipo_info', sql.VarChar, 'all')
                    .execute('sp_info_pais');

                const tablaCommonInfo = infoPaisResult.recordsets[0] || [];
                const tablaPlanteles = infoPaisResult.recordsets[1] || [];
                const tablaMundialPorMundial = infoPaisResult.recordsets[2] || [];
                const tablaPartidos = infoPaisResult.recordsets[3] || [];
                const tablaGoleadores = infoPaisResult.recordsets[4] || [];

                let common_info = {};
                if (tablaCommonInfo.length > 0) {
                    const raw = tablaCommonInfo[0];
                    
                    const parseAnios = (str) => {
                        if (!str) return [];
                        return str.toString().split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
                    };

                    common_info = {
                        cant_mundiales: raw.cant_mundiales,
                        campeon: parseAnios(raw.campeon),
                        subcampeon: parseAnios(raw.subcampeon),
                        partidos_jugados: raw.partidos_jugados,
                        partidos_ganados: raw.partidos_ganados,
                        partidos_empatados: raw.partidos_empatados,
                        partidos_perdidos: raw.partidos_perdidos,
                        goles_favor: raw.goles_favor,
                        goles_contra: raw.goles_contra,
                        Dif: raw.Dif,
                        prom_favor: raw.prom_favor || 0,
                        prom_contra: raw.prom_contra || 0,
                        prom_dif: raw.prom_dif || 0,
                        sede: parseAnios(raw.sede)
                    };
                }

                const plantelesMap = new Map();
                for (const row of tablaPlanteles) {
                    const anio = row.anio;
                    if (!plantelesMap.has(anio)) {
                        plantelesMap.set(anio, { mundial: anio, equipo: [] });
                    }
                    
                    const jugadorObj = {
                        jugador: row.jugador,
                        posicion: row.posicion ? row.posicion.toString().trim() : row.posicion
                    };
                    if (row.num_camisa !== null && row.num_camisa !== undefined) {
                        jugadorObj.num_camisa = row.num_camisa;
                    }
                    plantelesMap.get(anio).equipo.push(jugadorObj);
                }
                const planteles = Array.from(plantelesMap.values());

                const jugadoresBonitoResult = await pool.request()
                    .input('pais_jugador', sql.VarChar, nombre_pais)
                    .query("SELECT * FROM jugadores_bonito WHERE pais = @pais_jugador");
                
                const jugadores = (jugadoresBonitoResult.recordset || []).map(row => {
                    const j = {
                        referencia: row.referencia,
                        nombre: row.nombre
                    };
                    if (row.cumpleanios != null && row.cumpleanios !== '[NULL]') {
                        j.cumpleanios = row.cumpleanios instanceof Date ? row.cumpleanios.toISOString().split('T')[0] : row.cumpleanios;
                    }
                    if (row.height != null && row.height !== '[NULL]') j.height = row.height;
                    if (row.lugar_nacimiento != null && row.lugar_nacimiento !== '[NULL]') j.lugar_nacimiento = row.lugar_nacimiento;
                    if (row.apodos != null && row.apodos !== '[NULL]') j.apodos = row.apodos;
                    if (row.sitio_web != null && row.sitio_web !== '[NULL]') j.sitio_web = row.sitio_web;
                    if (row.ig != null && row.ig !== '[NULL]') j.ig = row.ig;
                    if (row.face != null && row.face !== '[NULL]') j.face = row.face;
                    if (row.yt != null && row.yt !== '[NULL]') j.yt = row.yt;
                    if (row.twitter != null && row.twitter !== '[NULL]') j.twitter = row.twitter;
                    if (row.tiktok != null && row.tiktok !== '[NULL]') j.tiktok = row.tiktok;
                    return j;
                });

                const partidos = tablaPartidos.map(p => ({
                    anio: p.anio,
                    fecha: p.fecha ? p.fecha.toISOString().split('T')[0] : null,
                    etapa: p.etapa,
                    Pais_1: p.Pais_1,
                    Pais_2: p.Pais_2,
                    puntaje_e1: p.puntaje_e1 !== undefined ? p.puntaje_e1 : null,
                    puntaje_e2: p.puntaje_e2 !== undefined ? p.puntaje_e2 : null,
                    id_partido: p.id_partido
                }));

                const goleadores = tablaGoleadores.map(g => ({
                    jugador: g.jugador,
                    goles: g.goles,
                    prom_gol: g.prom_gol,
                    partidos: g.partidos,
                    mundiales: g.mundiales
                }));

                const paisDoc = {
                    pais: nombre_pais,
                    common_info: common_info,
                    planteles: planteles,
                    jugadores: jugadores,
                    partidos: partidos,
                    goleadores: goleadores
                };
                
                allPaisesData.push(paisDoc);

                const collection = db.collection('paises');
                await collection.replaceOne({ pais: nombre_pais }, paisDoc, { upsert: true });
                console.log(`Coleccion de paises actualizada para ${nombre_pais}`);
            } catch (innerErr) {
                console.error(`Error procesando pais ${nombre_pais}:`, innerErr.message);
            }
        }

        fs.writeFileSync("./data/paises_data.json", JSON.stringify(allPaisesData, null, 2));
        console.log("Informacion exportada a paises_data.json");
    } catch (err) {
        console.error('Error general intentando llenar la coleccion de paises:', err);
    }
}

async function main() {
    console.log("=".repeat(60));
    console.log("MIGRACION MUNDIALES SQL DOCKER -> MONGODB");
    console.log("=".repeat(60));
    
    try {
        await coleccion_mundial();
        await coleccion_metricas_mundial();
        await coleccion_paises();
    } catch (err) {
        console.error("Error en main:", err);
    } finally {
        await pool.close();
        await client.close();
        console.log("\nConexiones cerradas correctamente");
    }
}

main();