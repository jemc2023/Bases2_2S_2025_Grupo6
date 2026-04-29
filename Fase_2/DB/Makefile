.PHONY: init
.PHONY: delete
.PHONY: stop
.PHONY: start
.PHONY: restart_data

init:
	@docker compose -p proyecto-mundial-f2 up -d

delete:
	@docker compose -p proyecto-mundial-f2 down -v

stop:
	@docker compose -p proyecto-mundial-f2 stop

start:
	@docker compose -p proyecto-mundial-f2 start
	
update_data:
	@docker compose -p proyecto-mundial-f2 down -v
	@docker compose -p proyecto-mundial-f2 up -d