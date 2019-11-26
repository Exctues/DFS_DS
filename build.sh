VERSION="3.2"
USER="concrete13377"

docker build -t=client:$VERSION -f docker/client_dockerfile .
docker tag client:$VERSION $USER/client:$VERSION
docker push $USER/client:$VERSION

docker build -t=namenode:$VERSION -f docker/namenode_dockerfile .
docker tag namenode:$VERSION $USER/namenode:$VERSION
docker push $USER/namenode:$VERSION

docker build -t=storage:$VERSION -f docker/storage_dockerfile .
docker tag storage:$VERSION $USER/storage:$VERSION
docker push $USER/storage:$VERSION

## now how to actually use it
## чтобы подключиться в сварм на воркинг ноде нужно к той команде которую swarm manager дает
## еще --advertise-addr publicip, и swarm init тожне надо с --advertise-addr publicip
## в константах


## docker network create --driver overlay mynetwork

# in compose
# network:
#   mynetwork:
#     external: true

