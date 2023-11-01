#!/bin/bash
start=$SECONDS
echo $(pwd)
path=$(pwd)
new_path="${path%/*/*/*}/Filtered${path#*Raw}"
echo "$new_path"

total_time=0
total_talk_time=0
file_count=0

# Set the minimum decibel level
min_db=-20

for folder in *;
# for folder in "kbtp_2022-09-10_audio";
do
    echo "Going through folder ${folder}"
    folder_total_time=0
    folder_start=$SECONDS
    folder_total_talk_time=0
    folder_file_count=0
    for d in $folder/*; 
    do
        echo "Going through files in directory ${d}"
        for f in $d/*.wav; 
        do 
            
            file_count=$((file_count + 1))
            folder_file_count=$((folder_file_count + 1))
            
            # Check for duration
            duration=$(ffmpeg -i $f -af 'volumedetect' -f null /dev/null 2>&1 | grep Duration | sed -n 's/.*\([0-9][0-9]:[0-9][0-9]:[0-9][0-9]\.[0-9][0-9]\).*/\1/p')
            
            IFS=":,." read -r hours minutes seconds milliseconds<<< "$duration"
            if [[ ${hours:0:1} == "0" ]]; then
                hours="${hours:1}"
            fi
            if [[ ${minutes:0:1} == "0" ]]; then
                minutes="${minutes:1}"
            fi
            if [[ ${seconds:0:1} == "0" ]]; then
                seconds="${seconds:1}"
            fi
            total_seconds=$(echo "$hours * 3600 + $minutes * 60 + $seconds + $milliseconds / 1000" | bc -l)
            
            total_time=$(echo "$total_seconds + $total_time" | bc -l)
            folder_total_time=$(echo "$total_seconds + $folder_total_time" | bc -l)
            

            # Set the silence threshold and duration
            silence_threshold=-20dB
            duration=1

            # Run the silencedetect filter and extract the output
            output=$(ffmpeg -i $f -af "silencedetect=n=$silence_threshold:d=$duration" -vn -sn -dn -f null /dev/null 2>&1)

            # Extract the silence start and end times from the output
            readarray -t silence_times < <(echo "$output" | grep -Eo 'silence_start: [0-9]+(\.[0-9]+)?|silence_end: [0-9]+(\.[0-9]+)?' | awk '{print $2}')

            # echo "Silence times are: ${silence_times[@]}"

            # Calculate the duration of the non-silent segments
            silent_duration=0
            for ((i=0; i<${#silence_times[@]}; i+=2)); do
                start_time=${silence_times[i]}
                end_time=${silence_times[i+1]}
                # echo "Start time: $start_time"
                # echo "End time: $end_time"
                segment_duration=$(echo "$end_time - $start_time" | bc)
                # echo "Segment duration: $segment_duration"
                silent_duration=$(echo "$silent_duration + $segment_duration" | bc)
            done

            

            non_silent_duration=$(echo "$total_seconds - $silent_duration" | bc)
            
            
            total_talk_time=$(echo "$total_talk_time + $non_silent_duration" | bc -l)
            folder_total_talk_time=$(echo "$folder_total_talk_time + $non_silent_duration" | bc -l)
            
            if (( $(echo "$total_seconds < 1." | bc -l) )); then 
                echo "";
                echo "Audio clip was not long enough";
                echo $total_seconds;
                echo $duration;
                echo "";
                echo "";
                continue;
            fi; 

            
            # echo $f;
            # echo $duration
            # echo "Total seconds is ${total_seconds}"
            # echo "Silent duration: $silent_duration seconds"
            # echo "Time above minimum decibel level is ${non_silent_duration}"

            # echo "File ${f} has ${total_seconds} seconds, ${silent_duration} seconds of silence, and ${non_silent_duration} seconds of talking"
            echo "File ${f} has $(printf "%.2f" $total_seconds) seconds, $(printf "%.2f" $silent_duration) silence, and $(printf "%.2f" $non_silent_duration) talking"


            # echo "-------------------";
        done
    done
    # echo "Total time is $((total_time / 3600)) hours, $((total_time % 3600 / 60)) minutes, and $((total_time % 60)) seconds"
    echo "Folder total time is $(printf "%.3f" $(echo "$total_time / 3600" | bc -l)) hours, $(printf "%.3f" $(echo "($total_time / 60) % 60" | bc -l)) minutes, and $(printf "%.3f" $(echo "$total_time % 60" | bc -l)) seconds"
    # echo "Total time is $(printf "%.0f" $(echo "$total_time / 3600" | bc -l)) hours, $(printf "%.0f" $(echo "($total_time / 60) % 60" | bc -l)) minutes, and $(printf "%.3f" $(echo "$total_time % 60" | bc -l)) seconds"
    echo "Folder total talk time is $(printf "%.3f" $(echo "$total_talk_time / 3600" | bc -l)) hours, $(printf "%.3f" $(echo "($total_talk_time / 60) % 60" | bc -l)) minutes, and $(printf "%.3f" $(echo "$total_talk_time % 60" | bc -l)) seconds"
    echo $total_talk_time
    echo "Folder total number of files is $file_count"

    duration=$(( SECONDS - folder_start ))
    echo "Time taken is $((duration / 3600)) hours, $((duration % 3600 / 60)) minutes, and $((duration % 60)) seconds"
done

echo $total_time
# echo "Total time is $((total_time / 3600)) hours, $((total_time % 3600 / 60)) minutes, and $((total_time % 60)) seconds"
echo "Total time is $(printf "%.3f" $(echo "$total_time / 3600" | bc -l)) hours, $(printf "%.3f" $(echo "($total_time / 60) % 60" | bc -l)) minutes, and $(printf "%.3f" $(echo "$total_time % 60" | bc -l)) seconds"
# echo "Total time is $(printf "%.0f" $(echo "$total_time / 3600" | bc -l)) hours, $(printf "%.0f" $(echo "($total_time / 60) % 60" | bc -l)) minutes, and $(printf "%.3f" $(echo "$total_time % 60" | bc -l)) seconds"
echo "Total talk time is $(printf "%.3f" $(echo "$total_talk_time / 3600" | bc -l)) hours, $(printf "%.3f" $(echo "($total_talk_time / 60) % 60" | bc -l)) minutes, and $(printf "%.3f" $(echo "$total_talk_time % 60" | bc -l)) seconds"
echo $total_talk_time
echo "Total number of files is $file_count"

duration=$(( SECONDS - start ))
echo "Total time taken is $((duration / 3600)) hours, $((duration % 3600 / 60)) minutes, and $((duration % 60)) seconds"
