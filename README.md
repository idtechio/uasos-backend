# Pre-install
- Install Docker

# Install
- `cd _build`
- `cp .env_example .env`
- `make install` (~3 min, 1.2GB)

# Running functions
Using HTTP requests:
- url: http://localhost:8060/[fnc-name]
- HTTP method: POST
- body (type json): `{ "data": { "data": "fnc params as JSON" } }`

_Yes, there is `body` inside `body` ;)_

Example:
- url: http://localhost:8060/hosts-insert
- body:
```json
{
  "data": {
    "data": "{\"phone_num\":\"+00123456789\", \"fnc_accounts_id\":\"00123456789\", \"email\":\"123@example.com\" }"
  }
}
```

You can run function from eg. Postman to check how it works or connect it with your local frontend application. Read more about that in README file for frontend app.
# Database

## Web Panel
Optional service, available only with `DC_PROFILES="standard,pgadmin"`
- PgAdmin (http://localhost:8050/)
- login/email and password are configured in `.env` file

## Useful commands
- `make db-up` - create db structure (it should be run on empty DB)
- `make db-clear` - remove all structures and data
- `make db-reset`- run clear & up

# Other Make cmds
- `make up` - start containers
- `make ps` - show containers
- `make restart` - restart containers
- `make stop` - stop containers
- `make down` - stop and remove containers
- `make recreate` - stop, remove, build and start containers
You can run `restart`, `stop` and `down` with param `s=NAME` for only one container

- `make exec s=NAME c=COMMAND` - run COMMAND in container NAME
- `make logs s=NAME` - show logs for container NAME

- `make install`
- `make reinstall`
- `make uninstall`

# Adding new function
1. Add `GCF_NAME="foo-bar" ./build.sh` to `build` target in `Makefile`
2. Add new container definition to `docker-compose.yml`:
```
foo-bar:
  image: ${PROJECT_NAME}-fnc-foo-bar:latest
  env_file:
    - .env
  expose:
    - "${FNC_DEFAULT_PORT}"
  environment:
    - PORT=${FNC_DEFAULT_PORT}
```
3. Add new server location in Nginx config file (`fnc.conf.template`):
```
location /foo-bar {
  proxy_pass http://foo-bar:${FNC_DEFAULT_PORT}/;
}
```