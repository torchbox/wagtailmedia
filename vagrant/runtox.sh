tox -c /vagrant/tox.ini -vv "$@"

docker stop $(docker ps -q)
docker system prune --force --volumes
