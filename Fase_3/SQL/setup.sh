#!/bin/bash
sleep 30s

/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -d master -i recovery.sql -C