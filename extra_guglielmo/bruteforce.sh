if [ $# -lt 4 ] || [ ! -e /opt/vid2curve/examples/$1/local_config.ini ] || [ ! -e ./Display ]; then
    echo "bruteforce example start stop increment"
    echo "example must be a valid directory in /opt/vid2curve/examples/ which contains a local_config.ini"
    echo "the script must be run in the same directory where exec ./Display is"
    exit 1
fi
for fl in $( seq $2 $4 $3 ); do
    echo Creating directory $fl
    mkdir -p $fl
    sed -i'.bak' "s/FocalLength = .*/FocalLength = $fl/" /opt/vid2curve/examples/$1/local_config.ini 
    for iter in {1..3}; do
        echo -n executing try $iter for focal length $fl... 
        ./Display > /dev/null 2>&1 # TODO launch in subshell to avoid garbage output
        mv curves.obj $fl/$iter.obj 2>/dev/null && echo " OK" || echo " FAIL"
    done
done
