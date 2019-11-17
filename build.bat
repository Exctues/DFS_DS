set VERSION="3.1"
set USER="danieldv99"

docker build -t=client:%VERSION% -f docker/client_dockerfile .
docker tag client:%VERSION% %USER%/client:%VERSION%
docker push %USER%/client:%VERSION%

docker build -t=namenode:%VERSION% -f docker/namenode_dockerfile .
docker tag namenode:%VERSION% %USER%/namenode:%VERSION%
docker push %USER%/namenode:%VERSION%

docker build -t=storage:%VERSION% -f docker/storage_dockerfile .
docker tag storage:%VERSION% %USER%/storage:%VERSION%
docker push %USER%/storage:%VERSION%
