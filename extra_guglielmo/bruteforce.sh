if [ $# -lt 3 ]; then
    echo "bruteforce start stop increment"
    exit 1
fi
for fl in $( seq $1 $3 $2 ); do
    echo Creating directory $fl
    mkdir -p $fl
    sed -i'.bak' "s/FocalLength = .*/FocalLength = $fl/" /opt/vid2curve/examples/pyramid/local_config.ini 
    for iter in {1..3}; do
        echo executing try $iter for focal length $fl
        ./Display > /dev/null 2>&1
        mv curves.obj $fl/$iter.obj
    done
done
    
