# MCTS no textual do jogo da velha

Parte da palestra que eu dei na Twitch no dia 25 de maio de 2025.

## Como executar?

1. Faça um clone do repositório.
2. Rode `poetry install`.
3. Rode `poetry run mcts`.

![Uma screenshot do programa](image.png)

## Ferramentas de desenvolvimento

### Lints

Para executar os lints do projeto, execute o comando:

```sh
poetry run task lint
```

Para corrigir os problemas de formatação, execute o comando:

```sh
poetry run task fmt
```

Para corrigir automaticamente os casos de lint possíveis, execute o comando:

```sh
poetry run task lint-fix
```
