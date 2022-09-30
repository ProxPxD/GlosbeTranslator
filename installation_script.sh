#!/bin/bash
main_script_name="translate.py"
main_script_path="$PWD/src/$main_script_name"
python_path=$1
python_path_size=${#python_path}
echo Path to translator script is $main_script_path

default_python=1
if [[ $python_path_size -eq 0 ]]; then echo "Using default system python"; else echo "Using python interpreter at: '$python_path'"; default_python=0; fi

if [[ $default_python -eq 0 ]] # if python path is provided check if path is correct (contains python)
then
    version=$($python_path -V 2>&1 | grep -Po '(?<=Python )(.+)') # get python version from python path
    if [[ -z "$version" ]]
    then
        echo "Error, incorrect python path!"
        exit 1 # exit script if python path is incorrect
    fi
fi

read -p "Enter desired alias for translator: " main_translate_alias
read -p "Enter alternative alias for translator(leave blank if not needed): " second_translate_alias

echo  >> ~/.bashrc # add empty line at the end of file
if [[ $default_python -eq 1 ]]
then
    echo "alias $main_translate_alias='python $main_script_path'" >> ~/.bashrc # add appropriate alias to .bashrc
    echo 'Translator installed using default system python'
else
    echo "alias glosbePython=$python_path" >> ~/.bashrc # add alias for python interpreter
    echo "alias $main_translate_alias='glosbePython $main_script_path'" >> ~/.bashrc # add appropriate alias to .bashrc
    echo 'Translator installed using' $python_path "python"
fi

echo 'Installed translator with alias:' $main_translate_alias

if [[ ${#second_translate_alias} -gt 0 ]]
then
    echo "alias $second_translate_alias='$main_translate_alias'" >> ~/.bashrc # add alternative alias
    echo 'Alternative alias is:' $second_translate_alias
fi