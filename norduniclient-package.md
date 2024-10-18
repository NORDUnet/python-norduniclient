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

```bash
poetry shell
poetry install
```

## Running tests

Add the following environment variables:

```bash
NEO4J_HTTP_PORT=7474
NEO4J_BOLT_PORT=7687
NEO4J_HOSTNAME=xx
NEO4J_USER=xx
NEO4J_PASSWORD=xx
```

```bash
poetry run python -m unittest discover
```

## Installation

```bash
pip install norduniclient
```

## Usage

```python
import norduniclient as nc

NODE_META_TYPE_CHOICES = zip(nc.META_TYPES, nc.META_TYPES)

print("nc.META_TYPES=", nc.META_TYPES)
```
