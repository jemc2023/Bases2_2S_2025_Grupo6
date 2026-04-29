import { client, db } from "./config/mongo.js";

async function verificarMundial(anio) {
    try {
        await client.connect();
        console.log("Conectado a MongoDB\n");
        
        const collection = db.collection("mundiales");
        
        // Buscar el mundial por año
        const mundial = await collection.findOne({ anio: anio });
        
        if (!mundial) {
            console.log(`No se encontro el mundial ${anio}`);
            return;
        }
        
        console.log("=".repeat(60));
        console.log(`MUNDIAL ${mundial.anio}`);
        console.log("=".repeat(60));
        
        // Informacion general
        console.log("\n--- INFORMACION GENERAL ---");
        console.log(`Anio: ${mundial.anio}`);
        console.log(`Equipos: ${mundial.planteles.length}`);
        console.log(`Partidos: ${mundial.partidos.length}`);
        
        // Lista de equipos participantes
        console.log("\n--- EQUIPOS PARTICIPANTES ---");
        for (let i = 0; i < mundial.planteles.length; i++) {
            const equipo = mundial.planteles[i];
            console.log(`${i+1}. ${equipo.pais} (Grupo ${equipo.grupo}) - ${equipo.jugadores.length} jugadores`);
        }
        
        // Mostrar jugadores de un equipo especifico (ejemplo: Argentina)
        console.log("\n--- EJEMPLO: JUGADORES DE ARGENTINA ---");
        const argentina = mundial.planteles.find(e => e.pais.toLowerCase() === 'argentina');
        if (argentina) {
            console.log(`Pais: ${argentina.pais}`);
            console.log(`Grupo: ${argentina.grupo}`);
            console.log(`Jugadores (${argentina.jugadores.length}):`);
            for (let i = 0; i < Math.min(10, argentina.jugadores.length); i++) {
                const j = argentina.jugadores[i];
                console.log(`  ${i+1}. ${j.jugador} - ${j.posicion || 'Sin posicion'} (Camiseta: ${j.num_camisa || 'N/A'})`);
            }
            if (argentina.jugadores.length > 10) {
                console.log(`  ... y ${argentina.jugadores.length - 10} jugadores mas`);
            }
        } else {
            console.log("Argentina no participo en este mundial");
        }
        
        // Mostrar partidos de la fase final
        console.log("\n--- PARTIDOS DE FASE FINAL ---");
        const partidosFinales = mundial.partidos.filter(p => 
            p.tipo_fase !== '1ra Ronda' && p.tipo_fase !== 'Grupo 1' && p.tipo_fase !== 'Grupo 2'
        );
        
        if (partidosFinales.length > 0) {
            for (const p of partidosFinales) {
                const goles1 = p.equipo1.goles ? p.equipo1.goles.length : 0;
                const goles2 = p.equipo2.goles ? p.equipo2.goles.length : 0;
                const penales1 = p.equipo1.penaless ? p.equipo1.penaless.length : 0;
                const penales2 = p.equipo2.penaless ? p.equipo2.penaless.length : 0;
                
                let resultado = `${p.equipo1.pais} ${goles1} - ${goles2} ${p.equipo2.pais}`;
                if (p.hubo_penales && penales1 > 0) {
                    resultado += ` (penales: ${penales1}-${penales2})`;
                }
                if (p.hubo_t_extra) {
                    resultado += ` (Tiempo Extra)`;
                }
                console.log(`  ${p.tipo_fase}: ${resultado}`);
            }
        } else {
            console.log("  No hay partidos de fase final en este mundial");
        }
        
        // Mostrar la final
        console.log("\n--- FINAL DEL MUNDIAL ---");
        const final = mundial.partidos.find(p => p.tipo_fase === 'Final');
        if (final) {
            const goles1 = final.equipo1.goles ? final.equipo1.goles.length : 0;
            const goles2 = final.equipo2.goles ? final.equipo2.goles.length : 0;
            console.log(`  ${final.equipo1.pais} ${goles1} - ${goles2} ${final.equipo2.pais}`);
            
            // Mostrar goleadores de la final
            if (final.equipo1.goles && final.equipo1.goles.length > 0) {
                console.log(`\n  Goles de ${final.equipo1.pais}:`);
                for (const gol of final.equipo1.goles) {
                    console.log(`    - ${gol.jugador} (${gol.min_marcado})`);
                }
            }
            if (final.equipo2.goles && final.equipo2.goles.length > 0) {
                console.log(`\n  Goles de ${final.equipo2.pais}:`);
                for (const gol of final.equipo2.goles) {
                    console.log(`    - ${gol.jugador} (${gol.min_marcado})`);
                }
            }
        } else {
            console.log("  No se encontro la final");
        }
        
        await client.close();
        
    } catch (err) {
        console.error("Error:", err);
    }
}

// Funcion para ver un mundial especifico
async function menu() {
    const args = process.argv.slice(2);
    let anio = args[0];
    
    if (!anio) {
        console.log("Uso: node verificar_mundial.js <anio>");
        console.log("Ejemplo: node verificar_mundial.js 2022");
        console.log("\nMundiales disponibles: 2022, 2018, 2014, 2010, 2006, 2002, 1998, 1994, 1990, 1986, 1982, 1978, 1974, 1970, 1966, 1962, 1958, 1954, 1950, 1938, 1934, 1930");
        return;
    }
    
    await verificarMundial(parseInt(anio));
}

menu();