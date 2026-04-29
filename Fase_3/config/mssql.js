import sql from "mssql";

const config = {
	user: "sa",
	password: "Mundial.123",
	server: "localhost",
	database: "MundialDB",
	options: {
		encrypt: false,
		trustServerCertificate: true,
	},
};

export const pool = await sql.connect(config);
