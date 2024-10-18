# python-norduniclient

[![PyPI](https://img.shields.io/pypi/v/norduniclient.svg)](https://pypi.python.org/pypi/norduniclient)

Neo4j database client for NORDUnet network inventory

## Compatibility

| Tools       | Version   |
| ----------- | --------- |
| neo4j DB    | 4.4.x     |
| neo4j       | 4.4.x     |
| neomodel    | 5.0.x     |

## Setup

```
poetry shell
poetry install
```

## Running tests

Add the following environment variables:

```env
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
NEO4J_HOSTNAME=xx
NEO4J_USER=xx
NEO4J_PASSWORD=xx
```

and run

```bash
poetry run python -m unittest discover
```

or save the environment variables in a local file `.env` and run it with [dotenvx](https://dotenvx.com/) as follows:

```bash
dotenvx run -- poetry run python -m unittest discover
```

or

```bash
nox -rs tests
```

```bash
nox -rs tests_dotenv
```

## Installation

```bash
pip install norduniclient
```

python3 -m pip install --index-url <https://platform.sunet.se/api/packages/benedith/pypi/simple/> --extra-index-url <https://pypi.org/simple/> norduniclient

python3 -m pip install -i <https://test.pypi.org/simple/> --extra-index-url <https://pypi.org/simple/> jolieprinter

## Usage

```python
import norduniclient as nc

NODE_META_TYPE_CHOICES = zip(nc.META_TYPES, nc.META_TYPES)

print("nc.META_TYPES=", nc.META_TYPES)
```

### Poetry guide

```
poetry run python [operation]
```

### Add depenency

#### Add a new lib

```bash
poetry add <library>
```

#### Remove a lib

```bash
poetry remove <library>
```

#### Get venv path

```bash
poetry run which python
```

#### Show dependencies

```bash
poetry show
```
                                                                                
```bash
poetry run pip list
```

#### List configuratiom

```bash
poetry config --list
```

### Publish

```bash
poetry config repositories.pypi https://upload.pypi.org/legacy/
poetry config pypi-token.pypi [token]
poetry publish --build --repository pypi
poetry publish --build --repository testpypi
```
