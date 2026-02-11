from fractions import Fraction
import math

def mult_of_two_or_three(x):
    if x <= 0:
        return False

    mults = [0, 0]

    while x % 2 == 0:
        mults[0] += 1
        x //= 2
    while x % 3 == 0:
        mults[1] += 1
        x //= 3

    if x == 1:
        return mults
    else:
        return False
    
def calc_exact():
    # TODO
    
    return

def main():
    # 输入参数
    N = 30 # 分流器数量
    battery_type = 0 # 电池类型，0 谷地, 1 武陵
    expected_electricity = 200+1100+Fraction(44000, 486)# 期望耗电量

    # 静态参数
    Belt_efficiency = 0.5
    Battery_lasting_seconds = 40
    Central = 200

    # 公式
    efficiency = 1100 + battery_type * 500
    energy_generated = efficiency * Battery_lasting_seconds

    # 基础计算
    full_load = (expected_electricity - Central) // efficiency      # 全速发电机数量
    target = (expected_electricity - Central) % efficiency          # 目标发电效率，等效平均发电效率
    serving_efficiency = Fraction(target, energy_generated)   # 供应电池间隔

    # 如果可以用1分2和1分3完美分出，则不需要近似计算
    den = serving_efficiency.denominator
    mults = mult_of_two_or_three(den)
    if mults:
        calc_exact()
        return

    # 分流器计算
    dp = [0 for _ in range(N)]

    max_scaling = math.pow(2, N)
    target_efficiency = float(serving_efficiency) * max_scaling
    current = Belt_efficiency * max_scaling

    for i in range(N - 1):
        if current > target_efficiency:
            current = current / 2
            continue
        elif current < 1:
            print("***** There is a calculation error. *****")
            break
        dp[i] = 1
        target_efficiency -= current
        current = current / 2

    is_last_necessary = 0
    if current > target_efficiency:
        if current / 2 > target_efficiency:
            dp[N - 1] = 1
        else:
            dp[N - 1] = 2
    else:
        dp[N - 2] += 1

    check = 2
    i = N - 1
    while check > 0 and i > 0:
        if dp[i] > 1:
            dp[i - 1] += 1
            dp[i] -= 2
            is_last_necessary = N - i
        elif dp[i] == 0 and check == 2:
            is_last_necessary = 1
        else:
            check -= 1
        i -= 1

    # 计算实际发电效率
    dp_actual = dp[:N - is_last_necessary]
    actual_efficiency = 0
    for i in range(N - is_last_necessary):
        actual_efficiency += dp_actual[i] * math.pow(0.5, i) * Belt_efficiency


    # 输出
    print(f"需要{full_load}个全速发电器")
    # print(dp_actual)
    print(f"实际使用了{N - is_last_necessary}个分流器")
    temp_string = ""
    for i in range(len(dp_actual)):
        if dp_actual[i] > 0:
            temp_string += f"第{i + 1}, "
    temp_string = temp_string[:-2]
    print(f"需连接{temp_string}个分流器至输出口")
    print(f"每 {1 / actual_efficiency} 秒运送一个电池至发电器")
    print(f"目标效率为 {expected_electricity}")
    print(f"实际效率为 {energy_generated * actual_efficiency + full_load * efficiency + Central}")
    print("计算完毕")




if __name__ == "__main__":
    main()