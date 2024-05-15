#!/bin/bash
clear

url="http://192.168.12.18/file/ankdrive/12%20%E5%8E%9F%E5%A7%8B%E6%95%B0%E6%8D%AE/%E6%96%91%E9%A9%AC%E9%82%A6%E8%B5%9B%E4%BA%8B%E5%BD%95%E5%83%8F/%E8%B6%B3%E7%90%83"
save="/home/sfy/SFY/NAS/Datasets/football/raw_data/videos/斑马邦"

folder_list=("A531024120002/" "A531024120003/" "X511023510010/" "X511023510019/" "X521024150021/")

for folder in "${folder_list[@]}"; do
    python akd.py \
        -i "$url/$folder" \
        -o "$save/$folder"

    bash ./akd_convert.sh "$save/$folder"
done