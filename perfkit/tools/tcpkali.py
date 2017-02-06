import click
import psutil
import os.path

from perfkit.process import Process


class Tcpkali(Process):
    def __init__(self, binary, time):
        if not binary:
            binary = 'vendor/tcpkali'
        self.binary = binary
        self.host = None
        self.port = None
        self.workers = 1
        self.connections = 1
        self.time = time or 10

    def configure(self, tested):
        self.host, self.port = tested.psprocess.connections()[0].laddr

    @property
    def cmd(self):
        return [
            os.path.abspath(self.binary), '-w', str(self.workers), '-c', str(self.connections),
            '-T', str(self.time), '-m', 'x', '{}:{}'.format(self.host, self.port)]

    def report(self):
        for line in self.output.splitlines():
            if not line.startswith(b'Bandwidth per channel:'):
                continue
            line = line[len(b'Bandwidth per channel: '):]
            line = line.split()
            bandwidth = float(line[0][:-3])
            return bandwidth

    def __repr__(self):
        return '<Tcpkali {}:{} {} worker(s) {} connection(s)>'.format(
            self.host, self.port, self.workers, self.connections)

@click.command()
@click.option('--binary')
@click.option('--time', type=int)
@click.option('--repeat', type=int)
def cli(binary, time, repeat):
    if repeat:
        return [Tcpkali(binary, time) for _ in range(repeat)]
    else:
        return Tcpkali(binary, time)
