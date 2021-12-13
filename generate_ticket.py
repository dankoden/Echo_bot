from io import BytesIO
import requests
from PIL import ImageFont,Image,ImageDraw
AVATAR_OFFSET = (100,125)

def generate_ticket(name,email):

    base = Image.open("Files/ticket.png")
    font = ImageFont.truetype("Files/arial.ttf",20)

    draw = ImageDraw.Draw(base)
    draw.text((290,130),f"{name}",font=font,fill = "black",)
    draw.text((220,155),f"{email}",font=font,fill = "black",)

    responce = requests.get("https://www.embarcadero.com/images/new-tools/PyScripter_IDE_Logosvg.png")
    avatar = Image.open(BytesIO(responce.content))
    width = 64
    height = 64
    resized_img = avatar.resize((width, height), Image.ANTIALIAS)
    base.paste(resized_img,AVATAR_OFFSET)

    tem_file = BytesIO()
    base.save(tem_file,"png")
    tem_file.seek(0)

    return tem_file



print(generate_ticket("Ihor","i.ok.danko@gmail.com"))