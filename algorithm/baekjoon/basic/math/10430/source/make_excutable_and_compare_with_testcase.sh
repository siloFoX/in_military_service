#!/bin/bash

g++ main.cpp -o test/main
./test/main < test/input > test/output_testcase
diff test/output test/output_testcase

echo "---"
echo "If nothing happend, testcase works. congratulations!"
echo "---"
