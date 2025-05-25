from mcts.tela import Tela

from math import sqrt

C = 0.1
max_iteracoes = 1000
jogador_vai_primeiro = True
tamanho = 3
pontos_pra_ganhar = 3

if __name__ == '__main__':
    Tela(
        C=C, \
        max_iteracoes=max_iteracoes, \
        jogador_vai_primeiro=jogador_vai_primeiro, \
        tamanho=tamanho, \
        pontos_pra_ganhar=pontos_pra_ganhar).run()
