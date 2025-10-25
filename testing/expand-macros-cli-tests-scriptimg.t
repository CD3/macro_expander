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
  ![](./_macro_expander-scratch/scriptimg-ecc39936216711b0d6c20cd02e5e573741869e26-image.png)
  $ test -f ./_macro_expander-scratch/scriptimg-ecc39936216711b0d6c20cd02e5e573741869e26-image.png
  $ test -f ./_macro_expander-scratch/scriptimg-ecc39936216711b0d6c20cd02e5e573741869e26-image.log
