USE MundialDB;
GO

SET LANGUAGE Spanish;
SET DATEFORMAT dmy;
GO

BULK INSERT jugador
FROM '/var/opt/mssql/data/Tablas_parceadas/Jugador.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT pais
FROM '/var/opt/mssql/data/Tablas_parceadas/pais.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT mundial
FROM '/var/opt/mssql/data/Tablas_parceadas/Mundial.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT plantel
FROM '/var/opt/mssql/data/Tablas_parceadas/Plantel.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO


delete
from plantel
where id_plantel in (select
    id_plantel
from (select
    id_plantel,
    row_number() over (
        partition by id_mundial, id_pais
        order by id_plantel
        ) as id_dup
from plantel) as sub
where id_dup = 2);
GO

UPDATE plantel
SET grupo = REPLACE(REPLACE(REPLACE(grupo, CHAR(13), ''), CHAR(10), ''), ' ', '');
GO

BULK INSERT jugador_plantel
FROM '/var/opt/mssql/data/Tablas_parceadas/jugador_plantel.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT tipo_premio
FROM '/var/opt/mssql/data/Tablas_parceadas/tipos_de_premio.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

-- ERROR
BULK INSERT premio
FROM '/var/opt/mssql/data/Tablas_parceadas/premios.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT equipo_ideal
FROM '/var/opt/mssql/data/Tablas_parceadas/equipo_ideal.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT jugador_especial
FROM '/var/opt/mssql/data/Tablas_parceadas/jugadores_especiales.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT partido
FROM '/var/opt/mssql/data/Tablas_parceadas/partido.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT capitania
FROM '/var/opt/mssql/data/Tablas_parceadas/capitania.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT no_disponible
FROM '/var/opt/mssql/data/Tablas_parceadas/no_disp.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT cambio
FROM '/var/opt/mssql/data/Tablas_parceadas/cambios.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT titular
FROM '/var/opt/mssql/data/Tablas_parceadas/titulares.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT tarjeta
FROM '/var/opt/mssql/data/Tablas_parceadas/tarjetas.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT gol
FROM '/var/opt/mssql/data/Tablas_parceadas/gol.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO

BULK INSERT penales
FROM '/var/opt/mssql/data/Tablas_parceadas/penales.csv'
WITH (
    FIELDTERMINATOR  = ';',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);
GO
