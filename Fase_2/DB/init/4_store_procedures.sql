USE MundialDB;
GO
CREATE OR ALTER PROCEDURE sp_info_mundial
    @anio_mundial int,
    @tipo_info varchar(30),
    @grupo varchar(30) = NULL,
    @pais varchar(30) = NULL,
    @fecha date = NULL
as
Begin
    declare @is_all bit = 0;
    if @tipo_info = 'all'
    begin
        set @is_all = 1;
    end

    if @is_all = 1 or @tipo_info = 'common info'
    begin
        select *
        from common_info_mundial
        where anio = @anio_mundial
        order by anio desc;
    end
    if @is_all = 1 or @tipo_info = 'posiciones finales'
    begin
        select *
        from posiciones_finales pf
        where anio = @anio_mundial and (pf.pais = @pais or @pais is null)
        ORDER BY prior DESC, PTS desc, Dif desc, pais;
    end
    if @is_all = 1 or @tipo_info = 'fase final'
    begin
        select *
        from fase_final ff
        where anio = @anio_mundial and
              ((ff.Pais_1 = @pais or ff.Pais_2 = @pais) or @pais is null) and
              (ff.fecha = @fecha or @fecha is null)
        order by prior desc, fecha desc;
    end
    if @is_all = 1 or @tipo_info = 'goleadores'
    begin
        select *
        from goleadores
        where anio = @anio_mundial and (@pais = pais or @pais is NULL)
        order by goles desc;
    end
    if @is_all = 1 or @tipo_info = 'grupos y planteles'
    begin
        select *
        from grupos_planteles
        where anio = @anio_mundial
            and (grupo = @grupo  or @grupo is NULL)
            and (pais = @pais  or @pais is NULL)
        order by PTS desc, Dif desc;
    end
    if @is_all = 1 or @tipo_info = 'calendario'
    begin
        select *
        from calendario
        where anio = @anio_mundial and (fecha = @fecha or @fecha is null)
            and ((Pais_1 = @pais or Pais_2 = @pais) or @pais is null)
        order by fecha;
    end
    if @is_all = 1 or @tipo_info = 'premios'
    begin
        select *
        from premios_bonito
        where anio = @anio_mundial and (@pais = pais or @pais is null)
    end
    if @is_all = 1 or @tipo_info = 'equipo ideal'
    begin
        select *
        from equipo_ideal_bonito
        where anio = @anio_mundial and (@pais = pais or @pais is null)
        order by posicion desc;
    end
end
GO

-- all
-- common info
-- posiciones finales
-- fase final
-- goleadores
-- grupos y planteles
-- calendario
-- premios
-- equipo ideal

-- sp_info_mundial 2022, 'all', @pais = 'Argentina'

CREATE OR ALTER PROCEDURE sp_info_pais
    @pais varchar(30),
    @tipo_info varchar(30),
    @ref_jugador varchar(30) = NULL,
    @anio int = NULL
AS
BEGIN
    declare @is_all bit = 0;
    if @tipo_info = 'all'
    begin
        set @is_all = 1;
    end

    if @is_all = 1 or @tipo_info = 'common info'
    begin
        select *
        from common_info_pais
        where pais = @pais
    end
    if @is_all = 1 or @tipo_info = 'planteles'
    begin
        select *
        from plantel_por_anio_pais
        where pais = @pais
          and (anio = @anio or @anio is null)
          and (referencia = @ref_jugador or @ref_jugador is null)
        order by posicion desc;
    end
    if @is_all = 1 or @tipo_info = 'mundial por mundial'
    begin
        select *
        from posiciones_mundiales_pais
        where pais = @pais
            and (@anio = anio or @anio is null)
        order by anio;
    end
    if @is_all = 1 or @tipo_info = 'resultados'
    begin
        select *
        from calendario
        where (@pais = Pais_1 or @pais = Pais_2)
            and (anio = @anio or @anio is null)
        order by anio, fecha;
    end
    if @is_all = 1 or @tipo_info = 'goleadores'
    begin
        select *
        from goleadores_pais
        where pais = @pais
            and (@ref_jugador = jugador or @ref_jugador is null)
        order by goles desc;
    end
END
GO

-- common info
-- planteles
-- mundial por mundial
-- resultados
-- goleadores

-- sp_info_pais 'Argentina', 'all', @ref_jugador = 'lionel messi'


CREATE OR ALTER PROCEDURE sp_info_partido
    @id_partido int,
    @tipo_info varchar(30)
AS
BEGIN
    declare @is_all bit = 0;
    if @tipo_info = 'all'
    begin
        set @is_all = 1;
    end

    if @is_all = 1 or @tipo_info = 'goles'
    begin
        select
            pais,
            jugador,
            min_marcado
        from goles_partido
        where id_partido = @id_partido
        order by pais, cast(minuto as int);
    end
    if @is_all = 1 or @tipo_info = 'penales'
    begin
        select
            pais,
            jugador,
            fue_metido
        from penales_partido
        where id_partido = @id_partido;
    end
    if @is_all = 1 or @tipo_info = 'jugadores'
    begin
        select
            pais,
            referencia,
            posicion,
            num_camisa,
            estado
        from jugadores_partido
        where id_partido = @id_partido
        order by pais, estado desc;
    end
    if @is_all = 1 or @tipo_info = 'tarjetas'
    begin
        select
            min_tarjeta,
            jugador,
            tipo_tarjeta
        from tarjetas_bonito
        where id_partido = @id_partido
        order by min_tarjeta;
    end
    if @is_all = 1 or @tipo_info = 'cambios'
    begin
        select
            minuto_cambio,
            entra,
            sale,
            pais,
            ET
        from cambios_bonito
        where id_partido = @id_partido
        order by pais, minuto_cambio;
    end
end
GO

-- all
-- goles
-- penales
-- jugadores
-- tarjetas
-- cambios

-- sp_info_partido 64, 'tarjetas'