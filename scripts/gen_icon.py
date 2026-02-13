"""生成应用图标 - 蓝紫渐变背景 + 白色文字。"""
from PIL import Image, ImageDraw, ImageFont
import os

SIZE = 256
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 圆角矩形背景 - 蓝紫渐变
for y in range(SIZE):
    r = int(50 + (120 - 50) * y / SIZE)
    g = int(100 + (80 - 100) * y / SIZE)
    b = int(220 + (200 - 220) * y / SIZE)
    draw.line([(0, y), (SIZE, y)], fill=(r, g, b, 255))

# 圆角遮罩
mask = Image.new("L", (SIZE, SIZE), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([(0, 0), (SIZE - 1, SIZE - 1)], radius=40, fill=255)
img.putalpha(mask)

# 白色文字 "剧"
try:
    font = ImageFont.truetype("msyh.ttc", 160)
except Exception:
    font = ImageFont.truetype("simsun.ttc", 160)

bbox = draw.textbbox((0, 0), "剧", font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
x = (SIZE - tw) // 2 - bbox[0]
y = (SIZE - th) // 2 - bbox[1]
draw.text((x, y), "剧", fill=(255, 255, 255, 255), font=font)

# 保存为 ico
os.makedirs("assets", exist_ok=True)
img.save("assets/app.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
print("图标已生成: assets/app.ico")
