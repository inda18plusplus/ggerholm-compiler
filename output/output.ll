; ModuleID = "C:\Programming\School\LLVMCompiler\compiler\codegen.py"
target triple = "i686-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...) 

define i32 @"func"(i32 %"x") 
{
entry:
  %"x.1" = alloca i32
  store i32 %"x", i32* %"x.1"
  %"x.2" = load i32, i32* %"x.1"
  %".4" = icmp eq i32 5, 0
  %".5" = select i1 %".4", i32 1, i32 0
  %".6" = add i32 5, %".5"
  %".7" = sub i32 %".6", 1
  %".8" = mul i32 %"x.2", %".7"
  %".9" = sub i32 0, %".8"
  %".10" = xor i32 2, -1
  %".11" = mul i32 5, %".10"
  %".12" = add i32 %".9", %".11"
  %".13" = sdiv i32 %".12", 5
  %".14" = bitcast [5 x i8]* @"f_str" to i8*
  %".15" = call i32 (i8*, ...) @"printf"(i8* %".14", i32 %".13")
  ret i32 0
}

@"f_str" = internal constant [5 x i8] c"%i \0a\00"
define i32 @"second"(i32 %"x", i32 %"y") 
{
entry:
  %"x.1" = alloca i32
  store i32 %"x", i32* %"x.1"
  %"y.1" = alloca i32
  store i32 %"y", i32* %"y.1"
  %"y.2" = load i32, i32* %"y.1"
  %".6" = mul i32 4, %"y.2"
  store i32 %".6", i32* %"x.1"
  %".8" = bitcast [5 x i8]* @"f_str" to i8*
  %".9" = call i32 (i8*, ...) @"printf"(i8* %".8", i32 %".6")
  %"x.2" = load i32, i32* %"x.1"
  %".10" = sub i32 %"x.2", 4
  store i32 %".10", i32* %"x.1"
  %"x.3" = load i32, i32* %"x.1"
  %".12" = sub i32 0, %"x.3"
  %".13" = sub i32 0, 4
  %".14" = icmp sle i32 %".12", %".13"
  br i1 %".14", label %"then", label %"else"
then:
  %".16" = bitcast [5 x i8]* @"f_str" to i8*
  %".17" = call i32 (i8*, ...) @"printf"(i8* %".16", i32 500000)
  br label %"after_if"
else:
  %"x.4" = load i32, i32* %"x.1"
  %"y.3" = load i32, i32* %"y.1"
  %".19" = add i32 %"x.4", %"y.3"
  store i32 %".19", i32* %"y.1"
  br label %"after_if"
after_if:
  %"if_phi" = phi i32 [%".17", %"then"], [%".19", %"else"]
  %"y.4" = load i32, i32* %"y.1"
  %".22" = bitcast [5 x i8]* @"f_str" to i8*
  %".23" = call i32 (i8*, ...) @"printf"(i8* %".22", i32 %"y.4")
  ret i32 5
}

define i32 @"main"() 
{
entry:
  %".2" = add i32 1, 2
  %".3" = sub i32 %".2", 4
  %".4" = icmp sgt i32 %".3", 0
  br i1 %".4", label %"then", label %"else"
then:
  %".6" = call i32 @"func"(i32 50)
  br label %"after_if"
else:
  %".8" = call i32 @"second"(i32 5, i32 2)
  %".9" = bitcast [5 x i8]* @"f_str" to i8*
  %".10" = call i32 (i8*, ...) @"printf"(i8* %".9", i32 3)
  br label %"after_if"
after_if:
  %"if_phi" = phi i32 [%".6", %"then"], [%".10", %"else"]
  %".12" = mul i32 2, 6
  %".13" = bitcast [5 x i8]* @"f_str" to i8*
  %".14" = call i32 (i8*, ...) @"printf"(i8* %".13", i32 %".12")
  %"i" = alloca i32
  store i32 2, i32* %"i"
  br label %"loop"
loop:
  %"i.1" = load i32, i32* %"i"
  %".17" = bitcast [5 x i8]* @"f_str" to i8*
  %".18" = call i32 (i8*, ...) @"printf"(i8* %".17", i32 %"i.1")
  %"j" = alloca i32
  store i32 0, i32* %"j"
  br label %"loop.1"
loop.1:
  %"i.2" = load i32, i32* %"i"
  %".21" = sub i32 %"i.2", 1
  store i32 %".21", i32* %"i"
  %"j.1" = load i32, i32* %"j"
  %"next_value" = add i32 %"j.1", 1
  store i32 %"next_value", i32* %"j"
  %"j.2" = load i32, i32* %"j"
  %".24" = icmp slt i32 %"j.2", 2
  %"loop_cond" = icmp ne i1 %".24", 0
  br i1 %"loop_cond", label %"loop.1", label %"after_loop"
after_loop:
  %".26" = sub i32 0, 1
  %"i.3" = load i32, i32* %"i"
  %"next_value.1" = add i32 %"i.3", %".26"
  store i32 %"next_value.1", i32* %"i"
  %"i.4" = load i32, i32* %"i"
  %".28" = sub i32 0, 5
  %".29" = icmp sgt i32 %"i.4", %".28"
  %"loop_cond.1" = icmp ne i1 %".29", 0
  br i1 %"loop_cond.1", label %"loop", label %"after_loop.1"
after_loop.1:
  %".31" = mul i32 2, 4
  %".32" = sdiv i32 %".31", 3
  ret i32 %".32"
}
