"""
monte.py  –  Monte-Carlo-Tree-Search Connect-4 engine
• 64-bit bitboards
"""

from __future__ import annotations
import math, random, time, sys
from dataclasses import dataclass, field
from typing import Optional


ROWS, COLS = 6, 7
BITS_PER_COL = ROWS + 1                   


COL_MASKS = [(1 << BITS_PER_COL) - 1 << (c * BITS_PER_COL) for c in range(COLS)]
TOP_MASKS = [1 << (ROWS + c * BITS_PER_COL) for c in range(COLS)]

def drop(bb, bit):
    return bb | (1 << bit)

def is_win(bb):
    m = bb & (bb >> 1)
    if m & (m >> 2): return True
    m = bb & (bb >> BITS_PER_COL)
    if m & (m >> (2 * BITS_PER_COL)): return True
    m = bb & (bb >> (BITS_PER_COL - 1))
    if m & (m >> (2 * (BITS_PER_COL - 1))): return True
    m = bb & (bb >> (BITS_PER_COL + 1))
    return bool(m & (m >> (2 * (BITS_PER_COL + 1))))


class BitboardGame:
    __slots__ = ("bb", "heights", "moves")

    def __init__(self):
        self.bb = [0, 0]                                    
        self.heights = [c * BITS_PER_COL + 1 for c in range(COLS)]
        self.moves: list[int] = []

    def __str__(self):
        gr = [["." for _ in range(COLS)] for _ in range(ROWS)]
        for c in range(COLS):
            bit = 1 << (c * BITS_PER_COL + 1)
            for r in range(ROWS):
                if self.bb[0] & bit:gr[r][c]= "X"
                if self.bb[1] & bit:gr[r][c] = "O"
                bit <<= 1
        rows = [" ".join(gr[r]) for r in reversed(range(ROWS))]
        rows.append("0 1 2 3 4 5 6")
        return "\n".join(rows)

    @property
    def side_to_move(self):
        return len(self.moves) & 1            

    def legal_moves(self):
        occ = self.bb[0] | self.bb[1]
        return [c for c in range(COLS) if not occ & TOP_MASKS[c]]

    def play(self, col) -> None:
        if col not in self.legal_moves():
            raise ValueError(f"Column {col} is full")
        side = self.side_to_move
        bit = self.heights[col]
        self.bb[side] |= 1 << bit
        self.heights[col] += 1
        self.moves.append(col)

    def undo(self):
        col  = self.moves.pop()
        side = self.side_to_move 
        self.heights[col] -= 1
        self.bb[side] &= ~(1 << self.heights[col])

    def terminal(self):
        if not self.moves:
            return False, None
        last = self.side_to_move ^ 1
        if is_win(self.bb[last]):           
            return True, last
        if len(self.moves) == ROWS * COLS: 
            return True, None
        return False, None

    def copy(self):
        g = BitboardGame()
        g.bb = self.bb[:]
        g.heights = self.heights[:]
        g.moves = self.moves[:]
        return g


EXPLORATION_C = math.sqrt(2)

@dataclass
class Node:
    key: tuple[int, int]
    heights_key: tuple[int, ...]
    parent: "Node | None"
    move_from_parent: int | None
    player: int                      
    wins: float = 0.0
    visits: int = 0
    untried: list[int] = field(default_factory=list)
    children: dict[int, "Node"] = field(default_factory=dict)

    def ucb(self):
        if self.visits == 0:
            return float("inf")
        return self.wins/self.visits + EXPLORATION_C*math.sqrt(math.log(self.parent.visits) / self.visits)


CENTER_ORDER = [3, 2, 4, 1, 5, 0, 6]    

def random_policy(game, rng):
    legal = game.legal_moves()
    if rng.random() < 0.75:
        for c in CENTER_ORDER:
            if c in legal:
                return c
    return rng.choice(legal)

class MCTSAgent:
    def __init__(self, time_limit = 1.2, tactical= False, rng = None):
        self.time_limit = time_limit
        self.use_tactic = tactical
        self.rng = rng or random.Random()
        self.tt: dict[tuple[int, int, tuple[int, ...]], Node] = {}
        self.last_root_visits = 0   

    def _tactic(self, g):
        if not self.use_tactic:
            return None

        me, opp = g.side_to_move, g.side_to_move ^ 1
        legal = g.legal_moves()

        for c in legal:
            if is_win(drop(g.bb[me], g.heights[c])):
                return c

        for c in legal:
            if is_win(drop(g.bb[opp], g.heights[c])):
                return c

        safe = []
        for c in legal:
            g.play(c)                      
            gives_reply_win = False
            for d in g.legal_moves():     
                if is_win(drop(g.bb[opp], g.heights[d])):
                    gives_reply_win = True
                    break
            g.undo()
            if not gives_reply_win:
                safe.append(c)
        if len(safe) == 1:
            return safe[0]
        return None


    def search(self, root):
        tac = self._tactic(root)
        if tac is not None:
            self.last_root_visits = 0        
            return tac

        root_key = self._key(root)
        node = self.tt.get(root_key)
        if not node:
            node = Node(key=root_key[0], heights_key=root_key[1], parent=None, move_from_parent=None, player=0, untried=root.legal_moves()[:])
            self.tt[root_key] = node

        stop = time.time() + self.time_limit
        while time.time() < stop:
            g = root.copy()
            n = node
            while not n.untried and n.children:
                n = max(n.children.values(), key=Node.ucb)
                g.play(n.move_from_parent)

            if n.untried:
                while n.untried:                       
                    c = self.rng.choice(n.untried)
                    try:
                        g.play(c)
                        break
                    except ValueError:
                        n.untried.remove(c)
                else:
                    self._backprop(n, *g.terminal())
                    continue

                child_key = self._key(g)
                child = self.tt.get(child_key)
                if not child:
                    child = Node(key=child_key[0], heights_key=child_key[1], parent=n, move_from_parent=c, player=n.player ^ 1, untried=g.legal_moves()[:])
                    self.tt[child_key] = child
                n.children[c] = child
                n = child

            term, winner = g.terminal()
            while not term:
                m = self._tactic(g)
                if m is None:
                    L = g.legal_moves()
                    if not L: break
                    m = random_policy(g, self.rng)
                try:
                    g.play(m)
                except ValueError:
                    break
                term, winner = g.terminal()

            self._backprop(n, term, winner)

        best_col, best_node = max(node.children.items(), key=lambda kv: kv[1].visits)
        self.last_root_visits = best_node.parent.visits if best_node.parent else 0
        return best_col


    def _backprop(self, n, term, winner):
        if winner is None:
            res = 0.5
        else:
            if winner == n.player:
                res = 1.0
            else:
                res = 0.0

        while n:
            n.visits += 1
            n.wins += res
            res = 1.0 - res
            n = n.parent

    def _key(self, g):
        p = g.side_to_move
        return (g.bb[p], g.bb[p ^ 1]), tuple(g.heights)


def human_vs_ai():
    print("Connect-4 – you are O (second).  Type column 0-6.")
    seed = int(time.time())
    random.seed(seed)
    print(f"[debug] random seed = {seed}")

    g = BitboardGame()
    ai = MCTSAgent(time_limit=5, tactical=True)   

    while True:
        col = ai.search(g)
        g.play(col)
        print(f"\nAI drops in column {col}\n{g}\n")
        over, win = g.terminal()
        if over:
            print("AI wins!" if win == 0 else "Draw.")
            break

        legal = g.legal_moves()
        move = input(f"Your move {legal}: ")
        while True:
            try:
                c = int(move)
                if c in legal: break
            except ValueError:
                pass
            move = input(f"Illegal. Choose from {legal}: ")
        g.play(c)
        print(g, "\n")
        over, win = g.terminal()
        if over:
            print("You win!" if win == 1 else "Draw.")
            break

def self_play(n = 5, t = 5.0):
    rng = random.Random(42)
    ai = MCTSAgent(time_limit=t, tactical=False, rng=rng)
    w, l, d = 0, 0, 0
    for i in range(n):
        g = BitboardGame()
        while True:
            g.play(ai.search(g))
            over, win = g.terminal()
            if over: break
        if win is None: d += 1
        elif win == 0: w += 1
        else: l += 1
    print(f"{w}-{l}-{d} (W-L-D) over {n} self games")


if __name__ == "__main__":
    human_vs_ai()
    #self_play()
