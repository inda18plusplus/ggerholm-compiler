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
  %".12" = bitcast [5 x i8]* @"f_str" to i8*
  %".13" = call i32 (i8*, ...) @"printf"(i8* %".12", i32 %".11")
  ret i32 0
}

@"f_str" = internal constant [5 x i8] c"%i \0a\00"
define i32 @"second"() 
{
entry:
  br label %"loop"
loop:
  %"count" = phi i32 [0, %"entry"], [%"next_var.1", %"after_loop"]
  br label %"loop.1"
loop.1:
  %"count.1" = phi i32 [0, %"loop"], [%"next_var", %"loop.1"]
  %".4" = call i32 @"func"()
  %"next_var" = add i32 %"count.1", 1
  %"loop_cond" = icmp ne i32 %"next_var", 2
  br i1 %"loop_cond", label %"loop.1", label %"after_loop"
after_loop:
  %"next_var.1" = add i32 %"count", 1
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
  %".6" = call i32 @"second"()
  br label %"if_mrg"
else:
  %".8" = call i32 @"func"()
  br label %"if_mrg"
if_mrg:
  %"if_temp" = phi i32 [%".6", %"then"], [%".8", %"else"]
  %".10" = mul i32 5, 2
  %".11" = sdiv i32 %".10", 3
  ret i32 %".11"
}
