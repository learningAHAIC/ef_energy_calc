import tkinter as tk
from tkinter import ttk, messagebox
from fractions import Fraction

import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Win 8.1+
except:
    ctypes.windll.user32.SetProcessDPIAware()       # Win 7



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
    return "当前版本的电池效率为1100和1600，无法完美电量，因此这个方法留在以后再实现\n"


def calculate(N, battery_type, expected_electricity):
    output = []

    # 检查输入参数
    if type(N) != int or N <= 0:
        raise ValueError("分流器数量必须为正整数")
    if N > 256:
        raise ValueError("分流器数量不能超过256")
    if battery_type not in [0, 1]:
        raise ValueError("电池类型必须为0或1")
    if expected_electricity <= 0:
        raise ValueError("期望耗电量必须为正数")
    if expected_electricity % 5 != 0:
        raise ValueError("期望耗电量必须为5的倍数")

    # 静态参数
    Belt_efficiency = Fraction(1, 2)
    Battery_lasting_seconds = 40
    Central = 200

    # 公式
    efficiency = 1100 + battery_type * 500
    energy_generated = efficiency * Battery_lasting_seconds

    # 基础计算
    full_load = (expected_electricity - Central) // efficiency
    target = (expected_electricity - Central) % efficiency
    serving_efficiency = Fraction(target, energy_generated)

    # 如果可以精确分流
    den = serving_efficiency.denominator
    mults = mult_of_two_or_three(den)
    if mults:
        output.append(calc_exact())
        return "".join(output)

    # 分流器计算
    dp = [0 for _ in range(N)]

    max_scaling = Fraction(2) ** N
    target_efficiency = serving_efficiency * max_scaling
    current = Belt_efficiency * max_scaling

    for i in range(N - 1):
        if current > target_efficiency:
            current /= 2
            continue
        elif current < 1:
            raise ValueError("N 不足以表示所需精度，请增大 N")
        dp[i] = 1
        target_efficiency -= current
        current /= 2

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
    actual_efficiency = Fraction(0, 1)
    for i in range(len(dp_actual)):
        actual_efficiency += dp_actual[i] * (Fraction(1, 2) ** i) * Belt_efficiency

    # 输出
    output.append(f"需要 {full_load} 个全速发电器\n")
    output.append(f"实际使用了 {N - is_last_necessary} 个分流器\n")

    temp_list = []
    for i in range(len(dp_actual)):
        if dp_actual[i] > 0:
            temp_list.append(f"第{i + 1}")

    if temp_list:
        output.append(f"需连接 {', '.join(temp_list)} 个分流器至输出口\n")
    else:
        output.append("不需要连接任何分流器至输出口\n")

    interval = Fraction(1, actual_efficiency)
    output.append(f"每 {float(interval):.6f} 秒运送一个电池至发电器 ({interval})\n")

    actual_total = energy_generated * actual_efficiency + full_load * efficiency + Central

    output.append(f"目标效率为 {expected_electricity}\n")
    output.append(f"实际效率为 {float(actual_total):.6f} ({actual_total})\n")

    return "".join(output)


# ================= GUI =================

def on_calculate():
    try:
        N = int(entry_n.get())
        battery_text = combo_battery.get()
        battery_type = 0 if battery_text == "谷地 (1100)" else 1
        expected = int(entry_expected.get())

        result = calculate(N, battery_type, expected)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, result)

    except Exception as e:
        messagebox.showerror("错误", str(e))


root = tk.Tk()
root.title("分流器电池效率计算器")
root.geometry("700x500")

# 输入区
frame_input = ttk.Frame(root, padding=10)
frame_input.pack(fill=tk.X)

ttk.Label(frame_input, text="分流器数量 N:").grid(row=0, column=0, sticky=tk.W, pady=5)
entry_n = ttk.Entry(frame_input)
entry_n.grid(row=0, column=1, pady=5)
entry_n.insert(0, "12")

ttk.Label(frame_input, text="电池类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
combo_battery = ttk.Combobox(frame_input, values=["谷地 (1100)", "武陵 (1600)"], state="readonly")
combo_battery.grid(row=1, column=1, pady=5)
combo_battery.current(0)

ttk.Label(frame_input, text="期望耗电量:").grid(row=2, column=0, sticky=tk.W, pady=5)
entry_expected = ttk.Entry(frame_input)
entry_expected.grid(row=2, column=1, pady=5)
entry_expected.insert(0, "5000")

btn_calc = ttk.Button(frame_input, text="计算", command=on_calculate)
btn_calc.grid(row=3, column=0, columnspan=2, pady=10)

# 输出区
frame_output = ttk.Frame(root, padding=10)
frame_output.pack(fill=tk.BOTH, expand=True)

text_output = tk.Text(frame_output, wrap=tk.WORD)
text_output.pack(fill=tk.BOTH, expand=True)

root.mainloop()
