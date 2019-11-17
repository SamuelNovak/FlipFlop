from PIL import Image, ImageDraw
from io import BytesIO

def process(img_data, emotion, landmarks):
    img = Image.open(BytesIO(img_data))
    draw = ImageDraw.Draw(img)
    for l1, l2 in [(i, j) for i in landmarks.keys() for j in landmarks.keys()]:
        pos1 = (landmarks[l1]["x"], landmarks[l1]["y"])
        pos2 = (landmarks[l2]["x"], landmarks[l2]["y"])
        draw.line((pos1, pos2), (255, 255, 255))
    img.show()
    with BytesIO() as buf:
        img.save(buf, format="jpeg")
        ret = buf.getvalue()
    return ret