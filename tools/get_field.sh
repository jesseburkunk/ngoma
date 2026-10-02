#!/bin/sh
# Ngoma Field: downloads the source recordings (all CC0, Felix Blume on Freesound) into field_src/.
# Run once on the Mac:  cd ~/MijnOS/Ngoma && sh tools/get_field.sh
# Claude then cuts them into loops in public/field/. field_src/ stays out of git.
set -e
mkdir -p field_src
get(){ echo "  $1"; curl -fsSL --retry 2 -o "field_src/$1.mp3" "$2"; }
get water  https://cdn.freesound.org/previews/260/260165_1661766-hq.mp3
get night  https://cdn.freesound.org/previews/328/328293_1661766-hq.mp3
get wires  https://cdn.freesound.org/previews/665/665629_1661766-hq.mp3
get dawn   https://cdn.freesound.org/previews/408/408048_1661766-hq.mp3
get ice    https://cdn.freesound.org/previews/133/133754_1661766-hq.mp3
get city   https://cdn.freesound.org/previews/395/395939_1661766-hq.mp3
get bats   https://cdn.freesound.org/previews/245/245811_1661766-hq.mp3
ls -l field_src
echo "Klaar. Zeg het tegen Claude."
