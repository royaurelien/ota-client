

id=$(ota send report.json --local)
ota download "$id" pdf --template default --local