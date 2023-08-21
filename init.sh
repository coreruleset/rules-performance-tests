#!/bin/bash


# copy necessary file for the framework
git clone https://github.com/coreruleset/coreruleset   

mv ./coreruleset/rules ./
mv ./coreruleset/plugins ./
mv ./coreruleset/tests ./
mv ./coreruleset/crs-setup.conf.example ./

rm -rf coreruleset