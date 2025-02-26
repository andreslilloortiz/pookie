# Using Clang with Docker

## Download the Docker Image
```bash
docker pull silkeh/clang
```

## Create and Run the Container
```bash
docker create -it --name my_clang_container -v $(pwd):/workspace silkeh/clang
docker start my_clang_container
```

## Access the Container
```bash
docker exec -it my_clang_container /bin/bash
```

## Update Packages in the Container
```bash
apt-get update
```

## Compile the Program
```bash
cd /workspace
clang cprogram.c -o cprogram
```

## Run the Program
```bash
./cprogram
``` 

## Stop the Container
```bash
docker stop my_clang_container
```
