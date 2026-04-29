#!/bin/bash
sleep 30s

/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -d master -i 1_init.sql -C
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -d master -i 2_insertData.sql -C
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -d master -i 3_views.sql -C
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P Mundial.123 -d master -i 4_store_procedures.sql -C