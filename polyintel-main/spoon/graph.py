from typing import Callable, Dict, List, TypedDict, Literal, Awaitable

class AgentState(TypedDict):
    market_slug: str
    current_odds: float
    narrative_score: float
    fundamental_truth: str
    decision: Literal["BUY", "PASS"]

Node = Callable[[AgentState], Awaitable[AgentState]]

class Graph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[str]] = {}

    def add_node(self, name: str, node: Node) -> None:
        self.nodes[name] = node
        if name not in self.edges:
            self.edges[name] = []

    def add_edge(self, src: str, dst: str) -> None:
        if src not in self.edges:
            self.edges[src] = []
        self.edges[src].append(dst)

    def topo(self) -> List[str]:
        indeg: Dict[str, int] = {n: 0 for n in self.nodes}
        for s, ds in self.edges.items():
            for d in ds:
                indeg[d] = indeg.get(d, 0) + 1
        q: List[str] = [n for n, v in indeg.items() if v == 0]
        order: List[str] = []
        seen: Dict[str, bool] = {}
        while q:
            u = q.pop(0)
            if seen.get(u):
                continue
            seen[u] = True
            order.append(u)
            for v in self.edges.get(u, []):
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        return order

    async def run(self, start: str, state: AgentState) -> AgentState:
        order = self.topo()
        if start not in order:
            order.insert(0, start)
        executed: Dict[str, bool] = {}
        for name in order:
            node = self.nodes.get(name)
            if not node:
                continue
            state = await node(state)
            executed[name] = True
        return state