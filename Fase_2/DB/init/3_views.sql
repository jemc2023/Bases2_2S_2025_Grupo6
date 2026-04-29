USE MundialDB;
GO
------------------------- Common info
CREATE OR ALTER VIEW common_info_mundial as select
    m.anio as anio,
    pa_camp.nombre as campeon,
    pa_org.nombre as organizador,
    count(distinct pl.id_plantel) as selecciones,
    count(distinct p.id_partido) as partidos,
    count(distinct g.id_gol) as goles
from mundial m
inner join partido p on p.id_mundial = m.id_mundial
inner join pais pa_org on pa_org.id_pais = m.id_pais_org
inner join pais pa_camp on pa_camp.id_pais = m.id_pais_camp
inner join plantel pl on pl.id_mundial = m.id_mundial
left join gol g on g.id_partido = p.id_partido
-- where
--     m.anio = 2022
--      g.fue_tiempo_extra = 0
group by m.anio,pa_org.nombre, pa_camp.nombre;
GO

-- select *
-- from common_info_mundial ci
-- order by anio desc;


------------------------- Resumen Partido
CREATE OR ALTER VIEW resumen_partido as WITH goles_pun AS (
    SELECT
        DISTINCT p.id_partido,
        (SELECT COUNT(*) FROM gol WHERE gol.id_partido = p.id_partido AND gol.id_plantel = p.id_plantel_e1) AS puntaje_e1,
        (SELECT COUNT(*) FROM gol WHERE gol.id_partido = p.id_partido AND gol.id_plantel = p.id_plantel_e2) AS puntaje_e2
    FROM partido p
    LEFT JOIN gol g ON g.id_partido = p.id_partido
),
penal_pun AS (
    SELECT
        DISTINCT p.id_partido,
        (SELECT COUNT(*) FROM penales WHERE penales.id_partido = p.id_partido AND penales.id_plantel = p.id_plantel_e1 AND penales.fue_metido = 1) AS puntaje_e1,
        (SELECT COUNT(*) FROM penales WHERE penales.id_partido = p.id_partido AND penales.id_plantel = p.id_plantel_e2 AND penales.fue_metido = 1) AS puntaje_e2
    FROM partido p
    LEFT JOIN penales pe ON pe.id_partido = p.id_partido
),
datos_resumenes AS (
    SELECT
        p.*,
        CASE
            WHEN pun.puntaje_e1 > pun.puntaje_e2 THEN p.id_plantel_e1
            WHEN pun.puntaje_e1 < pun.puntaje_e2 THEN p.id_plantel_e2
            ELSE NULL
        END AS id_ganador_goles,
        pun.puntaje_e1 AS goles_e1,
        pun.puntaje_e2 AS goles_e2,
        CASE
            WHEN pen.puntaje_e1 > pen.puntaje_e2 THEN p.id_plantel_e1
            WHEN pen.puntaje_e1 < pen.puntaje_e2 THEN p.id_plantel_e2
            ELSE NULL
        END AS id_ganador_penales,
        pen.puntaje_e1 AS penales_e1,
        pen.puntaje_e2 AS penales_e2
    FROM partido p
    INNER JOIN goles_pun pun ON p.id_partido = pun.id_partido
    LEFT JOIN penal_pun pen ON p.id_partido = pen.id_partido
)
SELECT *,
       CASE
           WHEN (t.id_ganador_penales IS NOT NULL) THEN t.id_ganador_penales
           ELSE t.id_ganador_goles
       END AS id_ganador
FROM datos_resumenes t;
GO

-- ----------------------- Posiciones finales
CREATE OR ALTER VIEW posiciones_finales as WITH PrioridadFases AS (
    SELECT
        p.id_mundial,
        p.id_partido,
        p.id_plantel_e1,
        p.id_plantel_e2,
        p.tipo_fase,
        CASE tipo_fase
            WHEN '1ra Ronda' THEN 1
            WHEN 'Octavos de final' THEN 2
            WHEN 'Cuartos de final' THEN 3
            WHEN 'Semifinales' THEN 4
            WHEN '3er puesto' THEN 5
            WHEN 'Final' THEN 6
            ELSE 0
        END AS prior
    FROM partido p
),
RankingEquipos AS (
    SELECT
        m.anio,
        pl.id_plantel,
        pa.nombre AS pais,
        pf.tipo_fase,
        pf.prior,
        ROW_NUMBER() OVER (
            PARTITION BY pl.id_plantel
            ORDER BY pf.prior DESC
        ) AS ranking_fase
    FROM mundial m
    INNER JOIN plantel pl ON pl.id_mundial = m.id_mundial
    INNER JOIN pais pa ON pa.id_pais = pl.id_pais
    INNER JOIN PrioridadFases pf ON pf.id_mundial = m.id_mundial
        AND (pf.id_plantel_e1 = pl.id_plantel OR pf.id_plantel_e2 = pl.id_plantel)
--     WHERE m.anio = 2022
),
posiciones as (
SELECT
    prior,
    anio,
    id_plantel,
    pais,
    tipo_fase,
    (select count(*) from partido where partido.id_plantel_e1 = id_plantel or partido.id_plantel_e2 = id_plantel ) as PJ,
    (select count(*) from resumen_partido where (resumen_partido.id_ganador = id_plantel) and ( resumen_partido.hubo_t_extra = 0)  ) as PG,
    (select count(*) from resumen_partido where (resumen_partido.goles_e1 = resumen_partido.goles_e2) and ( resumen_partido.id_plantel_e1 = id_plantel or resumen_partido.id_plantel_e2 = id_plantel)  ) as PE,
    (select count(*) from resumen_partido where resumen_partido.id_ganador != id_plantel and ( resumen_partido.id_plantel_e1 = id_plantel or resumen_partido.id_plantel_e2 = id_plantel)  ) as PP,
    (select count(*) from gol where gol.id_plantel = re.id_plantel) as GF,
    (select coalesce(sum(goles_e2),0) from resumen_partido where id_plantel_e1 = re.id_plantel)+ (select coalesce(sum(goles_e1),0) from resumen_partido where id_plantel_e2 = re.id_plantel) as GC
FROM RankingEquipos re
WHERE ranking_fase = 1
--   and
--       anio = 2022
)
select
    anio,
    pais,
    tipo_fase,
    case
        when anio >= 1994 then 3*PG+PE
        else 2*PG+PE
    end as PTS,
    PJ,
    PG,
    PE,
    PP,
    GF,
    GC,
    GF-GC as Dif,
    prior
from posiciones;
GO

-- select *
-- from posiciones_finales
-- where
--     anio = 1930
-- ORDER BY prior DESC, PTS desc, Dif desc, pais;

-- ----------------------- Fase Final
CREATE OR ALTER VIEW fase_final as select
    pa1.nombre Pais_1,
    CONCAT(rp.goles_e1, ' (', rp.penales_e1, ')') AS puntaje_e1,
    CONCAT(rp.goles_e2, ' (', rp.penales_e2, ')') AS puntaje_e2,
    pa2.nombre Pais_2,
    tipo_fase,
    anio,
    rp.fecha,
    CASE tipo_fase
            WHEN '1ra Ronda' THEN 1
            WHEN 'Octavos de final' THEN 2
            WHEN 'Cuartos de final' THEN 3
            WHEN 'Semifinales' THEN 4
            WHEN '3er puesto' THEN 5
            WHEN 'Final' THEN 6
            ELSE 0
    END as prior
from resumen_partido rp
inner join mundial m on m.id_mundial = rp.id_mundial
inner join plantel pl1 on pl1.id_plantel = rp.id_plantel_e1
inner join pais pa1 on pa1.id_pais = pl1.id_pais
inner join plantel pl2 on pl2.id_plantel = rp.id_plantel_e2
inner join pais pa2 on pa2.id_pais = pl2.id_pais
where
    rp.tipo_fase != '1ra Ronda';
GO

-- select *
-- from fase_final
-- where anio = 2022
-- order by prior desc, fecha desc;

-------------------------- Goleadores
CREATE OR ALTER VIEW goleadores as WITH asistencia AS (
    SELECT id_partido, id_jugador FROM titular
    UNION
    SELECT id_partido,id_jugador_entra FROM cambio
    UNION
    SELECT id_partido,id_jugador_sale FROM cambio
),
pre_tabla as (select
    j.referencia as jugador,
    count(distinct g.id_gol) as goles,
    COUNT(DISTINCT ar.id_partido) AS partidos,
    pa.nombre as pais,
    m.anio
from plantel pl
inner join mundial m on m.id_mundial = pl.id_mundial
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel
inner join jugador j on j.id_jugador = jp.id_jugador
inner join pais pa on pa.id_pais = pl.id_pais
left join gol g on g.id_jugador=j.id_jugador and g.id_plantel = pl.id_plantel
LEFT JOIN asistencia ar ON ar.id_jugador = j.id_jugador
    AND ar.id_partido IN (SELECT id_partido FROM partido WHERE id_mundial = m.id_mundial)
group by j.referencia, pa.nombre, m.anio)
select
    jugador,
    goles,
    partidos,
    cast((goles*1.0)/NULLIF(partidos, 0) as DECIMAL(4,2)) as promedio_gol,
    pais,
    anio
from pre_tabla
where goles != 0;
GO

-- select *
-- from goleadores
-- where anio = 2022
-- order by goles desc;


------------------------------ Grupo_planteles
CREATE OR ALTER VIEW grupos_planteles as with temp as (select
    m.anio,
    pl.grupo,
    pa.nombre pais,
    (select count(*) from partido where (partido.id_plantel_e1 = id_plantel or partido.id_plantel_e2 = id_plantel) and partido.tipo_fase = '1ra Ronda' ) as PJ,
    (select count(*) from resumen_partido where (resumen_partido.id_ganador = id_plantel) and ( resumen_partido.hubo_t_extra = 0) and tipo_fase = '1ra Ronda' ) as PG,
    (select count(*) from resumen_partido where (resumen_partido.goles_e1 = resumen_partido.goles_e2) and ( resumen_partido.id_plantel_e1 = id_plantel or resumen_partido.id_plantel_e2 = id_plantel) and tipo_fase = '1ra Ronda' ) as PE,
    (select count(*) from resumen_partido where resumen_partido.id_ganador != id_plantel and ( resumen_partido.id_plantel_e1 = id_plantel or resumen_partido.id_plantel_e2 = id_plantel) and tipo_fase = '1ra Ronda' ) as PP,
    (select count(*) from gol inner join partido on partido.id_partido = gol.id_partido where gol.id_plantel = pl.id_plantel and tipo_fase = '1ra Ronda') as GF,
    (select coalesce(sum(goles_e2),0) from resumen_partido where id_plantel_e1 = pl.id_plantel and tipo_fase = '1ra Ronda')+ (select coalesce(sum(goles_e1),0) from resumen_partido where id_plantel_e2 = pl.id_plantel and tipo_fase = '1ra Ronda') as GC
from plantel pl
inner join mundial m on m.id_mundial = pl.id_mundial
inner join pais pa on pa.id_pais = pl.id_pais)
select
    anio as anio,
    grupo as grupo,
    pais as pais,
    case
        when anio >= 1994 then 3*PG+PE
        else 2*PG+PE
    end as PTS,
    PJ,
    PG,
    PE,
    PP,
    GF,
    GC,
    GF-GC as Dif
from temp;
GO

-- select *
-- from grupos_planteles
-- where anio = 2022 and
--     grupo = 'C'
-- order by PTS desc, Dif desc;

-------------------------------- Equipo Ideal Bonito
CREATE OR ALTER VIEW equipo_ideal_bonito as select
    m.anio,
    j.referencia,
    jp.posicion,
    pa.nombre as pais
from equipo_ideal ei
inner join mundial m on m.id_mundial = ei.id_mundial
inner join plantel pl on pl.id_mundial = m.id_mundial
inner join jugador j on j.id_jugador = ei.id_jugador
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel and j.id_jugador = jp.id_jugador
inner join pais pa on pa.id_pais = pl.id_pais;
GO

-- select *
-- from equipo_ideal_bonito
-- where anio = 2018
-- order by posicion desc;

------------------------------- Premios Bonito
CREATE OR ALTER VIEW premios_bonito as (select
    m.anio,
    tp.nombre,
    j.referencia,
    p.nombre as pais
from premio pe
inner join tipo_premio tp on tp.id_tipo_premio = pe.id_tipo_premio
inner join jugador j on j.id_jugador = pe.id_jugador
inner join mundial m on m.id_mundial = pe.id_mundial
inner join jugador_plantel jp on jp.id_jugador = j.id_jugador
inner join plantel pl on pl.id_plantel = jp.id_plantel and pl.id_mundial = m.id_mundial
inner join pais p on p.id_pais = pl.id_pais)
union
(select
    m.anio,
    tp.nombre,
    p.nombre,
    p.nombre as pais
from premio pe
inner join tipo_premio tp on tp.id_tipo_premio = pe.id_tipo_premio
inner join pais p on p.id_pais = pe.id_pais
inner join mundial m on m.id_mundial = pe.id_mundial);
GO

-- select *
-- from premios_bonito
-- where anio = 2018;

----------------------------- Calendario
CREATE OR ALTER VIEW calendario as select
    anio,
    rp.fecha,
    concat(tipo_fase,case
        when (pl1.grupo = pl2.grupo) and tipo_fase = '1ra Ronda' then concat(', ',pl1.grupo)
        else ''
    end) as etapa,
    pa1.nombre Pais_1,
    CONCAT(rp.goles_e1, ' (', rp.penales_e1, ')') AS puntaje_e1,
    CONCAT(rp.goles_e2, ' (', rp.penales_e2, ')') AS puntaje_e2,
    pa2.nombre Pais_2,
    rp.id_partido
from resumen_partido rp
inner join mundial m on m.id_mundial = rp.id_mundial
inner join plantel pl1 on pl1.id_plantel = rp.id_plantel_e1
inner join pais pa1 on pa1.id_pais = pl1.id_pais
inner join plantel pl2 on pl2.id_plantel = rp.id_plantel_e2
inner join pais pa2 on pa2.id_pais = pl2.id_pais;
GO

-- select *
-- from calendario
-- where anio = 1930
-- order by fecha;

---------------------------- Common info pais
CREATE OR ALTER VIEW common_info_pais as with t_resumen as (select
    pa.nombre as pais,
    (select count(*) from plantel where plantel.id_pais = pa.id_pais) as cant_mundiales,
    (select string_agg(cast(anio as VARCHAR), ', ') from mundial where id_pais_camp = pa.id_pais) as campeon,
    (SELECT
    string_agg(cast(anio as VARCHAR), ', ')
FROM resumen_partido rp
INNER JOIN plantel pl ON (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
INNER JOIN mundial m ON m.id_mundial = pl.id_mundial
WHERE rp.tipo_fase = 'Final'
  AND pl.id_pais = pa.id_pais
  AND pl.id_plantel != rp.id_ganador) as subcampeon,
    (select count(distinct rp.id_partido)
from resumen_partido rp
inner join plantel pl on (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
where pl.id_pais = pa.id_pais) as partidos_jugados,
    (select count(distinct rp.id_partido)
from resumen_partido rp
inner join plantel pl on (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
where pl.id_pais = pa.id_pais and pl.id_plantel = rp.id_ganador_goles) as partidos_ganados,
    (select count(distinct rp.id_partido)
from resumen_partido rp
inner join plantel pl on (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
where pl.id_pais = pa.id_pais and rp.id_ganador_goles is null) as partidos_empatados,
    (select count(distinct rp.id_partido)
from resumen_partido rp
inner join plantel pl on (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
where pl.id_pais = pa.id_pais and pl.id_plantel != rp.id_ganador_goles) as partidos_perdidos,
    (SELECT
    sum(case
            when pl.id_plantel = rp.id_plantel_e1 then rp.goles_e1
            else rp.goles_e2
    end)
FROM resumen_partido rp
INNER JOIN plantel pl ON (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
INNER JOIN mundial m ON m.id_mundial = pl.id_mundial
WHERE pl.id_pais = pa.id_pais) as goles_favor,
    (SELECT
    sum(case
            when pl.id_plantel = rp.id_plantel_e1 then rp.goles_e2
            else rp.goles_e1
    end)
FROM resumen_partido rp
INNER JOIN plantel pl ON (pl.id_plantel = rp.id_plantel_e1 OR pl.id_plantel = rp.id_plantel_e2)
INNER JOIN mundial m ON m.id_mundial = pl.id_mundial
WHERE pl.id_pais = pa.id_pais) as goles_contra,
    (select string_agg(cast(anio as VARCHAR), ', ') from pais inner join mundial m on m.id_pais_org = pais.id_pais
    where pais.id_pais = pa.id_pais) as sede
from pais pa)
select
    pais,
    cant_mundiales,
    campeon,
    subcampeon,
    partidos_jugados,
    concat(partidos_ganados, ' (', cast((partidos_ganados*1.0/NULLIF(partidos_jugados, 0))*100 as DECIMAL(4,1)) ,'%', ')') as partidos_ganados,
    concat(partidos_empatados, ' (', cast((partidos_empatados*1.0/NULLIF(partidos_jugados, 0))*100 as DECIMAL(4,1)) ,'%', ')') as partidos_empatados,
    concat(partidos_perdidos, ' (', cast((partidos_perdidos*1.0/NULLIF(partidos_jugados, 0))*100 as DECIMAL(4,1)) ,'%', ')') as partidos_perdidos,
    goles_favor,
    goles_contra,
    goles_favor-goles_contra as Dif,
    cast(goles_favor*1.0/NULLIF(partidos_jugados, 0) as DECIMAL(4,2)) as prom_favor,
    cast(goles_contra*1.0/NULLIF(partidos_jugados, 0) as DECIMAL(4,2)) as prom_contra,
    cast(goles_favor*1.0/NULLIF(partidos_jugados, 0) as DECIMAL(4,2))-cast(goles_contra*1.0/NULLIF(partidos_jugados, 0) as DECIMAL(4,2)) as prom_dif,
    sede
from t_resumen;
GO

-- select *
-- from common_info_pais
-- where pais = 'Argentina';

---------------------------- Plantel por pais anio
CREATE OR ALTER VIEW plantel_por_anio_pais as select
    m.anio,
    pa.nombre as pais,
    jp.num_camisa,
    j.referencia,
    jp.posicion,
    j.cumpleanios,
    j.height
from pais pa
inner join plantel pl on pl.id_pais = pa.id_pais
inner join mundial m on m.id_mundial = pl.id_mundial
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel
inner join jugador j on jp.id_jugador = j.id_jugador;
GO

-- select *
-- from plantel_por_anio_pais
-- where pais = 'Argentina' and
--       anio = 1934
-- order by posicion desc;

------------------- Posiciones Mundial por Pais
CREATE OR ALTER VIEW posiciones_mundiales_pais as select *
from posiciones_finales
where anio in (select mundial.anio from mundial);
GO

-- select *
-- from posiciones_mundiales_pais
-- where pais = 'Argentina'
-- order by anio ;

------------------ Goleadores Pais
CREATE OR ALTER VIEW goleadores_pais AS WITH asistencia AS (
    SELECT id_partido, id_jugador FROM titular
    UNION
    SELECT id_partido,id_jugador_entra FROM cambio
    UNION
    SELECT id_partido,id_jugador_sale FROM cambio
)
select
    pa.nombre as pais,
    j.referencia as jugador,
    count(distinct g.id_gol) as goles,
    cast(count(distinct g.id_gol)*1.0/count(distinct a.id_partido) as DECIMAL(4,2)) as prom_gol,
    count(distinct a.id_partido) as partidos,
    count(distinct m.id_mundial) as mundiales

from jugador j
inner join jugador_plantel jp on jp.id_jugador = j.id_jugador
inner join plantel pl on pl.id_plantel = jp.id_plantel
inner join pais pa on pa.id_pais = pl.id_pais
inner join gol g on g.id_jugador = j.id_jugador
left join asistencia a on a.id_jugador = j.id_jugador
inner join mundial m on m.id_mundial = pl.id_mundial
group by j.id_jugador ,pa.nombre, j.referencia;
GO

-- select *
-- from goleadores_pais
-- where pais = 'Argentina'
-- order by goles desc;

------------------------------------ Cambios Bonito
CREATE OR ALTER VIEW cambios_bonito AS select
    cast(minuto as int) as minuto_cambio,
    j1.referencia entra,
    j2.referencia sale,
    pa.nombre as pais,
    case
        when fue_et = 1 then 1
        else NULL
    end as ET,
    c.id_partido
from cambio c
inner join jugador j1 on j1.id_jugador = c.id_jugador_entra
inner join jugador j2 on j2.id_jugador = c.id_jugador_sale
inner join jugador_plantel jp on jp.id_jugador = j1.id_jugador or jp.id_jugador = j2.id_jugador
inner join plantel pl on pl.id_plantel = jp.id_plantel
inner join pais pa on pa.id_pais = pl.id_pais
group by minuto, j1.referencia, j2.referencia, pa.nombre, fue_et, c.id_partido;
GO

-- select *
-- from cambios_bonito
-- where id_partido = 64
-- order by pais, minuto_cambio;

------------------------------- Tarjetas Bonito
CREATE OR ALTER VIEW tarjetas_bonito AS select
    cast(minuto as int) as min_tarjeta,
    j.referencia as jugador,
    case
        when es_amarilla = 1 then 'AMARILLA'
        else 'ROJA'
    end as tipo_tarjeta,
    t.id_partido
from tarjeta t
inner join jugador j on j.id_jugador = t.id_jugador
inner join jugador_plantel jp on jp.id_jugador = j.id_jugador
inner join plantel pl on pl.id_plantel = jp.id_plantel
inner join pais pa on pa.id_pais = pl.id_pais
group by minuto, j.referencia, es_amarilla, t.id_partido;
GO

-- select *
-- from tarjetas_bonito
-- where id_partido = 64
-- order by min_tarjeta;



------------------------------- Jugadores por Partido
CREATE OR ALTER VIEW jugadores_partido as with no_suplentes as ((select
    pa.nombre as pais,
    j.referencia,
    jp.posicion,
    jp.num_camisa,
    'Titular' estado,
    j.id_jugador,
    p.id_partido
from partido p
inner join titular t on t.id_partido = p.id_partido
left join capitania c on c.id_partido = t.id_partido and c.id_jugador = t.id_jugador
inner join plantel pl on pl.id_plantel = p.id_plantel_e1 or pl.id_plantel = id_plantel_e2
inner join pais pa on pa.id_pais = pl.id_pais
inner join jugador j on t.id_jugador = j.id_jugador
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel and jp.id_jugador = j.id_jugador)
union
(select
    pa.nombre as pais,
    j.referencia,
    jp.posicion,
    jp.num_camisa,
    'Ingresaron' estado,
    j.id_jugador,
    p.id_partido
from partido p
inner join cambio t on t.id_partido = p.id_partido
left join capitania c on c.id_partido = t.id_partido and c.id_jugador = t.id_jugador_entra
inner join plantel pl on pl.id_plantel = p.id_plantel_e1 or pl.id_plantel = id_plantel_e2
inner join pais pa on pa.id_pais = pl.id_pais
inner join jugador j on t.id_jugador_entra = j.id_jugador
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel and jp.id_jugador = j.id_jugador
)
union
(select
    pa.nombre as pais,
    j.referencia,
    jp.posicion,
    jp.num_camisa,
    'No disponible' estado,
    j.id_jugador,
    p.id_partido
from partido p
inner join no_disponible t on t.id_partido = p.id_partido
left join capitania c on c.id_partido = t.id_partido and c.id_jugador = t.id_jugador
inner join plantel pl on pl.id_plantel = p.id_plantel_e1 or pl.id_plantel = id_plantel_e2
inner join pais pa on pa.id_pais = pl.id_pais
inner join jugador j on t.id_jugador = j.id_jugador
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel and jp.id_jugador = j.id_jugador)),
suplentes as (select
    pa.nombre as pais,
    j.referencia,
    jp.posicion,
    jp.num_camisa,
    'Suplente' estado,
    j.id_jugador,
    p.id_partido
from plantel pl
inner join jugador_plantel jp on jp.id_plantel = pl.id_plantel
inner join partido p on p.id_plantel_e1 = pl.id_plantel or p.id_plantel_e2 = pl.id_plantel
left join no_suplentes ns on ns.id_jugador = jp.id_jugador and ns.id_partido = p.id_partido
inner join jugador j on j.id_jugador = jp.id_jugador
inner join pais pa on pa.id_pais = pl.id_pais
where ns.id_jugador is null)
select *
from no_suplentes
union
select *
from suplentes;
GO

-- select *
-- from jugadores_partido
-- where id_partido = 64
-- order by pais, estado desc;

------------------------------- Goles por partido
CREATE OR ALTER VIEW goles_partido AS select
    pa.nombre pais,
    j.referencia jugador,
    concat(g.minuto, case when g.detalle != '' then concat(' (',g.detalle,')') else '' end) min_marcado,
    id_partido,
    g.minuto
from gol g
inner join jugador j on j.id_jugador = g.id_jugador
inner join plantel pl on pl.id_plantel = g.id_plantel
inner join pais pa on pa.id_pais = pl.id_pais;
GO

-- select
--     pais,
--     jugador,
--     min_marcado
-- from goles_partido
-- where id_partido = 64
-- order by pais, cast(minuto as int);

----------------------------- Penales por partido
CREATE OR ALTER VIEW penales_partido as select
    pa.nombre pais,
    j.referencia jugador,
    concat(case when fue_metido = 1 then 'Metido' else 'Fallido' end, case when detalle != '' then concat(' (', detalle, ')') else '' end) fue_metido,
    id_partido
from penales g
inner join jugador j on j.id_jugador = g.id_jugador
inner join plantel pl on pl.id_plantel = g.id_plantel
inner join pais pa on pa.id_pais = pl.id_pais;
GO

-- select *
-- from penales_partido
-- where id_partido = 64;

----------------------------- Conteos
CREATE OR ALTER VIEW conteos AS
SELECT * FROM (
    -- Entidades Maestras
    SELECT 'jugador' as Tabla,
           (SELECT COUNT(*) FROM jugador) as Conteo_Tabla,
           (SELECT COUNT(*) FROM log_jugador) as Conteo_Log
    UNION ALL
    SELECT 'jugador_especial',
           (SELECT COUNT(*) FROM jugador_especial),
           (SELECT COUNT(*) FROM log_jugador_especial)
    UNION ALL
    SELECT 'mundial',
           (SELECT COUNT(*) FROM mundial),
           (SELECT COUNT(*) FROM log_mundial)
    UNION ALL
    SELECT 'pais',
           (SELECT COUNT(*) FROM pais),
           (SELECT COUNT(*) FROM log_pais)
    UNION ALL
    SELECT 'plantel',
           (SELECT COUNT(*) FROM plantel),
           (SELECT COUNT(*) FROM log_plantel)
    UNION ALL
    SELECT 'jugador_plantel',
           (SELECT COUNT(*) FROM jugador_plantel),
           (SELECT COUNT(*) FROM log_jugador_plantel)
    UNION ALL
    SELECT 'premio',
           (SELECT COUNT(*) FROM premio),
           (SELECT COUNT(*) FROM log_premio)
    UNION ALL
    SELECT 'tipo_premio',
           (SELECT COUNT(*) FROM tipo_premio),
           (SELECT COUNT(*) FROM log_tipo_premio)
    UNION ALL
    SELECT 'equipo_ideal',
           (SELECT COUNT(*) FROM equipo_ideal),
           (SELECT COUNT(*) FROM log_equipo_ideal)
    UNION ALL

    -- Eventos de Partido
    SELECT 'partido',
           (SELECT COUNT(*) FROM partido),
           (SELECT COUNT(*) FROM log_partido)
    UNION ALL
    SELECT 'gol',
           (SELECT COUNT(*) FROM gol),
           (SELECT COUNT(*) FROM log_gol)
    UNION ALL
    SELECT 'penales',
           (SELECT COUNT(*) FROM penales),
           (SELECT COUNT(*) FROM log_penales)
    UNION ALL
    SELECT 'titular',
           (SELECT COUNT(*) FROM titular),
           (SELECT COUNT(*) FROM log_titular)
    UNION ALL
    SELECT 'cambio',
           (SELECT COUNT(*) FROM cambio),
           (SELECT COUNT(*) FROM log_cambio)
    UNION ALL
    SELECT 'no_disponible',
           (SELECT COUNT(*) FROM no_disponible),
           (SELECT COUNT(*) FROM log_no_disponible)
    UNION ALL
    SELECT 'capitania',
           (SELECT COUNT(*) FROM capitania),
           (SELECT COUNT(*) FROM log_capitania)
    UNION ALL
    SELECT 'tarjeta',
           (SELECT COUNT(*) FROM tarjeta),
           (SELECT COUNT(*) FROM log_tarjeta)
) AS ConteosT;
GO

-- select *
-- from Conteos;