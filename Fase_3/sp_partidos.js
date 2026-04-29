import { client, db, printJSON } from "./config/mongo.js";

const args = process.argv.slice(2);
let anio = args[0];
const fecha = args[1];
const pais = args[2];
const tipo_info = args[3];

async function main() {
	try {
		checkParams();
		switch (tipo_info) {
			case "goles":
				await get_goles();
				break;
			case "penales":
				await get_penales();
				break;
			case "tarjetas":
				await get_tarjetas();
				break;
			case "cambios":
				await get_cambios();
				break;
			case "asistencias":
				await get_asistencias();
				break;
			default:
				console.log("Solo se aceptan las siguientes opciones:");
				console.log("goles");
				console.log("penales");
				console.log("tarjetas");
				console.log("cambios");
				console.log("asistencias");
				break;
		}
	} catch (error) {
		console.error(error);
	}

	await client.close();
}

function checkParams() {
	if (!anio || !fecha || !pais || !tipo_info) {
		throw new Error("anio, fecha, pais y tipo_info requerido..");
	}
	anio = Number(anio);
}

async function get_goles() {
	const res = await db
		.collection("mundiales")
		.aggregate([
			{ $match: { anio: anio } },
			{ $unwind: "$partidos" },
			{
				$match: {
					$or: [
						{ "partidos.equipo1.pais": pais },
						{ "partidos.equipo2.pais": pais },
					],
				},
			},
			{ $match: { "partidos.fecha": fecha } },
			{
				$project: {
					"partidos.equipo1.pais": 1,
					"partidos.equipo1.goles": 1,
					"partidos.equipo2.pais": 1,
					"partidos.equipo2.goles": 1,
					_id: 0,
				},
			},
		])
		.toArray();
	printJSON(res);
}
async function get_penales() {
	const res = await db
		.collection("mundiales")
		.aggregate([
			{ $match: { anio: anio } },
			{ $unwind: "$partidos" },
			{
				$match: {
					$or: [
						{ "partidos.equipo1.pais": pais },
						{ "partidos.equipo2.pais": pais },
					],
				},
			},
			{ $match: { "partidos.fecha": fecha } },
			{
				$project: {
					"partidos.equipo1.pais": 1,
					"partidos.equipo1.penales": 1,
					"partidos.equipo2.pais": 1,
					"partidos.equipo2.penales": 1,
					_id: 0,
				},
			},
		])
		.toArray();
	printJSON(res);
}
async function get_tarjetas() {
	const res = await db
		.collection("mundiales")
		.aggregate([
			{ $match: { anio: anio } },
			{ $unwind: "$partidos" },
			{
				$match: {
					$or: [
						{ "partidos.equipo1.pais": pais },
						{ "partidos.equipo2.pais": pais },
					],
				},
			},
			{ $match: { "partidos.fecha": fecha } },
			{
				$project: {
					"partidos.equipo1.pais": 1,
					"partidos.equipo1.tarjetas": 1,
					"partidos.equipo2.pais": 1,
					"partidos.equipo2.tarjetas": 1,
					_id: 0,
				},
			},
		])
		.toArray();
	printJSON(res);
}
async function get_cambios() {
	const res = await db
		.collection("mundiales")
		.aggregate([
			{ $match: { anio: anio } },
			{ $unwind: "$partidos" },
			{
				$match: {
					$or: [
						{ "partidos.equipo1.pais": pais },
						{ "partidos.equipo2.pais": pais },
					],
				},
			},
			{ $match: { "partidos.fecha": fecha } },
			{
				$project: {
					"partidos.equipo1.pais": 1,
					"partidos.equipo1.cambios": 1,
					"partidos.equipo2.pais": 1,
					"partidos.equipo2.cambios": 1,
					_id: 0,
				},
			},
		])
		.toArray();
	printJSON(res);
}
async function get_asistencias() {
	const res = await db
		.collection("mundiales")
		.aggregate([
			{ $match: { anio: anio } },
			{ $unwind: "$partidos" },
			{
				$match: {
					$or: [
						{ "partidos.equipo1.pais": pais },
						{ "partidos.equipo2.pais": pais },
					],
				},
			},
			{ $match: { "partidos.fecha": fecha } },
			{
				$project: {
					"partidos.equipo1.pais": 1,
					"partidos.equipo1.asistencias": 1,
					"partidos.equipo2.pais": 1,
					"partidos.equipo2.asistencias": 1,
					_id: 0,
				},
			},
		])
		.toArray();
	printJSON(res);
}

main();
