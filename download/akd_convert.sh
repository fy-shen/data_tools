#!/bin/bash

# 原始数据(aqms/h264)所在目录, MP4会存放在此目录, 文件名与最后一层文件夹名相同
# 例如 /home/sfy/SFY/NAS/Datasets/football/raw_data/videos/斑马邦/X511023510019/20240426-145647/20240426-145647.mp4
data_dir=$1
# test_single_video 所在目录
cd "/home/sfy/SFY/dev/sports_camera/bin"
rm -f "./pano.h264"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function copy_mp4() {
    local video="$1"
    echo "开始拷贝"
    ffmpeg -i "./pano.h264" -c copy "$video" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${RED}拷贝失败${NC}"
    else
        echo -e "${GREEN}拷贝成功${NC}"
    fi
}


for folder in "$data_dir"/*/; do
    fn=$(basename "$folder")
    video_dir="$data_dir/$fn"
    video_path="$video_dir/$fn.mp4"
    if [ -e "$video_dir/0.aqms" ] && [ -e "$video_dir/1.aqms" ]; then
        video_raw="$video_dir/0.aqms"
    elif [ -e "$video_dir/0.h264" ] && [ -e "$video_dir/1.h264" ]; then
        video_raw="$video_dir/0.h264"
    else
        echo -e "${RED}$video_dir 中不存在原始视频文件${NC}"
        continue
    fi

    if [ -e "$video_path" ]; then
        echo -e "${YELLOW}$video_path 已存在，跳过${NC}"
    else
        echo "$video_raw 开始解码"
        ./test_single_video "$video_raw" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo -e "${RED}$video_raw 解码失败${NC}"
            continue
        else
            echo -e "${GREEN}解码成功${NC}"
            copy_mp4 "$video_path"
        fi
    fi
done