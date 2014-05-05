#!/bin/bash



rootFolder="tests/"

tests=(
 "InstructionTest/backward_BEQ" 
 "InstructionTest/backward_BNE"
 "InstructionTest/backward_unconditional_jump" 
 "InstructionTest/forward_BEQ" 
 "InstructionTest/forward_BNE" 
 "InstructionTest/forward_unconditional_jump" 
 "InstructionTest/load_instructions" 
 "InstructionTest/store_instructions"
 "CacheTest/busCompetition"
 "CacheTest/storeandload" 
 "HazardTest/RAW"
 "HazardTest/Struct/FU-Struct-Hazard"
 "HazardTest/Struct/WB-Struct-Hazard"
 "HazardTest/WAW"
 "ComplexTest/firsttest"
 )


for i in "${tests[@]}"
	do
		name=$rootFolder$i
		echo $name	
		
		instFile=$name"/inst.txt"
		dataFile=$name"/data.txt"
		regFile=$name"/reg.txt"
		configFile=$name"/config.txt"
		resultFile=$name"/result.txt"
		
		python simulator.py  "$instFile" "$dataFile" "$regFile" "$configFile" "$resultFile"
		cat "$name/result.txt"
		
		echo -e "\n This was $name test"

		read 
	done



#echo "python simulator.py  $instFile $dataFile $regFile $configFile $resultFile"
#python simulator.py  "$instFile" "$dataFile" "$regFile" "$configFile" "$resultFile"
#cat "$1/result.txt"
#python simulator.py inst.txt data.txt reg.txt config.txt reg.txt
