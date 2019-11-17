import json
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO
from random import choice

# def ellipse_params(landmarks):
#     left = tuple([i for i in landmarks["eyeLeftOuter"]])
#     right = tuple([i for i in landmarks["eyeRightOuter"]])
#     bottom = tuple([i for i in landmarks["underLipBottom"]])

TOP_PADDING = 0.40
BOTTOM_PADDING = 0.10
SIDE_PADDING = 0.05

WIDTH = 640
HEIGHT = 480

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
    mask = mask.filter(ImageFilter.BLUR)

    face = img.crop(ell_coords[0] + ell_coords[1])
    face.putalpha(mask)
    return face

def random_background():
    with open("animals/faces.json", "r") as f:
        faces = json.loads(f.read())
    bg_file = choice(list(faces.keys()))
    bg = Image.open("animals/" + bg_file)
    return bg, tuple(faces[bg_file])

def attach_face_to_background(face, background, pos):
    w, h = background.size
    par = max((w / WIDTH, h / HEIGHT))
    if par >= 2:
        background = background.resize((int(w // min(2, par)), int(h // min(2, par))))
        background.paste(face, (int((pos[0] - (face.size[0] // 2)) // min(2, par)), int((pos[1] - (face.size[1] // 2)) // min(2, par))), face)
    else:
        background.paste(face, (pos[0] - (face.size[0] // 2), pos[1] - (face.size[1] // 2)), face)
    return background

def process(img_data, emotion, rectangle, landmarks):
    img = Image.open(BytesIO(img_data))

    size, ell_coords = ellipse_coords(rectangle)
    face = extract_face(img, size, ell_coords)

    background, fpos = random_background()
    result = attach_face_to_background(face, background, fpos)
    # result.show()

    with BytesIO() as buf:
        result.save(buf, format="jpeg")
        ret = buf.getvalue()
    return ret
