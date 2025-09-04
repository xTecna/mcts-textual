from copy import deepcopy
from math import sqrt
from random import choice

from mcts.jogo import Jogo


class No[Jogada]:
    def __init__(self) -> None:
        self.pontuacao: float = 0.0
        self.visitas: int = 0

        self.pai: No[Jogada] | None = None
        self.filhos: dict[Jogada, No[Jogada]] = {}

    def adiciona_filho(self, jogada: Jogada) -> None:
        filho = No[Jogada]()
        filho.pai = self

        self.filhos[jogada] = filho

    def adiciona_resultado(self, resultado: float) -> None:
        self.pontuacao = (self.pontuacao * self.visitas + resultado) / (self.visitas + 1)
        self.visitas += 1


class IA[Jogada]:
    def __init__(self, c: float, max_iteracoes: int) -> None:
        self.c = c
        self.max_iteracoes = max_iteracoes
        self.arvore = No[Jogada]()

    def escolhe_jogada(self, jogo: Jogo[Jogada]) -> Jogada:
        for _ in range(self.max_iteracoes):
            no_atual: No[Jogada] = self.arvore
            jogo_atual: Jogo[Jogada] = deepcopy(jogo)

            no_atual = self.selecao(no_atual, jogo_atual)
            no_atual = self.expansao(no_atual, jogo_atual)
            resultado = self.simulacao(jogo_atual)
            self.retropropagacao(no_atual, resultado)

        jogada_escolhida = None
        melhor_resultado = -1.0
        for jogada in self.arvore.filhos:
            filho = self.arvore.filhos[jogada]
            if filho.pontuacao > melhor_resultado:
                melhor_resultado = filho.pontuacao
                jogada_escolhida = jogada

        if jogada_escolhida is None:
            raise RuntimeError('Sem jogada disponível')

        return jogada_escolhida

    def selecao(self, no: No[Jogada], jogo: Jogo[Jogada]) -> No[Jogada]:
        while not jogo.acabou() and len(no.filhos) == len(jogo.lista_jogadas()):
            melhor_jogada = None
            maior_intervalo = -1.0
            for jogada in no.filhos:
                filho = no.filhos[jogada]
                intervalo = filho.pontuacao + self.c * sqrt(no.visitas / filho.visitas)

                if intervalo > maior_intervalo:
                    maior_intervalo = intervalo
                    melhor_jogada = jogada

            if melhor_jogada is None:
                raise RuntimeError('Sem jogada disponível')

            no = no.filhos[melhor_jogada]
            jogo.joga(melhor_jogada)

        return no

    def expansao(self, no: No[Jogada], jogo: Jogo[Jogada]) -> No[Jogada]:
        if jogo.acabou():
            return no

        jogadas = jogo.lista_jogadas().difference(no.filhos.keys())
        jogada_escolhida = choice(list(jogadas))

        no.adiciona_filho(jogada_escolhida)
        jogo.joga(jogada_escolhida)

        return no.filhos[jogada_escolhida]

    def simulacao(self, jogo: Jogo[Jogada]) -> float:
        while not jogo.acabou():
            jogadas = jogo.lista_jogadas()
            jogada_escolhida = choice(list(jogadas))

            jogo.joga(jogada_escolhida)

        ganhador = jogo.ganhador()
        if ganhador is None:
            return 0.5
        return 1.0

    def retropropagacao(self, no: No[Jogada] | None, resultado: float) -> None:
        while no is not None:
            no.adiciona_resultado(resultado)
            no = no.pai
            resultado = 1.0 - resultado
