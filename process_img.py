from PIL import Image, ImageDraw
from io import BytesIO

# def ellipse_params(landmarks):
#     left = tuple([i for i in landmarks["eyeLeftOuter"]])
#     right = tuple([i for i in landmarks["eyeRightOuter"]])
#     bottom = tuple([i for i in landmarks["underLipBottom"]])

TOP_PADDING = 0.40
BOTTOM_PADDING = 0.10
SIDE_PADDING = 0.05

PLATYPUS_X = 950
PLATYPUS_Y = 620

def ellipse_coords(rectangle):
    top = rectangle["top"]
    left = rectangle["left"]
    height = rectangle["height"]
    width = rectangle["width"]
    coords = ((left - round(SIDE_PADDING * width), top - round(TOP_PADDING * height)),
            (left + rectangle["width"] + round(SIDE_PADDING * width), top + rectangle["height"] + round(BOTTOM_PADDING * height)))
    return (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1]), coords

def extract_face(img, size, ell_coords):
    mask = Image.new("L", size, 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse(((0,0), size), 255)

    face = img.crop(ell_coords[0] + ell_coords[1])
    face.putalpha(mask)
    return face

def process(img_data, emotion, rectangle, landmarks):
    img = Image.open(BytesIO(img_data))
    draw = ImageDraw.Draw(img)

    size, ell_coords = ellipse_coords(rectangle)
    face = extract_face(img, size, ell_coords)
    face.show()

    platypus = Image.open("platypuses/0.jpg")
    platypus.paste(face, (PLATYPUS_X - (size[0] // 2), PLATYPUS_Y - (size[1] // 2)), face)
    platypus.show()

    with BytesIO() as buf:
        platypus.save(buf, format="jpeg")
        ret = buf.getvalue()
    return ret