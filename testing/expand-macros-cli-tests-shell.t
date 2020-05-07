  $ which expand-macros.py
  .*/_test-install-virtualenv/bin/expand-macros.py (re)
  $ cat << EOF > input.md.t
  > \shell{echo -n "Hello World"}
  > EOF
  $ expand-macros.py input.md.t input.md > /dev/null
  $ test -f input.md
  $ cat input.md
  Hello World

