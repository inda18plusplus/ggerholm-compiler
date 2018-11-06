llc -filetype=obj output.ll
gcc output.obj -o output
output
echo %ERRORLEVEL%