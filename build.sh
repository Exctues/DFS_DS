VERSION="3.1"
USER="concrete13377"
cd docker

docker build -t=client:$VERSION -f client_dockerfile src
docker tag client:$VERSION $USER/client:$VERSION
docker push $USER/client:$VERSION

docker build -t=namenode:$VERSION namenode_docker
docker tag namenode:$VERSION $USER/namenode:$VERSION
docker push $USER/namenode:$VERSION

docker build -t=storage:$VERSION storage_docker
docker tag storage:$VERSION $USER/storage:$VERSION
docker push $USER/storage:$VERSION

## now how to actually use it
## чтобы подключиться в сварм на воркинг ноде нужно к той команде которую swarm manager дает
## еще --attach_addr publicip
## в константах