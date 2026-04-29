import { client, db, printJSON } from "./config/mongo.js";

const args = process.argv.slice(2);
const pais = args[0];
const tipo_info = args[1];
let ref_jugador;
let anio;

async function main() {
	try {
		checkParams();
		switch (tipo_info) {
			case "common_info":
				await getCommonInfo();
				break;
			case "planteles":
				await getPlanteles();
				break;
			case "mundial_por_mundial":
				await get_mundial_por_mundial();
				break;
			case "resultados":
				await get_resultados();
				break;
			case "goleadores":
				await get_goleadores();
				break;
			case "personas":
				await get_personas();
				break;
			default:
				console.log("Solo se aceptan las siguientes opciones:");
				console.log("common_info");
				console.log("planteles");
				console.log("mundial_por_mundial");
				console.log("resultados");
				console.log("goleadores");
				console.log("personas");
				break;
		}
	} catch (error) {
		console.error(error);
	}

	await client.close();
}

function checkParams() {
	if (!pais || !tipo_info) {
		throw new Error("pais y tipo_info requerido..");
	}
	for (let i = 2; i < args.length; i++) {
		const tmp = args[i].split("=");
		switch (tmp[0]) {
			case "ref_jugador":
				ref_jugador = tmp[1].replace(/"/g, "");
				break;
			case "anio":
				anio = Number(tmp[1]);
				break;
			default:
				throw new Error("Param extra invalido...");
		}
	}
}

async function getCommonInfo() {
	const res = await db
		.collection("paises")
		.find({ pais: pais }, { projection: { common_info: 1, _id: 0 } })
		.toArray();
	printJSON(res);
	return;
}

async function getPlanteles() {
	let tmp = [{ $match: { pais: pais } }, { $unwind: "$planteles" }];
	if (anio) {
		tmp.push({ $match: { "planteles.mundial": anio } });
	}
	if (ref_jugador) {
		tmp.push(
			{ $unwind: "$planteles.equipo" },
			{ $match: { "planteles.equipo.jugador": ref_jugador } },
		);
	}
	tmp.push({ $project: { planteles: 1, _id: 0 } });
	const res = await db.collection("paises").aggregate(tmp).toArray();
	printJSON(res);
	return;
}

async function get_mundial_por_mundial() {
	let tmp = [
		{ $unwind: "$posiciones_finales" },
		{ $match: { "posiciones_finales.pais": pais } },
		{ $project: { posiciones_finales: 1, _id: 0, anio: 1 } },
	];
	if (anio) {
		tmp.unshift({ $match: { anio: anio } });
	}
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}

async function get_resultados() {
	let tmp = [{ $match: { pais: pais } }];
	if (anio) {
		tmp.push({ $unwind: "$partidos" }, { $match: { "partidos.anio": anio } });
	}
	tmp.push({ $project: { partidos: 1, _id: 0 } });
	const res = await db.collection("paises").aggregate(tmp).toArray();
	printJSON(res);
	return;
}

async function get_goleadores() {
	let tmp = [{ $match: { pais: pais } }];
	if (ref_jugador) {
		tmp.push(
			{ $unwind: "$goleadores" },
			{ $match: { "goleadores.jugador": ref_jugador } },
		);
	}
	tmp.push({ $project: { goleadores: 1, _id: 0 } });
	const res = await db.collection("paises").aggregate(tmp).toArray();
	printJSON(res);
	return;
}

async function get_personas() {
	let tmp = [{ $match: { pais: pais } }];
	if (ref_jugador) {
		tmp.push(
			{ $unwind: "$jugadores" },
			{ $match: { "jugadores.referencia": ref_jugador } },
		);
	}
	tmp.push({ $project: { jugadores: 1, _id: 0 } });
	const res = await db.collection("paises").aggregate(tmp).toArray();
	printJSON(res);
	return;
}

main();
