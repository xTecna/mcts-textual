from abc import ABC, abstractmethod


class Jogo[Jogada](ABC):
    @abstractmethod
    def lista_jogadas(self) -> set[Jogada]:
        raise NotImplementedError

    @abstractmethod
    def joga(self, jogada: Jogada) -> None:
        raise NotImplementedError

    @abstractmethod
    def acabou(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def ganhador(self) -> bool | None:
        raise NotImplementedError


JogadaJogoDaVelha = tuple[int, int]


class JogoDaVelha(Jogo[JogadaJogoDaVelha]):
    def __init__(self, tamanho: int, pontos_pra_ganhar: int) -> None:
        if tamanho <= 0:
            raise Exception('O tamanho passado não é válido.')
        if pontos_pra_ganhar <= 1 or pontos_pra_ganhar > tamanho:
            raise Exception('A quantidade de pontos pra ganhar passada não é válida.')

        self.terminou: bool = False
        self.jogador: bool = True
        self.tamanho: int = tamanho
        self.pontos_pra_ganhar: int = pontos_pra_ganhar
        self.tabuleiro: list[list[bool | None]] = [[None for j in range(self.tamanho)] for i in range(self.tamanho)]
        self.jogadas: set[JogadaJogoDaVelha] = {(i, j) for j in range(self.tamanho) for i in range(self.tamanho)}

    def lista_jogadas(self) -> set[JogadaJogoDaVelha]:
        if not self.terminou:
            return self.jogadas

        raise Exception('O jogo já terminou.')

    def joga(self, jogada: JogadaJogoDaVelha) -> None:
        x, y = jogada
        if jogada not in self.jogadas or self.tabuleiro[x][y] is not None:
            raise Exception('A jogada não é válida.')

        self.jogadas.remove(jogada)
        self.tabuleiro[x][y] = self.jogador
        self.jogador = not self.jogador

        if not self.jogadas or self.ganhador() is not None:
            self.terminou = True

    def acabou(self) -> bool:
        return self.terminou

    def ganhador(self) -> bool | None:
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if self.tabuleiro[i][j] is not None:
                    # Para cada peça do tabuleiro tenta estender linha, coluna e as duas diagonais
                    for x, y in [(0, 1), (1, 0), (1, 1), (-1, 1)]:
                        pontos = 1
                        a, b = i + x, j + y
                        while (
                            0 <= a < self.tamanho
                            and 0 <= b < self.tamanho
                            and self.tabuleiro[a][b] == self.tabuleiro[i][j]
                        ):
                            pontos += 1
                            if pontos == self.pontos_pra_ganhar:
                                return self.tabuleiro[i][j]
                            a, b = a + x, b + y

        return None


JogadaLig4 = int


class Lig4(Jogo[JogadaLig4]):
    def __init__(self, colunas: int, linhas: int, casas_pra_ganhar: int) -> None:
        if colunas <= 0:
            raise ValueError('Quantidade de colunas inválida')
        if linhas <= 0:
            raise ValueError('Quantidade de linhas inválida')
        if casas_pra_ganhar <= 1 or (casas_pra_ganhar > linhas and casas_pra_ganhar > colunas):
            raise ValueError('Quantidade de casas para ganhar inválida')

        self.vencedor: bool | None = None
        self.jogador = True
        self.colunas = colunas
        self.linhas = linhas
        self.casas_pra_ganhar = casas_pra_ganhar
        self.tabuleiro: list[list[bool | None]] = [[None for _ in range(linhas)] for _ in range(colunas)]
        self.jogadas = 0

    def lista_jogadas(self) -> set[JogadaLig4]:
        if self.acabou():
            raise RuntimeError('O jogo já terminou')

        return {i for i, coluna in enumerate(self.tabuleiro) if coluna.count(None) != 0}

    def joga(self, jogada: JogadaLig4) -> None:
        if self.tabuleiro[jogada].count(None) == 0:
            raise ValueError('Jogada não é válida')

        casa = self.tabuleiro[jogada].index(None)
        self.tabuleiro[jogada][casa] = self.jogador
        self.vencedor = self._verifica_ganhador(jogada, casa)
        self.jogador = not self.jogador
        self.jogadas += 1

    def _verifica_ganhador(self, coluna: int, linha: int) -> bool | None:
        ligs = [[0 for _ in range(3)] for _ in range(3)]
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                if x == 0 and y == 0:
                    continue
                pontos = 0
                a = coluna + x
                b = linha + y
                while (
                    0 <= a < self.colunas
                    and 0 <= b < self.linhas
                    and self.tabuleiro[a][b] == self.tabuleiro[coluna][linha]
                ):
                    pontos += 1
                    a += x
                    b += y
                ligs[x + 1][y + 1] = pontos
        if (
            ligs[0][0] + ligs[2][2] + 1 >= self.casas_pra_ganhar
            or ligs[1][0] + ligs[1][2] + 1 >= self.casas_pra_ganhar
            or ligs[2][0] + ligs[0][2] + 1 >= self.casas_pra_ganhar
            or ligs[0][1] + ligs[2][1] + 1 >= self.casas_pra_ganhar
        ):
            return self.tabuleiro[coluna][linha]
        return None

    def acabou(self) -> bool:
        return self.vencedor is not None or self.jogadas == self.colunas * self.linhas

    def ganhador(self) -> bool | None:
        return self.vencedor
