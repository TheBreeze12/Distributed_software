#!/bin/bash
set -e

echo "[slave-init] waiting for master ..."
until mysql -h mysql-master -uroot -proot123 -e "SELECT 1" >/dev/null 2>&1; do
  sleep 2
done

echo "[slave-init] configuring replication ..."
mysql -uroot -proot123 <<'SQL'
STOP REPLICA;
RESET REPLICA ALL;
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='mysql-master',
  SOURCE_PORT=3306,
  SOURCE_USER='repl',
  SOURCE_PASSWORD='repl123',
  SOURCE_AUTO_POSITION=1,
  GET_SOURCE_PUBLIC_KEY=1;
START REPLICA;
SQL

echo "[slave-init] replication started"
