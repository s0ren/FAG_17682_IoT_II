Se ... 


    git checkout --orphan gh-pages
    git reset --hard # make sure all changes are committed before running this!
    git commit --allow-empty -m "Initialising gh-pages branch"
    git push origin gh-pages