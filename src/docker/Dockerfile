FROM mcr.microsoft.com/mssql/server:2019-latest

USER root
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt update
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt install -y python3.12 python3.12-venv curl 
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 312
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 
RUN pip install pyodbc
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools18 unixodbc-dev
ENV PATH="/opt/mssql-tools18/bin:$PATH"
RUN chown mssql:root /var/backups/

COPY ../scripts ./var/scripts
ENV PATH="/var/scripts/bin:$PATH"

USER mssql
CMD ["/opt/mssql/bin/sqlservr"]