#!/bin/zsh
R=../../img/posters
mkdir -p $R
for f in shots/posters/*.png; do
  n=${f:t:r}
  cwebp -quiet -q 76 -m 6 -resize 736 1104 $f -o $R/$n.webp
  cwebp -quiet -q 72 -m 6 -resize 540 810 $f -o $R/$n-540.webp
done
du -sh $R
