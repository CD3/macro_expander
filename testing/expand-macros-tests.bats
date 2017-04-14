#! /usr/bin/env bats

@test "testing \mathimg macro" {
scratchdir=$(echo $BATS_TEST_DESCRIPTION | md5sum | cut -d' ' -f1)

[[ -d $scratchdir ]] && rm -r $scratchdir
mkdir $scratchdir
cd $scratchdir

eq="\vec{F} = \frac{k q_1 q_2}{r^2} \hat{r}"
cat << EOF > input.md.t
Coulomb's Law: \mathimg{$eq}
EOF

run ../expand-macros.py input.md.t input.md

[[ $status -eq 0 ]]
[[ -f input.md ]]

cmd="tex2im -o %s  -- '$eq' "
fhash=$(echo -n "$cmd" | sha1sum | cut -d' ' -f1)

ls >tmp.txt
[[ -f "mathimg-${fhash}-image.png" ]]
[[ -f "mathimg-${fhash}-image.log" ]]


cat input.md | grep "\!\[\](\./mathimg-${fhash}-image.png)"

}

@test "testing \scriptimg macro" {
scratchdir=$(echo $BATS_TEST_DESCRIPTION | md5sum | cut -d' ' -f1)

[[ -d $scratchdir ]] && rm -r $scratchdir
mkdir $scratchdir
cd $scratchdir

text=$(cat << EOF
#! $(which gnuplot)
set term png
set output "out.png"
plot sin(x), cos(x)
EOF
)

cat << EOF > input.md.t
\scriptimg{$text}
EOF

run ../expand-macros.py input.md.t input.md

[[ $status -eq 0 ]]
[[ -f input.md ]]

fhash=$(echo -n "$text" | sha1sum | cut -d' ' -f1)

[[ -f "scriptimg-${fhash}-image.png" ]]
[[ -f "scriptimg-${fhash}-image.log" ]]


}

@test "testing \shell macro" {
scratchdir=$(echo $BATS_TEST_DESCRIPTION | md5sum | cut -d' ' -f1)

[[ -d $scratchdir ]] && rm -r $scratchdir
mkdir $scratchdir
cd $scratchdir

cat << EOF > input.md.t
\shell{echo -n "Hello World"}
EOF

run ../expand-macros.py input.md.t input.md

[[ -f input.md ]]
[[ "$(cat input.md)" == "Hello World" ]]

}

@test "testing \write macro" {
scratchdir=$(echo $BATS_TEST_DESCRIPTION | md5sum | cut -d' ' -f1)
}

@test "testing \_img macro" {
scratchdir=$(echo $BATS_TEST_DESCRIPTION | md5sum | cut -d' ' -f1)
}



