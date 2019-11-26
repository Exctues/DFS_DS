# DFS_DS

### DFS - Distributed File System
It is a remote file system where you have 3 main entities: client, namenode, storage.   
Client is a guy who works with system: create folders, uploads\download files and so on.  
System works in master-slave fashion. Namenode is master and storages are slaves.  
It is written in Python using sockets.  


#### Communication protocol:  
in src/utils/codes.py there are codes that client sends to namenode and namenode sends to storages in order to execute one of  the scenarios:
``` exit = -10
    help = -3
    cd = -2
    pwd = -1
    init = 0
    make_file = 1
    print = 2
    upload = 3
    rm = 4
    info = 5
    copy = 6
    move = 7
    ls = 8
    make_dir = 9
    rmdir = 10
    validate_path = 11 # checks if path exists in namenode tree (only client uses)
    is_dir = 12 # checks if path file or directory in namenode tree (only client uses)
    get_all_storage_ips = 12 # storage node sends to namenode in order to request all ips to distribute file
    init_new_storage = 13 # new storage node appears sends it to namenode to get ip of storage and download all data from it
    download_all = 14 # storage node request downloading of all files from another storage node to restore consistency
    i_clear = 15 # new storage node tells namenode that it is clear and may be moved to set of clear nodes
```
send command and before each argument send acknowledgement

#### How to use:
* local network, at least 2 machine (or adjust docker-compose to run on 1 machine)
* ```docker swarm init``` on manager and join another nodes to it  
* on manager node ```docker network create --driver overlay mynetwork```  
* copy docker-compose.yml to manager
* ```docker stack deploy -c docker-compose.yml mydfs``` on manager to deploy 
* adjust number of storage nodes in docker-compose.yml
* ```docker stack rm mydfs``` to remove stack

to run client: 
* specify namenode ip to public ip address of machine where namenode is in utils/constants.py
* ```docker run -it danieldv99/client:3.2 /bin/sh``` and ```python3 client.py``` inside container
* or alternatively just run client.py

#### Architecture
![](https://i.imgur.com/tgcBVNw.png)


Project exists because of 3 people:  
Alexander Andryukov,  
Daniil Dvoryanov,  
Roman Bogachev.  
