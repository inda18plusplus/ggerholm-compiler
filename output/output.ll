; ModuleID = "C:\Programming\School\LLVMCompiler\compiler\codegen.py"
target triple = "i686-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

define i32 @"func"(i32 %"x") 
{
entry:
  %".3" = icmp eq i32 5, 0
  %".4" = select i1 %".3", i32 1, i32 0
  %".5" = add i32 5, %".4"
  %".6" = sub i32 %".5", 1
  %".7" = mul i32 %"x", %".6"
  %".8" = sub i32 0, %".7"
  %".9" = xor i32 2, -1
  %".10" = mul i32 5, %".9"
  %".11" = add i32 %".8", %".10"
  %".12" = sdiv i32 %".11", 5
  %".13" = bitcast [5 x i8]* @"f_str" to i8*
  %".14" = call i32 (i8*, ...) @"printf"(i8* %".13", i32 %".12")
  ret i32 0
}

@"f_str" = internal constant [5 x i8] c"%i \0a\00"
define i32 @"second"(i32 %"x", i32 %"y") 
{
entry:
  br label %"loop"
loop:
  %"i" = phi i32 [0, %"entry"], [%"next_var.1", %"after_loop"]
  br label %"loop.1"
loop.1:
  %"j" = phi i32 [0, %"loop"], [%"next_var", %"loop.1"]
  %".6" = mul i32 %"i", %"x"
  %".7" = mul i32 %"y", %"j"
  %".8" = sub i32 %".6", %".7"
  %".9" = bitcast [5 x i8]* @"f_str" to i8*
  %".10" = call i32 (i8*, ...) @"printf"(i8* %".9", i32 %".8")
  %"next_var" = add i32 %"j", 1
  %"loop_cond" = icmp ne i32 %"next_var", 2
  br i1 %"loop_cond", label %"loop.1", label %"after_loop"
after_loop:
  %"next_var.1" = add i32 %"i", 1
  %"loop_cond.1" = icmp ne i32 %"next_var.1", 3
  br i1 %"loop_cond.1", label %"loop", label %"after_loop.1"
after_loop.1:
  ret i32 5
}

define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 2
  %".3" = sub i32 %".2", 4
  %".4" = icmp slt i32 %".3", 0
  br i1 %".4", label %"then", label %"else"
then:
  %".6" = call i32 @"second"(i32 25, i32 10)
  br label %"if_mrg"
else:
  %".8" = call i32 @"func"(i32 50)
  br label %"if_mrg"
if_mrg:
  %"if_temp" = phi i32 [%".6", %"then"], [%".8", %"else"]
  %".10" = mul i32 5, 2
  %".11" = sdiv i32 %".10", 3
  ret i32 %".11"
}
