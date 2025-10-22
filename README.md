---
title: gradio-experiments
emoji: 🔬
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: 5.49.1
suggested_hardware: cpu-basic
app_file: src/gradio_experiments/app.py
pinned: true
disable_embedding: true
license: mit
short_description: A collection of feature experiments with Gradio
---

[![Sync to Hugging Face hub](https://github.com/anirbanbasu/gradio-experiments/actions/workflows/hfspaces.yml/badge.svg)](https://github.com/anirbanbasu/gradio-experiments/actions/workflows/hfspaces.yml) ![Status experimental](https://img.shields.io/badge/Status-experimental-yellow)

# gradio-experiments

A collection of feature experiments with Gradio.

## Environment variables

You can specify the following environment variables in a `.env`, for example. In addition to those, [Gradio environment variables](https://www.gradio.app/guides/environment-variables) can also be specified but `GRADIO_SERVER_NAME` (set to "0.0.0.0"), `GRADIO_SHARE` (set to False) and `GRADIO_ANALYTICS_ENABLED` (set to False) will be ignored.


| Variable       | Default value | Description             |
|----------------|---------------|-------------------------|
| LOCAL_STORAGE_ENCRYPTION_KEY    | None | If you want to be able read from previously saved local storage on the browser, you must specify this environment variable. If it is not specified, a new value is generated for a browser session. |

## Installation and use

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/). Then, run `uv sync` (with the `--all-groups` flag to install developer and test dependencies). Once dependencies are installed, you can start the Gradio server by running `uv run gre` or `uv run python src/gradio_experiments/app.py`. If the server is able to start without any problem, it will be listening to port 7860 on any IP address of your network adapter. You will be able to see the web interface on your localhost at http://127.0.0.1:7860/.

A public deployment may be available through Huggingface Spaces at: https://huggingface.co/spaces/anirbanbasu/gradio-experiments.

## Status

The following features have been or are being implemented.

| Feature | Description | Status |
|---------|-------------|--------|
| JSON display | The JSON component is unable to display a formatted JSON string correctly. | Bug reported in [issue 11592](https://github.com/gradio-app/gradio/issues/11592) and fixed in [pull request 11608](https://github.com/gradio-app/gradio/pull/11608). |
| State management | Demonstration of global, session and browser (local) states. | Completed |
| Datasets | Experimentation with datasets and data frames. | Preliminary stage |
| Pydantic enitity profile | Experimentation with Pydantic based entity profiles. | Partially implemented |
| Text transformation | Just a placeholder. | Completed |
