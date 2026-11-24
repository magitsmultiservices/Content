#!/bin/bash
# Haalt de twee grote clips voor reclame 5 en 7 (opnieuw) binnen, controleert of ze volledig zijn,
# en bouwt + rendert daarna reclame 5 en 7.
cd /home/user/content
duur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1" 2>/dev/null | cut -d. -f1; }
for poging in 1 2 3; do
  bash montage/hulp/haal2.sh montage/hulp/lijst-groot.txt
  a=$(duur media/rv4/20261118_162624.mp4); b=$(duur media/rv5/20261116_130245.mp4)
  echo "duur 162624=${a:-0} 130245=${b:-0}"
  goed=1
  if [ "${a:-0}" -lt 380 ]; then rm -f media/rv4/20261118_162624.mp4; goed=0; fi
  if [ "${b:-0}" -lt 250 ]; then rm -f media/rv5/20261116_130245.mp4; goed=0; fi
  [ $goed = 1 ] && break
  sleep 60
done
python3 montage/hulp/transcribeer.py medium 2>&1 | grep -v Warn | cut -c1-100
python3 montage/hulp/stem_bouwen.py reclame-005-palmbomen reclame-007-hout 2>&1 | grep -v "^    "
for p in reclame-005-palmbomen reclame-007-hout; do
  python3 montage/monteer.py montage/projecten/$p.json 2>&1 | tail -1
done
echo KLAAR-5-7
