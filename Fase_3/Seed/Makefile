# Variables
NODE = node
LOGS_DIR = logs
LOG_FILE = $(LOGS_DIR)/logs.log

# Comandos principales
help:
	@echo Comandos disponibles:
	@echo   make seed      - Ejecutar seed (salida normal a logs.log, errores en consola)
	@echo   make check     - Verificar datos en MongoDB
	@echo   make clean     - Limpiar todas las colecciones
	@echo   make mongo     - Entrar a MongoDB
	@echo   make status    - Ver contenedores Docker
	@echo   make logs      - Ver el archivo logs.log
	@echo   make tail      - Ver ultimas lineas de logs.log
	@echo   make clean-log - Eliminar archivo de log

# Crear directorio de logs
$(LOGS_DIR):
	if not exist $(LOGS_DIR) mkdir $(LOGS_DIR)

# Ejecutar seed: stdout a logs.log, stderr a consola
seed: $(LOGS_DIR)
	@echo Ejecutando seed... (salida normal guardada en $(LOG_FILE))
	@$(NODE) seed.js > $(LOG_FILE) 2>&1
	@type $(LOG_FILE) | findstr /i "error" || echo No se encontraron errores
	@echo.
	@echo Seed ejecutado. Revisa $(LOG_FILE) para ver la salida completa

# Ejecutar seed y ver errores en tiempo real
seed-verbose: $(LOGS_DIR)
	@echo Ejecutando seed mostrando solo errores...
	@$(NODE) seed.js 2>&1 1>$(LOG_FILE)

# Verificar datos
check:
	@docker exec mongo-mundial mongosh -u root -p password123 --eval "use MundialDB; print('\n=== COLECCIONES ==='); print('mundiales: ' + db.mundiales.countDocuments()); print('mundial_metricas: ' + db.mundial_metricas.countDocuments()); print('paises: ' + db.paises.countDocuments());"

# Limpiar todas las colecciones
clean:
	@docker exec mongo-mundial mongosh -u root -p password123 --eval "use MundialDB; db.mundiales.drop(); db.mundial_metricas.drop(); db.paises.drop(); print('Colecciones limpiadas');"
	@echo Colecciones eliminadas

# Entrar a MongoDB
mongo:
	docker exec -it mongo-mundial mongosh -u root -p password123

# Ver estado de contenedores
status:
	docker ps --format "table {{.Names}}\t{{.Status}}"

# Ver el archivo de log completo
logs:
	@type $(LOG_FILE) 2>nul || echo No hay archivo de log

# Ver ultimas 50 lineas del log
tail:
	@powershell -Command "Get-Content $(LOG_FILE) -Tail 50" 2>nul || echo No hay archivo de log

# Limpiar log
clean-log:
	@if exist $(LOG_FILE) del $(LOG_FILE)
	@echo Log eliminado

# Limpiar directorio logs
clean-logs:
	@if exist $(LOGS_DIR) rmdir /s /q $(LOGS_DIR)
	@echo Directorio logs eliminado

# Ejecutar todo (seed + check)
all: seed check
	@echo Proceso completado

# Reset: limpiar, ejecutar seed y verificar
reset: clean seed check
	@echo Reset completado