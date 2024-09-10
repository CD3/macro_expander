test:
  cd testing && rye run pytest
  cd testing && rye run cram *.t
