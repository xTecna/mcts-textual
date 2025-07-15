from mcts.jogo import Jogo
from mcts.ia import No, IA

from queue import Queue
from typing import TYPE_CHECKING, cast

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.coordinate import Coordinate
from textual.widgets import *
from textual import on

if TYPE_CHECKING:
    from textual.widgets._tree import TreeNode


class Tela(App[None]):
    CSS_PATH = './styles/tela.tcss'
    BINDINGS = [
        ('x', 'exit', 'Sair'),
        ('r', 'restart', 'Reiniciar'),
        ('t', 'swap_players', 'Troca jogadores'),
        ('f', 'easier', 'Mais fácil'),
        ('d', 'harder', 'Mais difícil'),
    ]

    def __init__(
        self,
        C: float,
        max_iteracoes: int,
        jogador_vai_primeiro: bool,
        tamanho: int,
        pontos_pra_ganhar: int,
    ) -> None:
        self.C = C
        self.max_iteracoes = max_iteracoes
        self.jogador = jogador_vai_primeiro
        self.tamanho = tamanho
        self.pontos_pra_ganhar = pontos_pra_ganhar
        self.jogo = Jogo(tamanho, pontos_pra_ganhar)

        self.pausado = False
        self.simbolos = {None: ' ', False: 'O', True: 'X'}

        super().__init__()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == 'exit':
            return True
        if action in ('restart', 'swap_players', 'easier', 'harder'):
            return not self.pausado
        return True

    def action_exit(self) -> None:
        self.exit(None)

    async def action_restart(self) -> None:
        await self.set_start()

    async def action_swap_players(self) -> None:
        self.jogador = not self.jogador
        await self.set_start()

    def action_easier(self) -> None:
        self.max_iteracoes = max(1, self.max_iteracoes // 2)
        cast(Label, self.query_one('#ia-info')).update(f'Iteracoes por jogada: {self.max_iteracoes}')

    def action_harder(self) -> None:
        self.max_iteracoes *= 2
        cast(Label, self.query_one('#ia-info')).update(f'Iteracoes por jogada: {self.max_iteracoes}')

    def compose(self) -> ComposeResult:
        yield Header()
        self.title = 'Jogando o jogo da velha com a IA'

        with Horizontal():
            with Vertical(id='ia-container'):
                yield Label(id='ia-info')
                yield Tree('*', id='ia-tree')
            with Vertical(id='game-container'):
                yield DataTable(id='game-table')
                yield Label(id='game-result')

        yield Footer()

        self.call_after_refresh(self.set_start)

    async def set_start(self) -> None:
        game_table_element = self.query_one('#game-table')
        game_table_element.disabled = True

        self.pausado = True
        self.refresh_bindings()

        self.jogo = Jogo(self.tamanho, self.pontos_pra_ganhar)
        self.set_tree(None)
        await self.set_table()
        cast(Label, self.query_one('#game-result')).update('')
        cast(Label, self.query_one('#ia-info')).update(f'Iteracoes por jogada: {self.max_iteracoes}')
        if not self.jogador:
            self.ia_play()

        self.pausado = False
        self.refresh_bindings()

        game_table_element.focus()
        game_table_element.disabled = False

    async def set_table(self) -> None:
        game_table_element = cast(DataTable[str], self.query_one('#game-table'))

        game_table_element.clear()
        game_table_element.cursor_type = 'cell'

        columns = list(game_table_element.columns.keys())
        for column in columns:
            game_table_element.remove_column(column)
        coordenadas = [str(i) for i in range(self.tamanho)]
        game_table_element.add_columns(*coordenadas)

        for y, linha in enumerate(self.jogo.tabuleiro):
            linha_tabela = [self.simbolos[x] for x in linha]
            game_table_element.add_row(*linha_tabela, label=str(y))

    @on(DataTable.CellSelected, '#game-table')
    async def choose_cell(self, event: DataTable.CellSelected) -> None:
        table_element = cast(DataTable[str], self.query_one('#game-table'))
        table_element.disabled = True

        self.pausado = True
        self.refresh_bindings()

        coordenadas = event.coordinate
        jogada = (coordenadas.row, coordenadas.column)

        try:
            self.jogo.joga(jogada)
            table_element.update_cell_at(Coordinate(jogada[0], jogada[1]), self.simbolos[self.jogador])
        except:
            self.pausado = False
            self.refresh_bindings()

            table_element.focus()
            table_element.disabled = False
            return

        if self.jogo.acabou():
            self.set_ending()
            return

        self.ia_play()

        if self.jogo.acabou():
            self.set_ending()
            return

        self.pausado = False
        self.refresh_bindings()

        table_element.focus()
        table_element.disabled = False

    def ia_play(self) -> None:
        ia = IA(self.C, self.max_iteracoes)
        jogada = ia.escolhe_jogada(self.jogo)
        self.jogo.joga(jogada)
        self.set_tree(ia.arvore)

        table_element = cast(DataTable[str], self.query_one('#game-table'))
        table_element.update_cell_at(Coordinate(jogada[0], jogada[1]), self.simbolos[not self.jogador])

    def set_tree(self, arvore: No | None) -> None:
        tree_element = cast(Tree[None], self.query_one('#ia-tree'))
        tree_element.clear()

        if arvore:
            fila: Queue[tuple[TreeNode[None], No]] = Queue()
            fila.put((tree_element.root, arvore))

            while not fila.empty():
                element, no_atual = fila.get()

                for jogada in sorted(list(no_atual.filhos)):
                    filho = no_atual.filhos[jogada]
                    visitas_pai = filho.pai.visitas if filho.pai else 0
                    child_element = element.add(
                        f'({jogada[0]}, {jogada[1]}) {filho.visitas} {filho.pontuacao:.6f} [{filho.pontuacao:.6f} + {self.C} * sqrt({visitas_pai} / {filho.visitas})]',
                        expand=False,
                    )

                    fila.put((child_element, filho))

            tree_element.root.expand()

    def set_ending(self) -> None:
        self.pausado = False
        self.refresh_bindings()

        if self.jogo.ganhador() is None:
            cast(Label, self.query_one('#game-result')).update('Ninguém ganhou.')
        elif self.jogo.ganhador() == self.jogador:
            cast(Label, self.query_one('#game-result')).update('Parabéns, você ganhou!')
        else:
            cast(Label, self.query_one('#game-result')).update('Que pena, você perdeu...')
