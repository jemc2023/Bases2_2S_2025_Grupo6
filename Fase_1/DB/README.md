## Cambios realizados:

### Entidad Premio

- Se ha agregado una pk natura o con un id autoincrementable, ya que, existen mundiales en donde 'N' cantidad de participantes ganaron el mismo tipo de premio.
- Se ha quitado la llave primera compuesta (id_tipo_premio, id_mundial) por solo una llave primera simple (id), dado el cambio anterior.

### Entidad Plantel

- Se ha puesto como no obligatorio el atributo 'grupo', ya que, existe un mundial en donde los equipos involucrados no tienen asignado un grupo.

### Entidad No_disponible

- Se ha modificado la relación que se tenía con la etnidad 'Partido', ahora pasó a ser una relación identificadora (error en el diseño lógico). Ya que con esto, ya podríamos tener la capacidad de registrar a los jugadores que no estuvieron disponibles en uno o varios partidos.

### Entidad Tarjeta

- Se ha generado una PK natural de un único atributo (id_tarjeta), ya que, existen partidos en donde a cierto jugador le han sacado más de una tarjeta, indpendientemente del color, en el mismo minuto, por lo que era realmente necesario una PK natura.
