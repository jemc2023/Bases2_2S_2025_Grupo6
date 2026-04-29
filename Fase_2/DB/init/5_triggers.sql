USE MundialDB;
GO

CREATE OR ALTER TRIGGER trg_log_jugador
ON jugador
AFTER UPDATE, INSERT, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted) -- UPDATE
        insert into log_jugador (operacion, info, usuario)
        select 'UPDATE', concat('Modificado ID: ', cast(id_jugador as VARCHAR(10))), ORIGINAL_LOGIN()
        from inserted;
    ELSE IF EXISTS(SELECT * FROM inserted) -- INSERT
        insert into log_jugador (operacion, info, usuario)
        select 'INSERT', concat('Insertado ID: ', cast(id_jugador as VARCHAR(10))), ORIGINAL_LOGIN()
        from inserted;
    ELSE IF EXISTS(SELECT * FROM deleted) -- DELETE
        insert into log_jugador (operacion, info, usuario)
        select 'DELETE', concat('Eliminado ID: ', cast(id_jugador as VARCHAR(10))), ORIGINAL_LOGIN()
        from deleted;
    ELSE
        return;
END;
GO

CREATE OR ALTER TRIGGER trg_log_pais
ON pais
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS(select * from inserted) AND EXISTS(select * from deleted)
        insert into log_pais (operacion, info, usuario)
        select 'UPDATE', concat('Modificado ID: ', cast(id_pais as VARCHAR(15))), ORIGINAL_LOGIN()
        from inserted;
    ELSE IF EXISTS(select * from inserted)
        insert into log_pais (operacion, info, usuario)
        select 'INSERT', concat('Insertado ID: ', cast(id_pais as VARCHAR(15))), ORIGINAL_LOGIN()
        from inserted;
    ELSE IF EXISTS(select * from deleted)
        insert into log_pais (operacion, info, usuario)
        select 'DELETE', concat('Eliminado ID: ', cast(id_pais as VARCHAR(15))), ORIGINAL_LOGIN()
        from deleted;
    ELSE
        return;
END
GO

CREATE OR ALTER TRIGGER trg_log_mundial ON mundial AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_mundial (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_mundial), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_mundial (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_mundial), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_mundial (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_mundial), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_plantel ON plantel AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_plantel (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_plantel), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_plantel (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_plantel), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_plantel (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_plantel), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_partido ON partido AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_partido (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_partido (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_partido (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_partido), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_cambio ON cambio AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_cambio (operacion, info, usuario) SELECT 'UPDATE', CONCAT('ID Part: ', id_partido, ' Entra: ', id_jugador_entra, ' Sale: ', id_jugador_sale), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_cambio (operacion, info, usuario) SELECT 'INSERT', CONCAT('ID Part: ', id_partido, ' Entra: ', id_jugador_entra, ' Sale: ', id_jugador_sale), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_cambio (operacion, info, usuario) SELECT 'DELETE', CONCAT('ID Part: ', id_partido, ' Entra: ', id_jugador_entra, ' Sale: ', id_jugador_sale), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_capitania ON capitania AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_capitania (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_capitania (operacion, info, usuario) SELECT 'INSERT', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_capitania (operacion, info, usuario) SELECT 'DELETE', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_equipo_ideal ON equipo_ideal AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_equipo_ideal (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Jugador: ', id_jugador, ' Mundial: ', id_mundial), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_equipo_ideal (operacion, info, usuario) SELECT 'INSERT', CONCAT('Jugador: ', id_jugador, ' Mundial: ', id_mundial), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_equipo_ideal (operacion, info, usuario) SELECT 'DELETE', CONCAT('Jugador: ', id_jugador, ' Mundial: ', id_mundial), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_gol ON gol AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_gol (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_gol), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_gol (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_gol), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_gol (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_gol), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_jugador_especial ON jugador_especial AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_jugador_especial (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_jugador), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_jugador_especial (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_jugador), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_jugador_especial (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_jugador), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_jugador_plantel ON jugador_plantel AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_jugador_plantel (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Plantel: ', id_plantel, ' Jugador: ', id_jugador), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_jugador_plantel (operacion, info, usuario) SELECT 'INSERT', CONCAT('Plantel: ', id_plantel, ' Jugador: ', id_jugador), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_jugador_plantel (operacion, info, usuario) SELECT 'DELETE', CONCAT('Plantel: ', id_plantel, ' Jugador: ', id_jugador), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_no_disponible ON no_disponible AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_no_disponible (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_no_disponible (operacion, info, usuario) SELECT 'INSERT', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_no_disponible (operacion, info, usuario) SELECT 'DELETE', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_penales ON penales AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_penales (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_penal), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_penales (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_penal), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_penales (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_penal), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_tipo_premio ON tipo_premio AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_tipo_premio (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_tipo_premio), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_tipo_premio (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_tipo_premio), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_tipo_premio (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_tipo_premio), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_premio ON premio AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_premio (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_premio), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_premio (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_premio), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_premio (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_premio), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_tarjeta ON tarjeta AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_tarjeta (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Modificado ID: ', id_tarjeta), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_tarjeta (operacion, info, usuario) SELECT 'INSERT', CONCAT('Insertado ID: ', id_tarjeta), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_tarjeta (operacion, info, usuario) SELECT 'DELETE', CONCAT('Eliminado ID: ', id_tarjeta), ORIGINAL_LOGIN() FROM deleted;
END;
GO

CREATE OR ALTER TRIGGER trg_log_titular ON titular AFTER INSERT, UPDATE, DELETE AS
BEGIN
    SET NOCOUNT ON;
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        INSERT INTO log_titular (operacion, info, usuario) SELECT 'UPDATE', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM inserted)
        INSERT INTO log_titular (operacion, info, usuario) SELECT 'INSERT', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM inserted;
    ELSE IF EXISTS(SELECT * FROM deleted)
        INSERT INTO log_titular (operacion, info, usuario) SELECT 'DELETE', CONCAT('Jugador: ', id_jugador, ' Partido: ', id_partido), ORIGINAL_LOGIN() FROM deleted;
END;
GO