.PHONY: init
.PHONY: delete
.PHONY: stop
.PHONY: start
.PHONY: restart_data

init:
	@docker compose up -d

delete:
	@docker compose down -v

stop:
	@docker compose stop 

start:
	@docker compose start 
	
update_data:
	@docker compose down -v
	@docker compose up -d