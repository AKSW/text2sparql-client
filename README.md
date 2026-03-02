# text2sparql-client

Command Line Client to retrieve SPARQL results from a TEXT2SPARQL conform endpoint.

[![workflow](https://github.com/aksw/text2sparql-client/actions/workflows/check.yml/badge.svg)](https://github.com/aksw/text2sparql-client/actions) [![pypi version](https://img.shields.io/pypi/v/text2sparql-client)](https://pypi.org/project/text2sparql-client) [![license](https://img.shields.io/pypi/l/text2sparql-client)](https://pypi.org/project/text2sparql-client)
[![poetry][poetry-shield]][poetry-link] [![ruff][ruff-shield]][ruff-link] [![mypy][mypy-shield]][mypy-link] [![copier][copier-shield]][copier] 

## Development

- Run [task](https://taskfile.dev/) to see all major development tasks.
- Use [pre-commit](https://pre-commit.com/) to avoid errors before commit.
- This repository was created with [this copier template](https://github.com/eccenca/cmem-plugin-template).


[poetry-link]: https://python-poetry.org/
[poetry-shield]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json
[ruff-link]: https://docs.astral.sh/ruff/
[ruff-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&label=Code%20Style
[mypy-link]: https://mypy-lang.org/
[mypy-shield]: https://www.mypy-lang.org/static/mypy_badge.svg
[copier]: https://copier.readthedocs.io/
[copier-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json


## Commands Reference

This portion describes all available CLI commands in the text2sparql-client.


### serve

Provide a TEXT2SPARQL testing endpoint. Serves as a simple reference implementation for testing purposes.

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--port` | Integer | `8000` | The port to listen on |
| `--host` | String | `127.0.0.1` | Bind socket to this host. Use `0.0.0.0` to make the endpoint available on your local network |
| `--sleep` | Integer | `0` | How long to sleep (in seconds) before answering (for testing purposes) |

#### Example

```bash
text2sparql serve --port 8000 --host 0.0.0.0
```

---


### ask

Query a TEXT2SPARQL endpoint using a questions YAML file and send each question to the endpoint. Creates a SQLite database to cache responses.

#### Arguments

| Name | Type | Description |
|------|------|-------------|
| `QUESTIONS_FILE` | File | YAML file containing the questions to ask |
| `URL` | String | TEXT2SPARQL endpoint URL to query |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--answers-db` | Path | `responses.db` | Where to save the endpoint responses (SQLite database) |
| `--timeout` | Integer | `600` | Timeout in seconds for each request |
| `--retries` / `-r` | Integer | `5` | Number of retries for disconnected, http error and timed out requests |
| `--retry-sleep` | Integer | `15` | Seconds to sleep between retries |
| `--retries-log` | Path | `retries.log` | File to log retries to |
| `--output` / `-o` | Path | `-` (stdout) | Save JSON output to this file |
| `--cache` / `--no-cache` | Boolean | `True` | If possible, return a cached response from the answers database |

#### Example

```bash
text2sparql ask questions.yml http://localhost:8000 -o answers.json
```

---


### query

Query an RDF endpoint with SPARQL queries from the questions file or answers file. Generates result sets for evaluation purposes.

#### Arguments

| Name | Type | Description |
|------|------|-------------|
| `QUESTIONS_FILE` | File | YAML file containing the questions with SPARQL queries |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--answers_file` / `-a` | File | None | File containing automatically generated answers. If provided, generates predicted result set instead of true result set |
| `--endpoint` / `-e` | String | `http://141.57.8.18:9080/sparql` | RDF endpoint URL for the dataset |
| `--output` / `-o` | Path | `-` (stdout) | File to save the result set (JSON) |
| `--languages` / `-l` | List | `['en']` | List of languages represented in the QUESTIONS_FILE |

#### Example

```bash
text2sparql query questions.yml -e http://localhost:9080/sparql -o result_set.json
```


---


### evaluate

Evaluate results from a TEXT2SPARQL endpoint by comparing predicted answers against a ground truth set.

#### Arguments

| Name | Type | Description |
|------|------|-------------|
| `API_NAME` | String | Name/identifier for the API being evaluated |
| `TRUE_SET` | File | JSON file containing the ground truth result set |
| `PRED_SET` | File | JSON file containing the predicted result set from the API |

#### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output` / `-o` | Path | `-` (stdout) | File to save the evaluation results (JSON) |
| `--languages` / `-l` | List | `['en']` | List of languages to generate separate metric results for |

#### Example

```bash
text2sparql evaluate my-api true_results.json predicted_results.json -o metrics.json -l "['en', 'es']"
```

---


### Common Features

#### Output Options

Ask, query and evaluate support the `--output` / `-o` option:
- Specify a file path to save output to a file
- Use `-` or omit the option to write to stdout
- The command will refuse to overwrite existing files

#### Language Support

Query and evaluate support multiple languages using the `--languages` / `-l` option:
- Provide a Python-style list string: `"['en', 'es']"`
- Default is English only: `['en']`
- Used to generate separate metrics per language in evaluation
