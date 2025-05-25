class Jogo:
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
        self.jogadas: set[tuple[int, int]] = set([(i, j) for j in range(self.tamanho) for i in range(self.tamanho)])

    def lista_jogadas(self) -> list[tuple[int, int]]:
        if not self.terminou:
            return list(self.jogadas)

        raise Exception('O jogo já terminou.')

    def joga(self, jogada: tuple[int, int]) -> None:
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
                    # Para cada peça do tabuleiro tenta estender linhas, colunas e diagonais
                    for x in [-1, 0, 1]:
                        for y in [-1, 0, 1]:
                            if x == 0 and y == 0:
                                continue

                            pontos = 1
                            a, b = i + x, j + y
                            while 0 <= a < self.tamanho and \
                                0 <= b < self.tamanho and \
                                self.tabuleiro[a][b] == self.tabuleiro[i][j]:
                                pontos += 1
                                if pontos == self.pontos_pra_ganhar:
                                    return self.tabuleiro[i][j]
                                a, b = a + x, b + y

        return None
