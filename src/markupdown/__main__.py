from .commands import init, serve
import sys

if __name__ == "__main__":
    match sys.argv:
        case [_, "init", *_]:
            init()
        case [_, "serve", *args]:
            port = int(next(iter(args), 8000))
            serve(port)
        case _:
            print("Usage: markupdown init | serve", file=sys.stderr)
            sys.exit(1)