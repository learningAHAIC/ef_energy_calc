from fractions import Fraction
from PIL import Image

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
    print("当前版本的电池效率为1100和1600，无法完美电量，因此这个方法留在以后再实现")
    return


def build_big_image(arr, img1_path, img2_path, img3_path, img4_path, img5_path):
    # 读取图片
    img1 = Image.open(img1_path).convert("RGBA")
    img2 = Image.open(img2_path).convert("RGBA")
    img3 = Image.open(img3_path).convert("RGBA")
    img4 = Image.open(img4_path).convert("RGBA")
    img5 = Image.open(img5_path).convert("RGBA")

    generator_path = './src/img/generator.png'
    generator = Image.open(generator_path).convert("RGBA")

    # # 统一尺寸
    size = (224, 224)
    # img1 = img1.resize(size)
    # img2 = img2.resize(size)
    # img3 = img3.resize(size)
    # img4 = img4.resize(size)
    # img5 = img5.resize(size)

    w, h = size

    # 旋转版本
    img1_r90 = img1.rotate(-90, expand=False)   # 右转90°
    img2_r180 = img2.rotate(180, expand=False)  # 180°
    img1_r180 = img1.rotate(180, expand=False)

    # 空白块
    blank = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    n = len(arr)

    # 总列数 = 原来的 n 列 + 右侧 2 列
    total_cols = n + 2

    big_w = (total_cols + 1) * w + generator.width 
    big_h = 4 * h
    big_img = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))

    # 最左边新增一列：1, blank, blank, 1(r180)
    x = 0
    col_imgs = [img1, blank, blank, img1_r180]
    for j, tile in enumerate(col_imgs):
        y = j * h
        big_img.paste(tile, (x, y), tile)

    seen_first_one = False  # 是否已经遇到过第一个 1

    for i in range(n):
        x = (i + 1) * w

        v = arr[i]

        # 最后一列：强制按 0 的样式（“已遇到1之后”的版本）
        if i == n - 1:
            col_imgs = [img3, img4, img1_r90, img2_r180]
        else:
            if v == 1:
                seen_first_one = True
                col_imgs = [img3, img2, blank, img2_r180]
            else:
                if not seen_first_one:
                    # 第一个 1 之前的 0
                    col_imgs = [img3, img1_r90, img1_r90, img2_r180]
                else:
                    # 第一个 1 之后的 0
                    col_imgs = [img3, img4, img1_r90, img2_r180]

        for j, tile in enumerate(col_imgs):
            y = j * h
            big_img.paste(tile, (x, y), tile)

    # 追加的第 1 列：2, 5, blank, blank
    x = (n + 1) * w
    col_imgs = [img2, img5, blank, blank]
    for j, tile in enumerate(col_imgs):
        y = j * h
        big_img.paste(tile, (x, y), tile)

    # 追加的第 2 列：1, blank, blank, blank
    x = (n + 2) * w
    col_imgs = [img1, blank, blank, blank]
    for j, tile in enumerate(col_imgs):
        y = j * h
        big_img.paste(tile, (x, y), tile)

    # 追加的第 3 列：generator
    x = (n + 3) * w
    y = 0
    big_img.paste(generator, (x, y), generator)

    return big_img

def main():
    # 输入参数
    N = 13  # 分流器数量
    battery_type = 0  # 电池类型，0 谷地, 1 武陵
    expected_electricity = 4695  # 期望耗电量

    # 检查输入参数
    if type(N) != int or N <= 0:
        print("分流器数量必须为正整数")
        return
    if N > 256:
        print("分流器数量不能超过256")
        return
    if battery_type not in [0, 1]:
        print("电池类型必须为0或1")
        return
    if expected_electricity <= 0:
        print("期望耗电量必须为正数")
        return
    if expected_electricity % 5 != 0:
        print("期望耗电量必须为5的倍数")
        return

    # 静态参数
    Belt_efficiency = Fraction(1, 2)
    Battery_lasting_seconds = 40
    Central_power_generated = 200

    # 公式
    energy_generated_per_generator = 1100 + battery_type * 500
    energy_generated_per_battery = energy_generated_per_generator * Battery_lasting_seconds

    # 基础计算
    full_load = (expected_electricity - Central_power_generated) // energy_generated_per_generator      # 全速发电机数量
    target = (expected_electricity - Central_power_generated) % energy_generated_per_generator          # 目标发电效率
    serving_efficiency = Fraction(target, energy_generated_per_battery)         # 供应电池比例

    # 如果可以用1分2和1分3完美分出，则不需要近似计算
    den = serving_efficiency.denominator
    mults = mult_of_two_or_three(den)
    if mults and serving_efficiency.numerator != 0:
        calc_exact()
        return

    # 分流器计算
    dp = [0 for _ in range(N)]

    max_scaling = Fraction(2) ** N
    target_efficiency = serving_efficiency * max_scaling
    current = Belt_efficiency * max_scaling

    for i in range(N - 1):
        current /= 2
        if current > target_efficiency:
            continue
        dp[i] = 1
        target_efficiency -= current

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
        actual_efficiency += dp_actual[i] * (Fraction(1, 2) ** (i + 1)) * Belt_efficiency

    # 输出
    print(f"需要 {full_load} 个全速发电器")
    print(f"实际使用了 {N - is_last_necessary} 个分流器")

    temp_list = []
    for i in range(len(dp_actual)):
        if dp_actual[i] > 0:
            temp_list.append(f"第{i + 1}")

    if temp_list:
        print(f"需连接{', '.join(temp_list)}个分流器至输出口")
    else:
        print("不需要连接任何分流器至输出口")

    interval = Fraction(1, actual_efficiency)
    print(f"每 {float(interval):.6f} 秒运送一个电池至发电器 ({interval})")

    actual_total = energy_generated_per_battery * actual_efficiency + full_load * energy_generated_per_generator + Central_power_generated

    print(f"目标效率为 {expected_electricity}")
    print(f"实际效率为 {float(actual_total):.6f} ({actual_total})")

    path = "src/img/"
    suffix = ".png"

    big = build_big_image(
        dp_actual,
        path + "belt" + suffix,
        path + "combiner" + suffix,
        path + "diverter" + suffix,
        path + "logistics_bridge" + suffix,
        path + "belt_turn" + suffix, 
    )

    big.show()


if __name__ == "__main__":
    main()
