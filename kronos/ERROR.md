If you having trouble using the gpu in the docker.

try this in the docker :
```sh
nvidia-smi
```

if you have this 

```
Failed to initialize NVML: Unknown Error
```

Try this 

```sh
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

if same error ask chatgpt, migh have to reinstall nvidia



