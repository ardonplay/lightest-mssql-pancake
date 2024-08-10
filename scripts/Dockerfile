FROM  mcr.microsoft.com/mssql/server:2019-latest

USER root

RUN apt update
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18 unixodbc-dev 
ENV  PATH="/opt/mssql-tools18/bin:$PATH"

RUN chown mssql:root /var/backups/

USER mssql
CMD ["/opt/mssql/bin/sqlservr"]