# PipelineWise

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pipelinewise-tap-mysql.svg)](https://pypi.org/project/pipelinewise-tap-mysql/)
[![License: Apache2](https://img.shields.io/badge/License-Apache2-yellow.svg)](https://opensource.org/licenses/Apache-2.0)

PipelineWise is a Data Pipeline Framework using the [Singer.io](https://www.singer.io/) specification to ingest and replicate data from various sources to various destinations.
Documentation is available at https://transferwise.github.io/pipelinewise/

![Logo](docs/img/pipelinewise-diagram-circle-bold.png)


## Features

* **Built with ELT in mind**: PipelineWise fits into the ELT landscape but does not do traditional ETL. PipelineWise ingests data first into DWH in the original format and the “transformation” shifts to the end of the data pipeline. Load time transformations are still supported but complex mapping and joins have to be done once the data is replicated into the Data Warehouse.
* **Replication Methods**: CDC (Log Based), Key-Based Incremental and Full Table snapshots
* **Managed Schema Changes**: When source data changes, PipelineWise detects the change and alters the schema in your DWH automatically
* **Load time transformations**: Ideal place to obfuscate, mask or filter sensitive data that should never be replicated in the Data Warehouse
* **YAML based configuration**: Data pipelines are defined as YAML files, ensuring that the entire configuration is kept under version control
* **Lightweight**: No daemons or database setup are required
* **Extensible**: PipelineWise is using [Singer.io](https://www.singer.io/) compatible taps and target connectors. New connectors can be added to PipelineWise with relatively small effort


## Table of Contents

- [Connectors](#connectors)
    - [Running from docker](#running-from-docker)
    - [Building from source](#building-from-source)
- [Developing with Docker](#developing-with-docker)
- [Links](#links)
- [License](#license)


## Connectors

Tap extracts data from any source and write it to a standard stream in a JSON-based format, and target
consumes data from taps and do something with it, like load it into a file, API or database

| Type      | Name       | Latest Version | Description                                          |
|-----------|------------|----------------|------------------------------------------------------|
| Tap       | **[Postgres](https://github.com/transferwise/pipelinewise-tap-postgres)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-tap-postgres.svg)](https://badge.fury.io/py/pipelinewise-tap-postgres) | Extracts data from PostgreSQL databases. Supporting Log-Based Inremental, Key-Based Incremental and Full Table replications |
| Tap       | **[MySQL](https://github.com/transferwise/pipelinewise-tap-mysql)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-tap-mysql.svg)](https://badge.fury.io/py/pipelinewise-tap-mysql) | Extracts data from MySQL databases. Supporting Log-Based Inremental, Key-Based Incremental and Full Table replications |
| Tap       | **[Oracle](https://github.com/transferwise/pipelinewise-tap-oracle)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-tap-oracle.svg)](https://badge.fury.io/py/pipelinewise-tap-oracle) | Extracts data from Oracle databases. Supporting Log-Based Inremental, Key-Based Incremental and Full Table replications |
| Tap       | **[Kafka](https://github.com/transferwise/pipelinewise-tap-kafka)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-tap-kafka.svg)](https://badge.fury.io/py/pipelinewise-tap-kafka) | Extracts data from Kafka topics |
| Tap       | **[AdWords](https://github.com/singer-io/tap-adwords)** | [![PyPI version](https://badge.fury.io/py/tap-adwords.svg)](https://badge.fury.io/py/tap-adwords) | Extracts data Google Ads API (former Google Adwords) using OAuth and support incremental loading based on input state |
| Tap       | **[S3 CSV](https://github.com/transferwise/pipelinewise-tap-s3-csv)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-tap-s3-csv.svg)](https://badge.fury.io/py/pipelinewise-tap-s3-csv) | Extracts data from S3 csv files (currently a fork of tap-s3-csv because we wanted to use our own auth method) |
| Tap       | **[Zendesk](https://github.com/singer-io/tap-zendesk)** | [![PyPI version](https://badge.fury.io/py/tap-zendesk.svg)](https://badge.fury.io/py/tap-zendesk) | Extracts data from Zendesk using OAuth and Key-Based incremental replications |
| Tap       | **[Snowflake](https://github.com/transferwise/pipelinewise-tap-snowflake)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-tap-snowflake.svg)](https://badge.fury.io/py/pipelinewise-tap-snowflake) | Extracts data from Snowflake databases. Supporting Key-Based Incremental and Full Table replications |
| Tap       | **[Salesforce](https://github.com/singer-io/tap-salesforce)** | [![PyPI version](https://badge.fury.io/py/tap-salesforce.svg)](https://badge.fury.io/py/tap-zendesk) | Extracts data from Salesforce database using BULK and REST extraction API with Key-Based incremental replications |
| Tap       | **[Jira](https://github.com/singer-io/tap-jira)** | [![PyPI version](https://badge.fury.io/py/tap-jira.svg)](https://badge.fury.io/py/tap-jira) | Extracts data from Atlassian Jira using Base auth or OAuth credentials |
| Target    | **[Postgres](https://github.com/transferwise/pipelinewise-target-postgres)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-target-postgres.svg)](https://badge.fury.io/py/pipelinewise-target-postgres) | Loads data from any tap into PostgreSQL database |
| Target    | **[Redshift](https://github.com/transferwise/pipelinewise-target-redshift)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-target-redshift.svg)](https://badge.fury.io/py/pipelinewise-target-redshift) | Loads data from any tap into Amazon Redshift Data Warehouse |
| Target    | **[Snowflake](https://github.com/transferwise/pipelinewise-target-snowflake)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-target-snowflake.svg)](https://badge.fury.io/py/pipelinewise-target-snowflake) | Loads data from any tap into Snowflake Data Warehouse |
| Target    | **[S3 CSV](https://github.com/transferwise/pipelinewise-target-s3-csv)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-target-s3-csv.svg)](https://badge.fury.io/py/pipelinewise-target-s3-csv) | Uploads data from any tap to S3 in CSV format |
| Transform | **[Field](https://github.com/transferwise/pipelinewise-transform-field)** | [![PyPI version](https://badge.fury.io/py/pipelinewise-transform-field.svg)](https://badge.fury.io/py/pipelinewise-transform-field) | Transforms fields from any tap and sends the results to any target. Recommended for data masking/ obfuscation |


### Running from docker

If you have [Docker](https://www.docker.com/) installed then using docker is the easiest and
recommended method of start using PipelineWise.

1. Build an executable docker images that has every required dependency and it's isolated from your host system:

    ```sh
    $ docker build -t pipelinewise:latest .
    ```

2. Once the image is ready, create an alias to the docker wrapper script:

    ```sh
    $ alias pipelinewise="$(PWD)/bin/pipelinewise-docker"
    ```

3. Check if the installation was successfully by running the `pipelinewise status` command:

    ```sh
    $ pipelinewise status
    
    Tap ID    Tap Type      Target ID     Target Type      Enabled    Status    Last Sync    Last Sync Result
    --------  ------------  ------------  ---------------  ---------  --------  -----------  ------------------
    0 pipeline(s)
    ```

You can run any pipelinewise command at this point. Tutorials to create and run pipelines is at https://transferwise.github.io/pipelinewise/installation_guide/creating_pipelines.html .

**PS**: 

For the tests to work, run the commands inside a PipelineWise container.
To create, start and get a bash shell in the container:

```sh
$ docker-compose up -d pipelinewise
$ docker exec -it pipelinewise_dev bash
```


### Building from source

1. Make sure that every dependencies installed on your system:
    * Python 3.x
    * python3-dev
    * python3-venv
    * postgresql

2. Run the install script that installs the PipelineWise CLI and every supported singer connectors into separated virtual environments:
   
    ```sh
    $ ./install.sh
    ```
    Press `Y` to accept the license agreement of the required singer components. To automate the installation and accept every license agreement run `./install --acceptlicenses`)

3. To start CLI you need to activate the CLI virtual environment and has to set `PIPELINEWISE_HOME` environment variable:
   
    ```sh
    $ source {ACTUAL_ABSOLUTE_PATH}/.virtualenvs/pipelinewise/bin/activate
    $ export PIPELINEWISE_HOME={ACTUAL_ABSOLUTE_PATH}
    ```
    (The `ACTUAL_ABSOLUTE_PATH` differs on every system, the install script prints you the correct command that fits
    to your system once the installation completed)

4. Check if the installation was successfully by running the `pipelinewise status` command:

    ```sh
    $ pipelinewise status
    
    Tap ID    Tap Type      Target ID     Target Type      Enabled    Status    Last Sync    Last Sync Result
    --------  ------------  ------------  ---------------  ---------  --------  -----------  ------------------
    0 pipeline(s)
    ```

You can run any pipelinewise command at this point. Tutorials to create and run pipelines is at https://transferwise.github.io/pipelinewise/installation_guide/creating_pipelines.html .

To run unit tests:

```sh
$ pytest --ignore tests/end-to-end
```
**Note**: End-to-end tests are ignored because it requires specific environment with source
and target databases. You need to use the docker development environment to run end to end tests.
Read more details at [Developing with Docker](#developing-with-docker).

To run unit tests and generate code coverage:

```
$ coverage run -m pytest --ignore tests/end-to-end && coverage report
```

To generate HTML coverage report.

```
$ coverage run -m pytest --ignore tests/end-to-end && coverage html -d coverage_html
```

**Note**: The HTML report will be generated in `coverage_html/index.html`


## Developing with Docker

If you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed,
you can create a local development environment that includes not only the PipelineWise executables but a
pre-configured development project as well with some databases as source and targets for a more convenient
development experience.

For further instructions about setting up local development environment go to
[Test Project for Docker Development Environment](dev-project/README.md).


## Contribution

To add new taps and targets follow the instructions on
[Contribution Page](https://transferwise.github.io/pipelinewise/project/contribution.html)


## Links

* [PipelineWise documentation](https://transferwise.github.io/pipelinewise/)
* [Singer ETL specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md)
* [Singer.io community slack channel](https://singer-slackin.herokuapp.com/)


## License

Apache License Version 2.0

See [LICENSE](LICENSE) to see the full text.

