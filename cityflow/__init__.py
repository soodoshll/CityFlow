from ._cityflow import Engine, Archive
class myEngine(Engine):
    def run_step(self, n):
        for i in range(n):
            self.next_step()