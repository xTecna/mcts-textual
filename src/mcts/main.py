from mcts.tela import Tela, TelaLig4

C = 0.1
max_iteracoes = 1000
jogador_vai_primeiro = True
tamanho = 3
pontos_pra_ganhar = 3


def main() -> None:
    Tela(
        c=C,
        max_iteracoes=max_iteracoes,
        jogador_vai_primeiro=jogador_vai_primeiro,
        tamanho=tamanho,
        pontos_pra_ganhar=pontos_pra_ganhar,
    ).run()


def main_lig4() -> None:
    TelaLig4(
        c=C,
        max_iteracoes=max_iteracoes,
        jogador_vai_primeiro=jogador_vai_primeiro,
        colunas=7,
        linhas=6,
        casas_para_ganhar=4,
    ).run()


if __name__ == '__main__':
    main()
