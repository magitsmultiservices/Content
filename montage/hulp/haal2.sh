#!/bin/bash
# Downloadt beelden uit Drive (map moet gedeeld zijn: Iedereen met de link) en maakt 1080p-proxies.
# Gebruik: bash montage/hulp/haal.sh lijst.txt   (regels: <map> <naam> <drive-id>; map vo* = alleen geluid)
B=/home/user/content/media
while read map naam id; do
  [ -z "$map" ] && continue
  mkdir -p $B/$map; basis=${naam%.*}; tmp=$B/tmp_download_$map
  if [[ $naam == *.jpg ]]; then [ -s $B/$map/$naam ] || curl -sSL -o $B/$map/$naam "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"; echo "FOTO $map $naam"; continue; fi
  if [[ $map == vo* ]]; then [ -s $B/$map/$basis.wav ] && { echo "AL $map $naam"; continue; }; else [ -s $B/$map/$basis.mp4 ] && { echo "AL $map $naam"; continue; }; fi
  curl -sSL -o $tmp "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t"
  if file $tmp | grep -q HTML; then echo "FOUT $map $naam"; rm -f $tmp; sleep 10; continue; fi
  if [[ $map == vo* ]]; then
    ffmpeg -nostdin -v error -y -i $tmp -vn -ac 1 -ar 48000 $B/$map/$basis.wav && echo "OK $map $naam"
  else
    ffmpeg -nostdin -v error -y -i $tmp -vf "scale='if(gt(iw,ih),-2,1080)':'if(gt(iw,ih),1080,-2)',fps=30" -c:v libx264 -preset veryfast -crf 22 -c:a aac -b:a 128k $B/$map/$basis.mp4 && echo "OK $map $naam"
  fi
  rm -f $tmp; sleep 5
done < "$1"
echo KLAAR
