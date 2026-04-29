import { MongoClient } from "mongodb";

const url = "mongodb://root:password123@localhost:27017";
export const client = new MongoClient(url);
await client.connect();
export let db = client.db("MundialDB");  
export function printJSON(json) {
	const output = JSON.stringify(json, null, 2);
	console.log(output);
}