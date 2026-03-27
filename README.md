<hr>

```
docker build -t s-image .
docker rm -f s-container
docker run -d --name s-container --add-host host.docker.internal:host-gateway --env-file .env s-image
```

<hr>

`docker pause s-container`

`docker unpause s-container`
