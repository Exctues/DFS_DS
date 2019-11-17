sudo cp logger.py client_docker/logger.py
sudo cp codes.py client_docker/codes.py
sudo cp parameters.py client_docker/parameters.py

sudo cp logger.py namenode_docker/logger.py
sudo cp codes.py namenode_docker/codes.py
sudo cp parameters.py namenode_docker/parameters.py

sudo cp logger.py storage_docker/logger.py
sudo cp codes.py storage_docker/codes.py
sudo cp parameters.py storage_docker/parameters.py

sudo cp constants.py client_docker/constants.py
sudo cp constants.py namenode_docker/constants.py
sudo cp constants.py storage_docker/constants.py

docker build -t=client:3.0 client_docker
docker tag client:3.0 concrete13377/client:3.0
docker push concrete13377/client:3.0

docker build -t=namenode:3.0 namenode_docker
docker tag namenode:3.0 concrete13377/namenode:3.0
docker push concrete13377/namenode:3.0

docker build -t=storage:3.0 storage_docker
docker tag storage:3.0 concrete13377/storage:3.0
docker push concrete13377/storage:3.0

# clean-up to avoid code duplication
rm client_docker/logger.py
rm client_docker/codes.py
rm client_docker/parameters.py

rm namenode_docker/logger.py
rm namenode_docker/codes.py
rm namenode_docker/parameters.py

rm storage_docker/logger.py
rm storage_docker/codes.py
rm storage_docker/parameters.py

rm client_docker/constants.py
rm namenode_docker/constants.py
rm storage_docker/constants.py


## now how to actually use it
## чтобы подключиться в сварм на воркинг ноде нужно к той команде которую swarm manager дает
## еще --attach_addr publicip
## в константах