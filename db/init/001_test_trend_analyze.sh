#! /bin/sh

echo "CREATE DATABASE IF NOT EXISTS \`test_trend_analyze\` ;" | "${mysql[@]}"
echo "GRANT ALL ON \`test_trend_analyze\`.* TO '"$MYSQL_USER"'@'%' ;" | "${mysql[@]}"
echo 'FLUSH PRIVILEGES ;' | "${mysql[@]}"

"${mysql[@]}" < /docker-entrypoint-initdb.d/test_trend_analyze.sql_