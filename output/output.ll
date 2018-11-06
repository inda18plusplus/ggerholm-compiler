; ModuleID = "C:\Programming\School\LLVMCompiler\compiler\codegen.py"
target triple = "i686-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

define i32 @"func"() 
{
entry:
  %".2" = icmp eq i32 5, 0
  %".3" = select i1 %".2", i32 1, i32 0
  %".4" = add i32 5, %".3"
  %".5" = sub i32 %".4", 1
  %".6" = mul i32 50, %".5"
  %".7" = sub i32 0, %".6"
  %".8" = xor i32 2, -1
  %".9" = mul i32 5, %".8"
  %".10" = add i32 %".7", %".9"
  %".11" = sdiv i32 %".10", 5
  %".12" = bitcast [5 x i8]* @"fstr" to i8*
  %".13" = call i32 (i8*, ...) @"printf"(i8* %".12", i32 %".11")
  ret i32 0
}

@"fstr" = internal constant [5 x i8] c"%i \0a\00"
define i32 @"unused"() 
{
entry:
  %".2" = sdiv i32 10, 2
  %".3" = add i32 10, %".2"
  %".4" = bitcast [5 x i8]* @"fstr" to i8*
  %".5" = call i32 (i8*, ...) @"printf"(i8* %".4", i32 %".3")
  ret i32 5
}

define i32 @"main"() 
{
entry:
  %".2" = call i32 @"func"()
  %".3" = add i32 5, 5
  ret i32 %".3"
}
