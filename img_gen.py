from PIL import Image

def build_big_image(arr, img1_path, img2_path, img3_path, img4_path, img5_path):
    # 读取图片
    img1 = Image.open(img1_path).convert("RGBA")
    img2 = Image.open(img2_path).convert("RGBA")
    img3 = Image.open(img3_path).convert("RGBA")
    img4 = Image.open(img4_path).convert("RGBA")
    img5 = Image.open(img5_path).convert("RGBA")

    # 统一尺寸
    size = (224, 224)
    img1 = img1.resize(size)
    img2 = img2.resize(size)
    img3 = img3.resize(size)
    img4 = img4.resize(size)
    img5 = img5.resize(size)

    w, h = size

    # 旋转版本
    img1_r90 = img1.rotate(-90, expand=False)   # 右转90°
    img2_r180 = img2.rotate(180, expand=False)  # 180°

    # 空白块
    blank = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    n = len(arr)

    # 总列数 = 原来的 n 列 + 右侧 2 列
    total_cols = n + 2

    big_w = total_cols * w
    big_h = 4 * h
    big_img = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))

    seen_first_one = False  # 是否已经遇到过第一个 1

    for i in range(n):
        x = i * w

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
    x = n * w
    col_imgs = [img2, img5, blank, blank]
    for j, tile in enumerate(col_imgs):
        y = j * h
        big_img.paste(tile, (x, y), tile)

    # 追加的第 2 列：1, blank, blank, blank
    x = (n + 1) * w
    col_imgs = [img1, blank, blank, blank]
    for j, tile in enumerate(col_imgs):
        y = j * h
        big_img.paste(tile, (x, y), tile)

    return big_img


arr = [0, 0, 0, 1, 0, 0, 1]  # 例子（保证最后是1）
path = "src/img/"
suffix = ".png"

big = build_big_image(
    arr,
    path + "belt" + suffix,
    path + "combiner" + suffix,
    path + "diverter" + suffix,
    path + "logistics_bridge" + suffix,
    path + "belt_turn" + suffix, # TODO: 改成拐弯传送带！！！
)

big.save("output.png")
big.show()
