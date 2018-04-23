#! /usr/bin/env bash 

gv_path="../images/phylopics/gekko-vittatus.svg"
gg_path="../images/phylopics/gekko-gecko.svg"
gp_path="../images/phylopics/gecko-pixabay-cc0.png"

echo "Getting phylopics..."
if [ ! -e "$gv_path" ]
then
    curl -o "$gv_path" http://phylopic.org/assets/images/submissions/21ebdb0e-35ac-4e66-a7ba-99c101a7c2d1.svg
fi
if [ ! -e "$gg_path" ]
then
    curl -o "$gg_path" http://phylopic.org/assets/images/submissions/9aca34d8-4dde-418d-9fdc-2d58b6a7b267.svg
fi
echo "done."

paths="${gv_path} ${gg_path} ${gp_path}"

colors="green_rgb(50,162,81) orange_rgb(255,127,15) blue_rgb(60,183,204) yellow_rgb(255,217,74) teal_rgb(57,115,124) auburn_rgb(184,90,13)"
# colors="red_#f00000 orange_#ff8000 yellow_#ffff00 green_#007940 blue_#4040ff violet_#a000c0"

for g_path in $paths;
do
    n=1
    for c in $colors
    do
        color="${c%%_*}"
        color_code="${c##*_}"
        fuzz="90%"
        out_path="${g_path/\.svg/-$n-$color\.png}"
        shadow_path="${g_path/\.svg/-$n-$color-shadow\.png}"
        if [ "$g_path" = "$gp_path" ]
        then
            # fuzz="80%"
            out_path="${g_path/\.png/-$n-$color\.png}"
            shadow_path="${g_path/\.png/-$n-$color-shadow\.png}"
        fi
        echo "Converting to $color ($color_code)..."
        convert "$g_path" -fuzz "$fuzz" -transparent white -fill "$color_code" -opaque black "$out_path"
        convert "$out_path" \( +clone -background black -shadow 95x9+20+20 \) +swap -background none -layers merge +repage "$shadow_path" 
        echo "done."
        n=$(expr $n + 1)
    done
done
