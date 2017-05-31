paste -d' ' <(for d in `cat embeddings.list`; do ls $HOME"${d##*ignacio}"; done) <(cat links) | while read first second; do ln -s $first $second; done
