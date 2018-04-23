#! /usr/bin/env bash 

i_path1="../images/island-cartoons/island-1.svg"
i_path2="../images/island-cartoons/island-2.svg"
i_path3="../images/island-cartoons/island-3.svg"
i_path4="../images/island-cartoons/paleo-island-1.svg"
i_path5="../images/island-cartoons/paleo-island-2.svg"

islands="${i_path1} ${i_path2} ${i_path3} ${i_path4} ${i_path5}"

colors="green_rgb(50,162,81) orange_rgb(255,127,15) blue_rgb(60,183,204) yellow_rgb(255,217,74) teal_rgb(57,115,124) auburn_rgb(184,90,13)"
# colors="red_#f00000 orange_#ff8000 yellow_#ffff00 green_#007940 blue_#4040ff violet_#a000c0"

for g_path in $islands;
do
    n=1
    for c in $colors
    do
        color="${c%%_*}"
        color_code="${c##*_}"
        fuzz="10%"
        out_path="${g_path/\.svg/-$color\.png}"
        shadow_path="${g_path/\.svg/-$color-shadow\.png}"
        echo "Converting to $color ($color_code)..."
        convert "$g_path" -fuzz "$fuzz" -transparent white -fill "$color_code" -opaque black "$out_path"
        convert "$out_path" \( +clone -background black -shadow 95x9+15+15 \) +swap -background none -layers merge +repage "$shadow_path" 
        echo "done."
        n=$(expr $n + 1)
    done
done
