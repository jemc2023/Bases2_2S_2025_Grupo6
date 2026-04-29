.PHONY: run-sql
.PHONY: run-mongo
.PHONY: shutdown
.PHONY: run
.PHONY: seed

run-sql:
	@cd ./SQL && make update_data
run-mongo:
	@docker compose up -d
shutdown:
	@cd ./SQL && docker compose down -v
	@docker compose down -v
run:
	@make run-sql
	@make run-mongo
seed:
	@node seed.js > logs.log


# node seed.js > data.json
