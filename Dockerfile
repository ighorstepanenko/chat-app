ARG PYTHON_BASE=python:3.12-slim

########## Build stage ##########
FROM $PYTHON_BASE AS builder

ENV PDM_CHECK_UPDATE=false
ENV PDM_VENV_IN_PROJECT=true
ENV HOME=/srv/project

RUN mkdir $HOME && pip install --no-cache-dir pdm
COPY pyproject.toml pdm.lock $HOME/

WORKDIR $HOME
RUN pdm install --check --prod --no-editable

########## Run stage ##########
FROM $PYTHON_BASE

ENV HOME=/srv/project
ENV TZ=Europe/Moscow
ENV PYTHONPATH="$PYTHONPATH:$HOME"
ENV PATH="$HOME/.venv/bin:$PATH"

RUN groupadd --gid 1000 project \
    && useradd \
        --system \
        --create-home \
        --no-log-init \
        --home-dir $HOME \
        --gid project \
        --uid 1000 \
        --shell /bin/bash \
        project \
    && chown project:project $HOME

WORKDIR $HOME
USER project

COPY --chown=project:project --from=builder $HOME/.venv $HOME/.venv

COPY --chown=project:project app $HOME/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
