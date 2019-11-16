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

sudo docker build -t=client:1.0 client_docker
sudo docker tag client:1.0 concrete13377/client:1.0
sudo docker push concrete13377/client:1.0

sudo docker build -t=namenode:1.0 namenode_docker
sudo docker tag namenode:1.0 concrete13377/namenode:1.0
sudo docker push concrete13377/namenode:1.0

sudo docker build -t=storage:1.0 storage_docker
sudo docker tag storage:1.0 concrete13377/storage:1.0
sudo docker push concrete13377/storage:1.0

# to deploy:
# docker swarm init
# docker stack deploy -c docker-compose.yml mydfs

# sudo docker stack rm mydfs
# sudo docker service ps mydfs_client