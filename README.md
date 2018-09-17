
# pilon_parallel
Split reference and bam to run pilon in parallel</br>
## install
You need conda to install pilon_parallel</br>
```
git clone https://github.com/zhouyiqi91/pilon_parallel.git
cd pilon_parallel
sh install_dependencies.sh
```
## usage:
1.cp pilon.cfg to workdir and modify</br>
2.```run_pilon.sh```</br>
note:Only suitable for SGE cluster;need to modify sgearrpy.py to adapt to other clusters.</br>

