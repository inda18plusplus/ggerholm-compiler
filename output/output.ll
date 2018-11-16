; ModuleID = "C:\Programming\School\LLVMCompiler\compiler\codegen.py"
target triple = "i686-pc-windows-msvc"
target datalayout = ""

@"println_number" = internal constant [6 x i8] c"%lld\0a\00"
@"input_number" = internal constant [5 x i8] c"%lld\00"
declare i64 @"printf"(i8* %".1", ...) 

declare i64 @"scanf"(i8* %".1", ...) 

define i64 @"func"(i64 %"x") 
{
entry:
  %"x.1" = alloca i64
  store i64 %"x", i64* %"x.1"
  %".4" = bitcast [6 x i8]* @"println_number" to i8*
  %"x.2" = load i64, i64* %"x.1"
  %".5" = icmp eq i64 5, 0
  %".6" = select i1 %".5", i64 1, i64 0
  %".7" = add i64 5, %".6"
  %".8" = sub i64 %".7", 1
  %".9" = mul i64 %"x.2", %".8"
  %".10" = sub i64 0, %".9"
  %".11" = xor i64 2, -1
  %".12" = mul i64 5, %".11"
  %".13" = add i64 %".10", %".12"
  %".14" = sdiv i64 %".13", 5
  %".15" = call i64 (i8*, ...) @"printf"(i8* %".4", i64 %".14")
  ret i64 0
}

define i64 @"second"(i64 %"x", i64 %"y") 
{
entry:
  %"x.1" = alloca i64
  store i64 %"x", i64* %"x.1"
  %"y.1" = alloca i64
  store i64 %"y", i64* %"y.1"
  %".6" = bitcast [6 x i8]* @"println_number" to i8*
  %"y.2" = load i64, i64* %"y.1"
  %".7" = mul i64 4, %"y.2"
  store i64 %".7", i64* %"x.1"
  %".9" = call i64 (i8*, ...) @"printf"(i8* %".6", i64 %".7")
  %".10" = bitcast [5 x i8]* @"input_number" to i8*
  %".11" = call i64 (i8*, ...) @"scanf"(i8* %".10", i64* %"x.1")
  %"x.2" = load i64, i64* %"x.1"
  %".12" = sub i64 0, %"x.2"
  %".13" = sub i64 0, 4
  %".14" = icmp sle i64 %".12", %".13"
  br i1 %".14", label %"then", label %"else"
then:
  %".16" = bitcast [6 x i8]* @"println_number" to i8*
  %".17" = call i64 (i8*, ...) @"printf"(i8* %".16", i64 500000)
  br label %"after_if"
else:
  %"x.3" = load i64, i64* %"x.1"
  %"y.3" = load i64, i64* %"y.1"
  %".19" = add i64 %"x.3", %"y.3"
  store i64 %".19", i64* %"y.1"
  br label %"after_if"
after_if:
  %"if_phi" = phi i64 [%".17", %"then"], [%".19", %"else"]
  %".22" = bitcast [6 x i8]* @"println_number" to i8*
  %"y.4" = load i64, i64* %"y.1"
  %".23" = call i64 (i8*, ...) @"printf"(i8* %".22", i64 %"y.4")
  ret i64 5
}

define i64 @"main"() 
{
entry:
  %".2" = bitcast [6 x i8]* @"println_number" to i8*
  %".3" = mul i64 2, 6
  %".4" = call i64 (i8*, ...) @"printf"(i8* %".2", i64 %".3")
  %".5" = add i64 1, 2
  %".6" = sub i64 %".5", 4
  %".7" = icmp sgt i64 %".6", 0
  br i1 %".7", label %"then", label %"else"
then:
  %".9" = call i64 @"func"(i64 50)
  br label %"after_if"
else:
  %".11" = call i64 @"second"(i64 5, i64 2)
  %".12" = bitcast [6 x i8]* @"println_number" to i8*
  %".13" = call i64 (i8*, ...) @"printf"(i8* %".12", i64 3)
  br label %"after_if"
after_if:
  %"if_phi" = phi i64 [%".9", %"then"], [%".13", %"else"]
  %"i" = alloca i64
  store i64 2, i64* %"i"
  br label %"loop"
loop:
  %".17" = bitcast [6 x i8]* @"println_number" to i8*
  %"i.1" = load i64, i64* %"i"
  %".18" = call i64 (i8*, ...) @"printf"(i8* %".17", i64 %"i.1")
  %"j" = alloca i64
  store i64 0, i64* %"j"
  br label %"loop.1"
loop.1:
  %"i.2" = load i64, i64* %"i"
  %".21" = sub i64 %"i.2", 1
  store i64 %".21", i64* %"i"
  %"j.1" = load i64, i64* %"j"
  %"next_value" = add i64 %"j.1", 1
  store i64 %"next_value", i64* %"j"
  %"j.2" = load i64, i64* %"j"
  %".24" = icmp slt i64 %"j.2", 2
  %"loop_cond" = icmp ne i1 %".24", 0
  br i1 %"loop_cond", label %"loop.1", label %"after_loop"
after_loop:
  %".26" = sub i64 0, 1
  %"i.3" = load i64, i64* %"i"
  %"next_value.1" = add i64 %"i.3", %".26"
  store i64 %"next_value.1", i64* %"i"
  %"i.4" = load i64, i64* %"i"
  %".28" = sub i64 0, 5
  %".29" = icmp sgt i64 %"i.4", %".28"
  %"loop_cond.1" = icmp ne i1 %".29", 0
  br i1 %"loop_cond.1", label %"loop", label %"after_loop.1"
after_loop.1:
  %".31" = mul i64 2, 4
  %".32" = sdiv i64 %".31", 3
  ret i64 %".32"
}
