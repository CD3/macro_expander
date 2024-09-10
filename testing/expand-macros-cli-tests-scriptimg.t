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
  ![](./_macro_expander-scratch/scriptimg-d8059e6deca3da5722b0e8e0a5c5aa7f805830f5-image.png)
  $ test -f ./_macro_expander-scratch/scriptimg-d8059e6deca3da5722b0e8e0a5c5aa7f805830f5-image.png
  $ test -f ./_macro_expander-scratch/scriptimg-d8059e6deca3da5722b0e8e0a5c5aa7f805830f5-image.log
