from queue import Queue
from typing import TYPE_CHECKING, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.widgets import DataTable, Footer, Header, Label, Tree

from mcts.ia import IA, No
from mcts.jogo import Jogo

if TYPE_CHECKING:
    from textual.widgets._tree import TreeNode


class Tela(App[None]):
    CSS_PATH = './styles/tela.tcss'
    BINDINGS: ClassVar = [
        ('x', 'exit', 'Sair'),
        ('r', 'restart', 'Reiniciar'),
        ('t', 'swap_players', 'Troca jogadores'),
        ('f', 'easier', 'Mais fácil'),
        ('d', 'harder', 'Mais difícil'),
    ]

    def __init__(
        self,
        c: float,
        max_iteracoes: int,
        jogador_vai_primeiro: bool,
        tamanho: int,
        pontos_pra_ganhar: int,
    ) -> None:
        self.c = c
        self.max_iteracoes = max_iteracoes
        self.jogador = jogador_vai_primeiro
        self.tamanho = tamanho
        self.pontos_pra_ganhar = pontos_pra_ganhar
        self.jogo = Jogo(tamanho, pontos_pra_ganhar)

        self.pausado = False
        self.simbolos = {None: ' ', False: 'O', True: 'X'}

        self.elemento_ia_info = Label(id='ia-info')
        self.elemento_ia_tree = Tree[None]('*', id='ia-tree')
        self.elemento_game_table = DataTable[str](id='game-table')
        self.elemento_game_result = Label(id='game-result')

        super().__init__()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:  # noqa: ARG002
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
        self.elemento_ia_info.update(f'Iteracoes por jogada: {self.max_iteracoes}')

    def action_harder(self) -> None:
        self.max_iteracoes *= 2
        self.elemento_ia_info.update(f'Iteracoes por jogada: {self.max_iteracoes}')

    def compose(self) -> ComposeResult:
        yield Header()
        self.title = 'Jogando o jogo da velha com a IA'

        with Horizontal():
            with Vertical(id='ia-container'):
                yield self.elemento_ia_info
                yield self.elemento_ia_tree
            with Vertical(id='game-container'):
                yield self.elemento_game_table
                yield self.elemento_game_result

        yield Footer()

        self.call_after_refresh(self.set_start)

    async def set_start(self) -> None:
        self.elemento_game_table.disabled = True

        self.pausado = True
        self.refresh_bindings()

        self.jogo = Jogo(self.tamanho, self.pontos_pra_ganhar)
        self.set_tree(None)
        await self.set_table()
        self.elemento_game_result.update('')
        self.elemento_ia_info.update(f'Iteracoes por jogada: {self.max_iteracoes}')
        if not self.jogador:
            self.ia_play()

        self.pausado = False
        self.refresh_bindings()

        self.elemento_game_table.focus()
        self.elemento_game_table.disabled = False

    async def set_table(self) -> None:
        self.elemento_game_table.clear()
        self.elemento_game_table.cursor_type = 'cell'

        columns = list(self.elemento_game_table.columns.keys())
        for column in columns:
            self.elemento_game_table.remove_column(column)
        coordenadas = [str(i) for i in range(self.tamanho)]
        self.elemento_game_table.add_columns(*coordenadas)

        for y, linha in enumerate(self.jogo.tabuleiro):
            linha_tabela = [self.simbolos[x] for x in linha]
            self.elemento_game_table.add_row(*linha_tabela, label=str(y))

    @on(DataTable.CellSelected, '#game-table')
    async def choose_cell(self, event: DataTable.CellSelected) -> None:
        self.elemento_game_table.disabled = True

        self.pausado = True
        self.refresh_bindings()

        coordenadas = event.coordinate
        jogada = (coordenadas.row, coordenadas.column)

        try:
            self.jogo.joga(jogada)
            self.elemento_game_table.update_cell_at(Coordinate(jogada[0], jogada[1]), self.simbolos[self.jogador])
        except:
            self.pausado = False
            self.refresh_bindings()

            self.elemento_game_table.focus()
            self.elemento_game_table.disabled = False
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

        self.elemento_game_table.focus()
        self.elemento_game_table.disabled = False

    def ia_play(self) -> None:
        ia = IA(self.c, self.max_iteracoes)
        jogada = ia.escolhe_jogada(self.jogo)
        self.jogo.joga(jogada)
        self.set_tree(ia.arvore)

        self.elemento_game_table.update_cell_at(Coordinate(jogada[0], jogada[1]), self.simbolos[not self.jogador])

    def set_tree(self, arvore: No | None) -> None:
        self.elemento_ia_tree.clear()

        if arvore:
            fila: Queue[tuple[TreeNode[None], No]] = Queue()
            fila.put((self.elemento_ia_tree.root, arvore))

            while not fila.empty():
                element, no_atual = fila.get()

                for jogada in sorted(no_atual.filhos):
                    filho = no_atual.filhos[jogada]
                    visitas_pai = filho.pai.visitas if filho.pai else 0
                    child_element = element.add(
                        f'({jogada[0]}, {jogada[1]}) {filho.visitas} {filho.pontuacao:.6f} [{filho.pontuacao:.6f} + {self.c} * sqrt({visitas_pai} / {filho.visitas})]',
                        expand=False,
                    )

                    fila.put((child_element, filho))

            self.elemento_ia_tree.root.expand()

    def set_ending(self) -> None:
        self.pausado = False
        self.refresh_bindings()

        if self.jogo.ganhador() is None:
            self.elemento_game_result.update('Ninguém ganhou.')
        elif self.jogo.ganhador() == self.jogador:
            self.elemento_game_result.update('Parabéns, você ganhou!')
        else:
            self.elemento_game_result.update('Que pena, você perdeu...')
