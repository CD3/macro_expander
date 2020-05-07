  $ which expand-macros.py
  .*/_test-install-virtualenv/bin/expand-macros.py (re)
  $ text=$(cat << EOF
  > #! $(which gnuplot)
  > set term png
  > set output "out.png"
  > plot sin(x), cos(x)
  > EOF
  > )
  $ cat << EOF > input.md.t
  > \scriptimg{$text}
  > EOF
  $ expand-macros.py input.md.t input.md > /dev/null
  $ test -f input.md
  $ cat input.md
  ![](./scriptimg-15c1ea7aa573f85e9b292ed54ae7bdc1f428b625-image.png)
  $ test -f ./scriptimg-15c1ea7aa573f85e9b292ed54ae7bdc1f428b625-image.png
  $ test -f ./scriptimg-15c1ea7aa573f85e9b292ed54ae7bdc1f428b625-image.log
