import { pool } from "./config/mssql.js";
import fs from "fs";

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

async function extraerMetricasMundial(anio) {
    console.log(`\nExtrayendo metricas del Mundial ${anio}...`);
    console.log("=".repeat(50));
    
    const metricasData = {
        anio: anio,
        common_info: {},
        fase_final: [],
        goleadores: [],
        posiciones_finales: [],
        grupos_y_planteles: [],
        premios: [],
        equipo_ideal: []
    };
    
    // 1. Common Info
    console.log("\n1. Obteniendo informacion comun...");
    const commonInfo = await executeStoredProcedure('sp_info_mundial', [anio, 'common info', null, null, null]);
    if (commonInfo.length > 0) {
        const info = commonInfo[0];
        metricasData.common_info = {
            campeon: limpiarString(info.campeon),
            organizador: limpiarString(info.organizador),
            selecciones: info.selecciones,
            partidos: info.partidos,
            goles: info.goles
        };
        console.log(`   Campeon: ${metricasData.common_info.campeon}`);
        console.log(`   Organizador: ${metricasData.common_info.organizador}`);
        console.log(`   Selecciones: ${metricasData.common_info.selecciones}`);
        console.log(`   Partidos: ${metricasData.common_info.partidos}`);
        console.log(`   Goles: ${metricasData.common_info.goles}`);
    }
    
    // 2. Fase Final
    console.log("\n2. Obteniendo fase final...");
    const faseFinal = await executeStoredProcedure('sp_info_mundial', [anio, 'fase final', null, null, null]);
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
    console.log(`   Partidos de fase final: ${metricasData.fase_final.length}`);
    
    // 3. Goleadores
    console.log("\n3. Obteniendo goleadores...");
    const goleadores = await executeStoredProcedure('sp_info_mundial', [anio, 'goleadores', null, null, null]);
    for (const g of goleadores) {
        metricasData.goleadores.push({
            jugador: limpiarString(g.jugador),
            goles: g.goles,
            partidos: g.partidos,
            promedio_gol: parseFloat(g.promedio_gol).toFixed(2),
            pais: limpiarString(g.pais)
        });
    }
    console.log(`   Goleadores registrados: ${metricasData.goleadores.length}`);
    if (metricasData.goleadores.length > 0) {
        console.log(`   Maximo goleador: ${metricasData.goleadores[0].jugador} (${metricasData.goleadores[0].goles} goles)`);
    }
    
    // 4. Posiciones Finales
    console.log("\n4. Obteniendo posiciones finales...");
    const posiciones = await executeStoredProcedure('sp_info_mundial', [anio, 'posiciones finales', null, null, null]);
    for (const p of posiciones) {
        metricasData.posiciones_finales.push({
            pais: limpiarString(p.pais),
            tipo_fase: limpiarString(p.tipo_fase),
            PTS: p.PTS,
            PJ: p.PJ,
            PG: p.PG,
            PE: p.PE,
            PP: p.PP,
            GF: p.GF,
            GC: p.GC,
            Dif: p.Dif
        });
    }
    console.log(`   Equipos en posiciones: ${metricasData.posiciones_finales.length}`);
    
    // 5. Grupos y Planteles
    console.log("\n5. Obteniendo grupos y planteles...");
    const grupos = await executeStoredProcedure('sp_info_mundial', [anio, 'grupos y planteles', null, null, null]);
    for (const g of grupos) {
        metricasData.grupos_y_planteles.push({
            pais: limpiarString(g.pais),
            grupo: limpiarString(g.grupo),
            PTS: g.PTS,
            PJ: g.PJ,
            PG: g.PG,
            PE: g.PE,
            PP: g.PP,
            GF: g.GF,
            GC: g.GC,
            Dif: g.Dif
        });
    }
    console.log(`   Equipos en grupos: ${metricasData.grupos_y_planteles.length}`);
    
    // 6. Premios
    console.log("\n6. Obteniendo premios...");
    const premios = await executeStoredProcedure('sp_info_mundial', [anio, 'premios', null, null, null]);
    for (const pr of premios) {
        const premioData = {
            premio: limpiarString(pr.premio)
        };
        if (pr.jugador) premioData.jugador = limpiarString(pr.jugador);
        if (pr.pais) premioData.pais = limpiarString(pr.pais);
        metricasData.premios.push(premioData);
    }
    console.log(`   Premios otorgados: ${metricasData.premios.length}`);
    
    // 7. Equipo Ideal (solo si hay datos)
    console.log("\n7. Obteniendo equipo ideal...");
    const equipoIdeal = await executeStoredProcedure('sp_info_mundial', [anio, 'equipo ideal', null, null, null]);
    if (equipoIdeal && equipoIdeal.length > 0) {
        for (const eq of equipoIdeal) {
            metricasData.equipo_ideal.push({
                jugador: limpiarString(eq.jugador),
                posicion: limpiarString(eq.posicion),
                pais: limpiarString(eq.pais)
            });
        }
        console.log(`   Equipo ideal: ${metricasData.equipo_ideal.length} jugadores`);
    } else {
        console.log(`   No hay equipo ideal para este mundial`);
        // No agregamos la propiedad si no hay datos
        delete metricasData.equipo_ideal;
    }
    
    return metricasData;
}

async function main() {
    console.log("=".repeat(60));
    console.log("EXTRACCION DE METRICAS MUNDIAL 2022");
    console.log("=".repeat(60));
    
    try {
        await pool.connect();
        console.log("\nConectado a SQL Server");
        
        const anio = 2022;
        const metricas = await extraerMetricasMundial(anio);
        
        // Limpiar el JSON final
        const metricasLimpio = limpiarJson(metricas);
        
        // Guardar a archivo JSON
        fs.writeFileSync(`mundial_${anio}_metricas.json`, JSON.stringify(metricasLimpio, null, 2));
        console.log(`\n✅ Datos guardados en mundial_${anio}_metricas.json`);
        
        // Mostrar resumen
        console.log("\n" + "=".repeat(60));
        console.log("RESUMEN DE METRICAS");
        console.log("=".repeat(60));
        console.log(`Anio: ${metricasLimpio.anio}`);
        console.log(`Campeon: ${metricasLimpio.common_info.campeon}`);
        if (metricasLimpio.goleadores && metricasLimpio.goleadores.length > 0) {
            console.log(`Goleador: ${metricasLimpio.goleadores[0].jugador} (${metricasLimpio.goleadores[0].goles} goles)`);
        }
        console.log(`Partidos fase final: ${metricasLimpio.fase_final.length}`);
        console.log(`Premios: ${metricasLimpio.premios.length}`);
        if (metricasLimpio.equipo_ideal) {
            console.log(`Equipo ideal: ${metricasLimpio.equipo_ideal.length} jugadores`);
        } else {
            console.log(`Equipo ideal: No disponible para este mundial`);
        }
        
        await pool.close();
        
    } catch (err) {
        console.error("Error:", err);
    }
}

main();