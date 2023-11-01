#!/bin/sh

echo $(pwd)
path=$(pwd)
new_path="${path%/*/*/*}/Filtered${path#*Raw}"
echo "$new_path"

for d in *; 
# for d in "11-17-21_audio"; 
do
    echo ""
    echo "Going through files in directory ${d}"
    echo ""
    for f in $d/*.wav; 
    do 
        echo $f;
        # echo $(ffmpeg -i $f  -af 'volumedetect' -f null /dev/null 2>&1);
        if $(ffmpeg -i $f  -af 'volumedetect' -f null /dev/null 2>&1 | grep -q "Invalid data found when processing input")
        then 
            echo "File had invalid data. Skipping.";
            continue;
        fi
        
        # Check for duration longer than a second
        duration=$(ffmpeg -i $f  -af 'volumedetect' -f null /dev/null 2>&1 | grep Duration)[4]; 
        duration=${duration%.*};
        duration=${duration#*:};
        IFS=":" read -r hours minutes seconds <<< "$duration"
        if [[ ${hours:0:1} == "0" ]]; then
            hours="${hours:1}"
        fi
        if [[ ${minutes:0:1} == "0" ]]; then
            minutes="${minutes:1}"
        fi
        if [[ ${seconds:0:1} == "0" ]]; then
            seconds="${seconds:1}"
        fi
        total_seconds=$(( hours * 3600 + minutes * 60 + seconds ))
        
        if (( $(echo "$total_seconds < 1." | bc -l) )); then 
            echo "";
            echo "Audio clip was not long enough";
            echo $total_seconds;
            echo $duration;
            echo "";
            echo "";
            continue;
        fi; 

        # Check the decibel level is above -20
        a=$(ffmpeg -i $f  -af 'volumedetect' -f null /dev/null 2>&1 | grep max_volume)[4];
        b=($a); 
        c=${b[4]}; 
        # echo $c; 
        if (( $(echo "$c > -20." | bc -l) )); then 
            # echo "Not empty"; 
            f_txt="${f%.wav}.txt"
            full_new_path="${new_path}/${f}"
            full_new_path_txt="${full_new_path%.wav}.txt"
            mkdir -p "${new_path}/${d}"
            cp $f "${full_new_path}"; 
            cp $f_txt "${full_new_path_txt}";
        else echo EMPTY; 
        fi; 
        # echo "-------------------";
    done
done
