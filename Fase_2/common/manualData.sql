-- ------------------------------------ Carga 1
BULK INSERT partido
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/partido.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT capitania
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/capitania.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT no_disponible
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/no_disp.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT cambio
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/cambios.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT titular
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/titulares.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT tarjeta
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/tarjetas.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT gol
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/gol.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT penales
FROM '/var/opt/mssql/data/Tablas_parceadas/carga1/penales.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

-- ------------------------------------ Carga 2
BULK INSERT partido
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/partido.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT capitania
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/capitania.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT no_disponible
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/no_disp.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT cambio
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/cambios.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT titular
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/titulares.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT tarjeta
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/tarjetas.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT gol
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/gol.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

BULK INSERT penales
FROM '/var/opt/mssql/data/Tablas_parceadas/carga2/penales.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2,
    FIRE_TRIGGERS
);
GO

-- ------------------------------- Carga 3
update pais
set nombre = UPPER(nombre);

update jugador
set nombre = UPPER(nombre);