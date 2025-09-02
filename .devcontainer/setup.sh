#!/bin/bash

set -xe

mkdir -p ~/.local/share/bash-completion/completions
pipx install argcomplete

# Configura python
echo '. <(pip completion --bash)' > ~/.local/share/bash-completion/completions/pip
echo '. <(register-python-argcomplete pipx)' > ~/.local/share/bash-completion/completions/pipx

# Configura poetry
pipx install poetry==2.1.4
poetry config virtualenvs.in-project true
[ -e .venv ] || poetry env use /usr/local/bin/python
echo '.  <(poetry completions bash)' > ~/.local/share/bash-completion/completions/poetry

# Configura projeto
poetry install
