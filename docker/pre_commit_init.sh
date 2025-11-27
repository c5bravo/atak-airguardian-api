#!/bin/bash -l
if [ ! -d .git ]
then
  git init
  git checkout -b precommit_init
  git add .
  git reset rune
fi
set -e
poetry run pre-commit install
SKIP="poetry-lock" poetry run pre-commit run --all-files
