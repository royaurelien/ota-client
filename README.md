

id=$(ota send report.json --local --verbose false)
ota download "$id" pdf --template default --local


docker run -it python:3.9 bash