import { client, db, printJSON } from "./config/mongo.js";

const args = process.argv.slice(2);
let anio_mundial = args[0];
const tipo_info = args[1];
let grupo;
let pais;
let fecha;

async function main() {
	try {
		checkParams();
		switch (tipo_info) {
			case "common_info":
				await get_common_info(db);
				break;
			case "posiciones_finales":
				await get_posiciones_finales(db);
				break;
			case "fase_final":
				await get_fase_final(db);
				break;
			case "goleadores":
				await get_goleadores(db);
				break;
			case "grupos_y_planteles":
				await get_grupos_y_planteles(db);
				break;
			case "calendario":
				await get_calendario(db);
				break;
			case "premios":
				await get_premios(db);
				break;
			case "equipo_ideal":
				await get_equipo_ideal(db);
				break;

			default:
				console.log("Solo se aceptan las siguientes opciones:");
				console.log("common_info");
				console.log("posiciones_finales");
				console.log("fase_final");
				console.log("goleadores");
				console.log("grupos_y_planteles");
				console.log("calendario");
				console.log("premios");
				console.log("equipo_ideal");
				break;
		}
	} catch (error) {
		console.error(error);
	}

	await client.close();
}

async function get_common_info(db) {
	const res = await db
		.collection("mundial_metricas")
		.find({ anio: anio_mundial }, { projection: { common_info: 1, _id: 0 } })
		.toArray();
	printJSON(res);
	return;
}

async function get_posiciones_finales(db) {
	let tmp = [{ $match: { anio: anio_mundial } }];
	if (pais) {
		tmp.push(
			{ $unwind: "$posiciones_finales" },
			{ $match: { "posiciones_finales.pais": pais } },
		);
	}
	tmp.push({ $project: { posiciones_finales: 1, _id: 0 } });
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}
async function get_fase_final(db) {
	let tmp = [{ $match: { anio: anio_mundial } }];
	if (pais || fecha) {
		tmp.push({ $unwind: "$fase_final" });
	}
	if (pais) {
		tmp.push({
			$match: {
				$or: [{ "fase_final.Pais_1": pais }, { "fase_final.Pais_2": pais }],
			},
		});
	}
	if (fecha) {
		tmp.push({ $match: { "fase_final.fecha": fecha } });
	}
	tmp.push({ $project: { fase_final: 1, _id: 0 } });
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}
async function get_goleadores(db) {
	let tmp = [
		{ $match: { anio: anio_mundial } },
		{ $project: { goleadores: 1, _id: 0 } },
	];
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}
async function get_grupos_y_planteles(db) {
	let tmp = [{ $match: { anio: anio_mundial } }];
	if (grupo || pais) {
		tmp.push({ $unwind: "$grupos_y_planteles" });
	}
	if (grupo) {
		tmp.push({ $match: { "grupos_y_planteles.grupo": grupo } });
	}
	if (pais) {
		tmp.push({ $match: { "grupos_y_planteles.pais": pais } });
	}
	tmp.push({ $project: { grupos_y_planteles: 1, _id: 0 } });
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}
async function get_calendario(db) {
	let tmp = [{ $match: { anio: anio_mundial } }];
	if (fecha || pais) {
		tmp.push({ $unwind: "$partidos" });
	}
	if (pais) {
		tmp.push({
			$match: {
				$or: [
					{ "partidos.equipo1.pais": pais },
					{ "partidos.equipo2.pais": pais },
				],
			},
		});
	}
	if (fecha) {
		tmp.push({ $match: { "partidos.fecha": fecha } });
	}
	tmp.push({
		$project: {
			"partidos.fecha": 1,
			"partidos.tipo_fase": 1,
			"partidos.hubo_t_extra": 1,
			"partidos.hubo_penales": 1,
			"partidos.equipo1.pais": 1,
			"partidos.equipo2.pais": 1,
			"partidos.puntaje_e1": 1,
			"partidos.puntaje_e2": 1,
			_id: 0,
		},
	});
	const res = await db.collection("mundiales").aggregate(tmp).toArray();
	printJSON(res);
	return;
}
async function get_premios(db) {
	let tmp = [{ $match: { anio: anio_mundial } }];
	if (pais) {
		tmp.push({ $unwind: "$premios" }, { $match: { "premios.pais": pais } });
	}
	tmp.push({ $project: { premios: 1, _id: 0 } });
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}
async function get_equipo_ideal(db) {
	let tmp = [{ $match: { anio: anio_mundial } }];
	if (pais) {
		tmp.push(
			{ $unwind: "$equipo_ideal" },
			{ $match: { "equipo_ideal.pais": pais } },
		);
	}
	tmp.push({ $project: { equipo_ideal: 1, _id: 0 } });
	const res = await db.collection("mundial_metricas").aggregate(tmp).toArray();
	printJSON(res);
	return;
}

function checkParams() {
	if (!anio_mundial || !tipo_info) {
		throw new Error("anio_mundial y tipo_info requerido..");
	}
	anio_mundial = Number(anio_mundial);
	for (let i = 2; i < args.length; i++) {
		const tmp = args[i].split("=");
		switch (tmp[0]) {
			case "grupo":
				grupo = tmp[1].replace(/"/g, "");
				break;
			case "pais":
				pais = tmp[1].replace(/"/g, "");
				break;
			case "fecha":
				fecha = tmp[1];
				break;
			default:
				throw new Error("Param extra invalido...");
		}
	}
}

main();
