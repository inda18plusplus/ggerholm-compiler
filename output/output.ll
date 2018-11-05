; ModuleID = "C:\Programming\School\LLVMCompiler\compiler\codegen.py"
target triple = "i686-pc-windows-msvc"
target datalayout = ""

define void @"main"() 
{
entry:
  %".2" = icmp eq i8 5, 0
  %".3" = select i1 %".2", i8 1, i8 0
  %".4" = add i8 5, %".3"
  %".5" = sub i8 %".4", 1
  %".6" = mul i8 5, %".5"
  %".7" = xor i8 2, -1
  %".8" = mul i8 5, %".7"
  %".9" = add i8 %".6", %".8"
  %".10" = bitcast [5 x i8]* @"fstr" to i8*
  %".11" = call i32 (i8*, ...) @"printf"(i8* %".10", i8 %".9")
  ret void
}

declare i32 @"printf"(i8* %".1", ...) 

@"fstr" = internal constant [5 x i8] c"%i \0a\00"