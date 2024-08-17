# GQL_Forms

## Execution
```bash
uvicorn main:app --env-file environment.txt --port 8001 --log-level info --reload
```

```bash
pytest --cov-report term-missing --cov=DBDefinitions --cov=GraphTypeDefinitions --cov=utils --log-cli-level=INFO -x
```


```bash
python -m pydoc GraphTypeDefinitions
```

## Environment variables

### DB related variables
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=example
- POSTGRES_HOST=postgres:5432
- POSTGRES_DB=data

### Authorization related variables
- JWTPUBLICKEYURL=http://localhost:8000/oauth/publickey
- JWTRESOLVEUSERPATHURL=http://localhost:8000/oauth/userinfo
- ROLELISTURL=http://localhost:8088/gql/
- RBACURL=http://localhost:8088/gql

### 
- DEMO=true


## Docker compose

```yaml

```