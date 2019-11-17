
sudo docker build -t=client:2.0 client_docker
sudo docker tag client:2.0 concrete13377/client:2.0
sudo docker push concrete13377/client:2.0

sudo docker build -t=namenode:2.0 namenode_docker
sudo docker tag namenode:2.0 concrete13377/namenode:2.0
sudo docker push concrete13377/namenode:2.0

sudo docker build -t=storage:2.0 storage_docker
sudo docker tag storage:2.0 concrete13377/storage:2.0
sudo docker push concrete13377/storage:2.0

# to deploy: doesnt really works yet, use run_locally.sh
# docker swarm init
# docker stack deploy -c docker-compose.yml mydfs

# sudo docker stack rm mydfs
# sudo docker service ps mydfs_client