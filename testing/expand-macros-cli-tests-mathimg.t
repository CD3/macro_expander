  $ eq="\vec{F} = \frac{k q_1 q_2}{r^2} \hat{r}"
  $ cat << EOF > input.md.t
  > Coulomb's Law: \mathimg{$eq}
  > EOF
  $ expand-macros.py input.md.t input.md > /dev/null
  $ test -f input.md
  $ cat input.md
  Coulomb's Law: ![](./_macro_expander-scratch/mathimg-a12c90dd39e0ee8cb5025183d44ec431cad68d6d-image.png)
  $ test -f ./_macro_expander-scratch/mathimg-a12c90dd39e0ee8cb5025183d44ec431cad68d6d-image.png
  $ test -f ./_macro_expander-scratch/mathimg-a12c90dd39e0ee8cb5025183d44ec431cad68d6d-image.log
  $ cat << EOF > input.md.t
  > Coulomb's Law: \mathimg[o="html"]{$eq}
  > EOF
  $ expand-macros.py input.md.t input.md > /dev/null
  $ cat input.md
  Coulomb's Law: <img src="data:image/png;base64,.*" > (re)
  $ rm input.md
  $ expand-macros.py -c input.md.t input.md > /dev/null
  $ cat input.md
  Coulomb's Law: <img src="data:image/png;base64,.*" > (re)
  $ test -f expand-macros.cache
  $ rm input.md
  $ expand-macros.py -c input.md.t input.md > /dev/null
  $ cat input.md
  Coulomb's Law: <img src="data:image/png;base64,.*" > (re)
  $ rm input.md
  $ expand-macros.py -c -f mycache.txt input.md.t input.md > /dev/null
  $ cat input.md
  Coulomb's Law: <img src="data:image/png;base64,.*" > (re)
  $ test -f expand-macros.cache
  $ test -f mycache.txt
