USE master;
GO
CREATE DATABASE MundialDB;
GO
USE MundialDB;
GO

-- Creación de Tablas
CREATE TABLE pais (
    id_pais INT NOT NULL,
    nombre  VARCHAR(30) NOT NULL,
    CONSTRAINT pais_pk PRIMARY KEY ( id_pais )
);

CREATE TABLE jugador (
    id_jugador  INT NOT NULL,
    referencia  VARCHAR(30) NOT NULL,
    nombre      VARCHAR(60),
    cumpleanios DATE,
    height      DECIMAL(3, 2),
    CONSTRAINT jugador_pk PRIMARY KEY ( id_jugador )
);

CREATE TABLE mundial (
    id_mundial   INT NOT NULL,
    anio         INT NOT NULL,
    id_pais_org  INT NOT NULL,
    id_pais_camp INT NOT NULL,
    CONSTRAINT mundial_pk PRIMARY KEY ( id_mundial )
);

CREATE TABLE plantel (
    id_plantel INT NOT NULL,
    id_mundial INT NOT NULL,
    id_pais    INT NOT NULL,
    grupo      VARCHAR(10),
    CONSTRAINT plantel_pk PRIMARY KEY ( id_plantel )
);

CREATE TABLE partido (
    id_partido    INT NOT NULL,
    id_plantel_e1 INT NOT NULL,
    id_plantel_e2 INT NOT NULL,
    fecha         DATE NOT NULL,
    tipo_fase     VARCHAR(30) NOT NULL,
    id_mundial    INT NOT NULL,
    hubo_t_extra  INT,
    hubo_penales  INT,
    CONSTRAINT partido_pk PRIMARY KEY ( id_partido )
);

CREATE TABLE cambio (
    id_partido       INT NOT NULL,
    id_jugador_entra INT NOT NULL,
    id_jugador_sale  INT NOT NULL,
    minuto           VARCHAR(30) NOT NULL,
    fue_et           INT NOT NULL,
    CONSTRAINT cambio_pk PRIMARY KEY ( id_partido, id_jugador_entra, id_jugador_sale )
);

CREATE TABLE capitania (
    id_partido INT NOT NULL,
    id_jugador INT NOT NULL,
    CONSTRAINT capitania_pk PRIMARY KEY ( id_jugador, id_partido )
);

CREATE TABLE equipo_ideal (
    id_mundial INT NOT NULL,
    id_jugador INT NOT NULL,
    CONSTRAINT equipo_ideal_pk PRIMARY KEY ( id_jugador, id_mundial )
);

CREATE TABLE gol (
    id_gol           INT NOT NULL,
    id_partido       INT NOT NULL,
    detalle          VARCHAR(30) NOT NULL,
    id_jugador       INT NOT NULL,
    id_plantel       INT NOT NULL,
    minuto           VARCHAR(30) NOT NULL,
    fue_tiempo_extra INT NOT NULL,
    CONSTRAINT gol_pk PRIMARY KEY ( id_gol )
);

CREATE TABLE jugador_especial (
    id_jugador       INT NOT NULL,
    lugar_nacimiento VARCHAR(60),
    apodos           VARCHAR(60),
    sitio_web        VARCHAR(150),
    ig               VARCHAR(150),
    face             VARCHAR(150),
    yt               VARCHAR(150),
    twitter          VARCHAR(150),
    tiktok           VARCHAR(150),
    CONSTRAINT jugador_especial_pk PRIMARY KEY ( id_jugador )
);

CREATE TABLE jugador_plantel (
    id_plantel INT NOT NULL,
    id_jugador INT NOT NULL,
    num_camisa INT,
    posicion   VARCHAR(15) NOT NULL,
    CONSTRAINT jugador_plantel_pk PRIMARY KEY ( id_plantel, id_jugador )
);

CREATE TABLE no_disponible (
    id_partido INT NOT NULL,
    id_jugador INT NOT NULL,
    detalle    VARCHAR(30) NOT NULL,
    CONSTRAINT no_disponible_pk PRIMARY KEY ( id_jugador, id_partido )
);

CREATE TABLE penales (
    id_penal   INT NOT NULL,
    id_partido INT NOT NULL,
    detalle     VARCHAR(30) NOT NULL,
    id_jugador INT NOT NULL,
    id_plantel INT NOT NULL,
    fue_metido INT NOT NULL,
    CONSTRAINT penales_pk PRIMARY KEY ( id_penal )
);

CREATE TABLE tipo_premio (
    id_tipo_premio INT NOT NULL,
    nombre         VARCHAR(30) NOT NULL,
    CONSTRAINT tipo_premio_pk PRIMARY KEY ( id_tipo_premio )
);

CREATE TABLE premio (
    id_premio      INT NOT NULL,
    id_mundial     INT NOT NULL,
    id_tipo_premio INT NOT NULL,
    id_jugador     INT,
    id_pais        INT,
    CONSTRAINT premio_pk PRIMARY KEY ( id_premio )
);

ALTER TABLE premio
    ADD CONSTRAINT arc_1
        CHECK ( ( ( id_jugador IS NOT NULL )
                  AND ( id_pais IS NULL ) )
                OR ( ( id_pais IS NOT NULL )
                     AND ( id_jugador IS NULL ) ) );

CREATE TABLE tarjeta (
    id_tarjeta  INT NOT NULL,
    id_partido  INT NOT NULL,
    id_jugador  INT NOT NULL,
    minuto      VARCHAR(30) NOT NULL,
    es_amarilla INT NOT NULL,
    CONSTRAINT tarjeta_pk PRIMARY KEY ( id_tarjeta )
);

CREATE TABLE titular (
    id_partido INT NOT NULL,
    id_jugador INT NOT NULL,
    CONSTRAINT titular_pk PRIMARY KEY ( id_jugador, id_partido )
);

-- Tablas de logs
CREATE TABLE log_jugador (
    id_log_jugador INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_pais (
    id_log_pais INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_mundial (
    id_log_mundial INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_plantel (
    id_log_plantel INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_jugador_plantel (
    id_log_jugador_plantel INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_jugador_especial (
    id_log_jugador_especial INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_partido (
    id_log_partido INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_gol (
    id_log_gol INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_cambio (
    id_log_cambio INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_tarjeta (
    id_log_tarjeta INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_penales (
    id_log_penales INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_titular (
    id_log_titular INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_capitania (
    id_log_capitania INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_no_disponible (
    id_log_no_disponible INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_tipo_premio (
    id_log_tipo_premio INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_premio (
    id_log_premio INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE log_equipo_ideal (
    id_log_equipo_ideal INT IDENTITY(1,1) PRIMARY KEY,
    operacion VARCHAR(10),
    info VARCHAR(70),
    usuario VARCHAR(100),
    fecha DATETIME DEFAULT GETDATE()
);

CREATE TABLE backupTimer (
    tipo VARCHAR(20),
    hora DATETIME PRIMARY KEY  DEFAULT GETDATE()
);

-- Foreign Keys con ON DELETE CASCADE

-- Cambio
ALTER TABLE cambio ADD CONSTRAINT cambio_jugador_fk FOREIGN KEY ( id_jugador_entra ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE cambio ADD CONSTRAINT cambio_jugador_fkv1 FOREIGN KEY ( id_jugador_sale ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE cambio ADD CONSTRAINT cambio_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;

-- Capitania
ALTER TABLE capitania ADD CONSTRAINT capitania_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE capitania ADD CONSTRAINT capitania_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;

-- Equipo Ideal
ALTER TABLE equipo_ideal ADD CONSTRAINT equipo_ideal_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE equipo_ideal ADD CONSTRAINT equipo_ideal_mundial_fk FOREIGN KEY ( id_mundial ) REFERENCES mundial ( id_mundial ) ON DELETE CASCADE;

-- Gol
ALTER TABLE gol ADD CONSTRAINT gol_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE gol ADD CONSTRAINT gol_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;
ALTER TABLE gol ADD CONSTRAINT gol_plantel_fk FOREIGN KEY ( id_plantel ) REFERENCES plantel ( id_plantel ) ON DELETE CASCADE;

-- Jugador Especial
ALTER TABLE jugador_especial ADD CONSTRAINT jugador_especial_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;

-- Jugador Plantel
ALTER TABLE jugador_plantel ADD CONSTRAINT jugador_plantel_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE jugador_plantel ADD CONSTRAINT jugador_plantel_plantel_fk FOREIGN KEY ( id_plantel ) REFERENCES plantel ( id_plantel ) ON DELETE CASCADE;

-- Mundial
ALTER TABLE mundial ADD CONSTRAINT mundial_pais_fk FOREIGN KEY ( id_pais_org ) REFERENCES pais ( id_pais ) ON DELETE CASCADE;
ALTER TABLE mundial ADD CONSTRAINT mundial_pais_fkv1 FOREIGN KEY ( id_pais_camp ) REFERENCES pais ( id_pais ) ON DELETE CASCADE;

-- No Disponible
ALTER TABLE no_disponible ADD CONSTRAINT no_disponible_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE no_disponible ADD CONSTRAINT no_disponible_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;

-- Partido
ALTER TABLE partido ADD CONSTRAINT partido_mundial_fk FOREIGN KEY ( id_mundial ) REFERENCES mundial ( id_mundial ) ON DELETE NO ACTION; -- Nota: Se usa No Action para evitar ciclos si es necesario
ALTER TABLE partido ADD CONSTRAINT partido_plantel_fk FOREIGN KEY ( id_plantel_e1 ) REFERENCES plantel ( id_plantel ) ON DELETE CASCADE;
ALTER TABLE partido ADD CONSTRAINT partido_plantel_fkv1 FOREIGN KEY ( id_plantel_e2 ) REFERENCES plantel ( id_plantel ) ON DELETE NO ACTION;

-- Penales
ALTER TABLE penales ADD CONSTRAINT penales_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE penales ADD CONSTRAINT penales_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;
ALTER TABLE penales ADD CONSTRAINT penales_plantel_fk FOREIGN KEY ( id_plantel ) REFERENCES plantel ( id_plantel ) ON DELETE CASCADE;

-- Plantel
ALTER TABLE plantel ADD CONSTRAINT plantel_mundial_fk FOREIGN KEY ( id_mundial ) REFERENCES mundial ( id_mundial ) ON DELETE CASCADE;
ALTER TABLE plantel ADD CONSTRAINT plantel_pais_fk FOREIGN KEY ( id_pais ) REFERENCES pais ( id_pais ) ON DELETE CASCADE;

-- Premio
ALTER TABLE premio ADD CONSTRAINT premio_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE premio ADD CONSTRAINT premio_mundial_fk FOREIGN KEY ( id_mundial ) REFERENCES mundial ( id_mundial ) ON DELETE CASCADE;
ALTER TABLE premio ADD CONSTRAINT premio_pais_fk FOREIGN KEY ( id_pais ) REFERENCES pais ( id_pais ) ON DELETE NO ACTION;
ALTER TABLE premio ADD CONSTRAINT premio_tipo_premio_fk FOREIGN KEY ( id_tipo_premio ) REFERENCES tipo_premio ( id_tipo_premio ) ON DELETE CASCADE;

-- Tarjeta
ALTER TABLE tarjeta ADD CONSTRAINT tarjeta_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE tarjeta ADD CONSTRAINT tarjeta_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;

-- Titular
ALTER TABLE titular ADD CONSTRAINT titular_jugador_fk FOREIGN KEY ( id_jugador ) REFERENCES jugador ( id_jugador ) ON DELETE CASCADE;
ALTER TABLE titular ADD CONSTRAINT titular_partido_fk FOREIGN KEY ( id_partido ) REFERENCES partido ( id_partido ) ON DELETE CASCADE;

