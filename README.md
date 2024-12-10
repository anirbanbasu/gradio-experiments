---
title: gradio-experiments
emoji: 🔬
colorFrom: gray
colorTo: blue
sdk: gradio
sdk_version: 5.8.0
suggested_hardware: cpu-basic
app_file: src/app.py
pinned: true
disable_embedding: true
license: gpl-3.0
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

Create a Python virtual environment for Python 3.12.0 or above. In that virtual environment, run `pip install -U -r requirements.txt`. (You can clean everything you have installed in that environment by running `python -m pip freeze | cut -d "@" -f1 | xargs pip uninstall -y`.) Once all the packages are installed, you can start the Gradio server by running `python src/app.py`. If the server is able to start without any problem, it will be listening to port 7860 on any IP address of your network adapter. You will be able to see the web interface on your localhost at http://127.0.0.1:7860/.

A public deployment may be available through Huggingface Spaces.

## Status

The following features have been or are being implemented.

| Feature | Description | Status |
|---------|-------------|--------|
| State management | Demonstration of global, session and browser (local) states. | Completed |
| Datasets | Experimentation with datasets and data frames. | Preliminary stage |
| Pydantic enitity profile | Experimentation with Pydantic based entity profiles. | Partially implemented |
| Text transformation | Just a placeholder. | Completed |
