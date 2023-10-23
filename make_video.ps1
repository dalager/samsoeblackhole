
ffmpeg -r 10 -i out/plot_%03d.png -pix_fmt yuv420p  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -r 10 blackhole.mp4
