import sys
from trckr import app


if __name__ == "__main__":
    app.main(
        **app.parse_main(sys.argv[1:])
    )
