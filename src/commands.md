Create network (necessary to connect workbench and mysql to easily inspect database schema)
```shell
docker network create uhma_net
```

Export MySQL root password as environment variable
```shell
export MYSQL_ROOT_PASSWORD=<password>
```

Create mysql container
```shell
docker container run -d --name uhma -p 3306:3306 --network uhma_net -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD mysql
```

Create mysql-workbench container
```shell
docker run -d --name mysql-workbench --network uhma_net -e PUID=1000 -e PGID=1000 -e TZ=US/CENTRAL -p 3000:3000 --cap-add="IPC_LOCK" --restart unless-stopped ghcr.io/linuxserver/mysql-workbench
```

Restore old databases
```shell
docker container exec -i uhma sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < Dump20190404.sql 
```

Get backup of individual database of interest
```shell
docker container exec -i uhma sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" uhma' > uhma.sql
```