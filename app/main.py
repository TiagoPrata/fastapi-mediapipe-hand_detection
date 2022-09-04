# https://www.youtube.com/watch?v=NZde8Xt78Iw
# https://www.youtube.com/watch?v=9iEPzbG-xLE

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from hand_tracking_module import HandDetector

app = FastAPI()
hd = HandDetector(min_detection_confidence=0.7)


@app.get("/")
async def root():
    return {"message": "Hello World"}


class InputImg(BaseModel):
    img_base64str : str


@app.post("/find_hands/")
def find_hands(d:InputImg):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    return hd.processed_img()

@app.post("/find_position/")
def find_position(d:InputImg):
    hd.process_hands(d.img_base64str)
    return hd.find_position()

@app.post("/find_thumb_and_index/")
def find_thumb_and_index(d:InputImg):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    hd.find_thumb_and_index()
    hd.line_between_thumb_and_index()
    if hd.get_arrow_length() != None:
        if hd.get_arrow_length() < 60:
            hd.draw_circle_in_the_arrow((0, 255, 0))
        else:
            hd.draw_circle_in_the_arrow()
    hd.calc_arrow_angle()

    return hd.processed_img()

@app.post("/line_between_thumb_and_index/")
def line_between_thumb_and_index(d:InputImg):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    hd.find_thumb_and_index()
    hd.line_between_thumb_and_index()

    return hd.processed_img()

@app.post("/click/")
def get_angle(d:InputImg):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    hd.find_thumb_and_index()
    hd.line_between_thumb_and_index()
    if hd.get_arrow_length() != None:
        if hd.get_arrow_length() < 60:
            hd.draw_circle_in_the_arrow((0, 255, 0))
        else:
            hd.draw_circle_in_the_arrow()

    return hd.processed_img()

@app.post("/get_angle/")
def get_angle(d:InputImg):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    hd.find_thumb_and_index()
    hd.line_between_thumb_and_index()
    if hd.get_arrow_length() != None:
        if hd.get_arrow_length() < 60:
            hd.draw_circle_in_the_arrow((0, 255, 0))
        else:
            hd.draw_circle_in_the_arrow()
            hd.calc_arrow_angle()
            
    hd.putText(str(hd.angle), (10,50), 2)
    return hd.processed_img()

@app.post("/get_angle_value/")
def get_angle_value(d:InputImg):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    hd.find_thumb_and_index()
    hd.line_between_thumb_and_index()
    if hd.get_arrow_length() != None:
        if hd.get_arrow_length() < 60:
            hd.draw_circle_in_the_arrow((0, 255, 0))
        else:
            hd.draw_circle_in_the_arrow()
            hd.calc_arrow_angle()
            
    ret = {hd.angle}
    return ret

@app.post("/get_angle_img_and_value/")
def get_angle_img_and_value(d:InputImg, printAngle: bool = False):
    hd.process_hands(d.img_base64str)
    hd.find_hands()
    hd.find_thumb_and_index()
    hd.line_between_thumb_and_index()
    if hd.get_arrow_length() != None:
        if hd.get_arrow_length() < 60:
            hd.draw_circle_in_the_arrow((0, 255, 0))
        else:
            hd.draw_circle_in_the_arrow()
            hd.calc_arrow_angle()
            
    if printAngle:
        hd.putText(str(hd.angle), (10,50), 2)

    ret = {'img': hd.processed_img(), 'angle': hd.angle}
    
    return ret


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)