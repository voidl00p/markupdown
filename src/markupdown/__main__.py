from .commands import init, serve
import sys

if __name__ == "__main__":
    match sys.argv:
        case [_, "init", *_]:
            init()
        case [_, "serve", *args]:
            arg_iter = iter(args)
            port = int(next(arg_iter, 8000))
            watch_dir = next(arg_iter, "pages")
            serve(port, watch_dir)
        case _:
            print("Usage: markupdown init | serve", file=sys.stderr)
            sys.exit(1)