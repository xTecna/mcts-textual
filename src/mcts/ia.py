from mcts.jogo import Jogo

from random import choice
from copy import deepcopy
from math import sqrt


class No:
    def __init__(self) -> None:
        self.pontuacao: float = 0.0
        self.visitas: int = 0

        self.pai: No | None = None
        self.filhos: dict[tuple[int, int], No] = {}

    def adiciona_filho(self, jogada: tuple[int, int]) -> None:
        filho = No()
        filho.pai = self

        self.filhos[jogada] = filho

    def adiciona_resultado(self, resultado: float) -> None:
        self.pontuacao = (self.pontuacao * self.visitas + resultado) / (self.visitas + 1)
        self.visitas += 1


class IA:
    def __init__(self, C: float, max_iteracoes: int) -> None:
        self.C = C
        self.max_iteracoes = max_iteracoes
        self.arvore = No()

    def escolhe_jogada(self, jogo: Jogo) -> tuple[int, int]:
        for _ in range(self.max_iteracoes):
            no_atual: No = self.arvore
            jogo_atual: Jogo = deepcopy(jogo)

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

    def selecao(self, no: No, jogo: Jogo) -> No:
        while not jogo.acabou() and len(no.filhos) == len(jogo.lista_jogadas()):
            melhor_jogada = None
            maior_intervalo = -1.0
            for jogada in no.filhos:
                filho = no.filhos[jogada]
                intervalo = filho.pontuacao + self.C * sqrt(no.visitas / filho.visitas)

                if intervalo > maior_intervalo:
                    maior_intervalo = intervalo
                    melhor_jogada = jogada

            if melhor_jogada is None:
                raise RuntimeError('Sem jogada disponível')

            no = no.filhos[melhor_jogada]
            jogo.joga(melhor_jogada)

        return no

    def expansao(self, no: No, jogo: Jogo) -> No:
        if jogo.acabou():
            return no

        jogadas = set(jogo.lista_jogadas()).difference(no.filhos.keys())
        jogada_escolhida = choice(list(jogadas))

        no.adiciona_filho(jogada_escolhida)
        jogo.joga(jogada_escolhida)

        return no.filhos[jogada_escolhida]

    def simulacao(self, jogo: Jogo) -> float:
        while not jogo.acabou():
            jogadas = jogo.lista_jogadas()
            jogada_escolhida = choice(jogadas)

            jogo.joga(jogada_escolhida)

        ganhador = jogo.ganhador()
        if ganhador is None:
            return 0.5
        return 1.0

    def retropropagacao(self, no: No | None, resultado: float) -> None:
        while no is not None:
            no.adiciona_resultado(resultado)
            no = no.pai
            resultado = 1.0 - resultado
