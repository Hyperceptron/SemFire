
from pycallgraph2 import PyCallGraph
from pycallgraph2.output import GraphvizOutput

with PyCallGraph(output=GraphvizOutput()):
    import sys
    sys.path.insert(0, 'src')
    from cli import main

    sys.argv = ['src/cli.py', 'analyze', 'hello world']
    main()
