import os
import nox


@nox.session(python=["3.9"])
def tests(session):
    # Install dev dependencies
    session.install("neo4j==4.4.12")
    # Set environment variables using os.environ
    os.environ["NEO4J_HTTP_PORT"] = "7476"
    os.environ["NEO4J_BOLT_PORT"] = "7689"
    os.environ["NEO4J_HOSTNAME"] = "localhost"
    os.environ["NEO4J_USER"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = ""
    session.run("python", "-m", "unittest", "discover", "-s", "tests")


@nox.session(python=["3.9"])
def tests_dotenv(session):
    session.install("neo4j==4.4.12")
    session.run("dotenvx", "run", "--", "python", "-m", "unittest", "discover", "-s", "tests")


@nox.session(python=["3.9"])
def lint(session):
    session.install("flake8")
    session.install("flake8-pyproject")
    session.run("flake8", "norduniclient")


@nox.session(python=["3.9"])
def typecheck(session):
    session.install("mypy")
    session.run("mypy", "norduniclient")


@nox.session(python=["3.9"])
def format(session):
    session.install("black")
    session.run("black", "--check", "norduniclient")
