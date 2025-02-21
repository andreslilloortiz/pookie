# Using Clang with Docker

## Download the Docker Image
```bash
docker pull silkeh/clang
```

## Run the Container
```bash
docker run -it --name my_clang_container -v $(pwd):/workspace silkeh/clang
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