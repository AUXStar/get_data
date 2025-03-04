#!/usr/bin/env python
# coding=utf-8
###
# @FilePath     : /douyin/utils/webdriver/captcha.py
# @Author       : njzy 48835121@qq.com
# @Date         : 2024-07-30 05:28:47
# @LastEditors  : njzy 48835121@qq.com
# @LastEditTime : 2024-08-05 15:59:32
###

import cv2
import numpy as np
import base64
import openai, json

base_url = "http://192.168.33.165:15237/v1"
api_key = "sk-jrq1nvJYt2WPbobW75870c75B78c44C691E7Fe43CbFaF650"

class Douyin:
    def get_slider(bg_bytes: bytes, ico_bytes: bytes, tip_y: int, width: int) -> int:
        """
        抖音滑块验证码，
        背景照片，滑块照片，y坐标偏移量，图片宽度（计算相对滑动像素）
        """
        bg = cv2.imdecode(np.frombuffer(bg_bytes, np.uint8), cv2.IMREAD_COLOR)
        ico = cv2.imdecode(np.frombuffer(ico_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

        bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
        ico = cv2.cvtColor(ico, cv2.COLOR_BGRA2RGBA)

        ico_height, ico_width, _ = ico.shape

        bg_cut = bg[tip_y * 2 : tip_y * 2 + ico_height, :, :]
        bg_height, bg_width, _ = bg_cut.shape

        for x in ico:
            for y in x:
                if y[3] == 255:
                    y[0] *= 0.5
                    y[1] *= 0.5
                    y[2] *= 0.5

        ico = cv2.cvtColor(ico, cv2.COLOR_RGBA2RGB)
        res = []
        ico_part = np.array(ico, dtype=np.int64)

        for x in range(bg_width - ico_width):
            bg_part = np.array(bg_cut[:, x : x + ico_width, :], dtype=np.int64)
            s = abs(ico_part - bg_part)
            res.append(s.sum())
        x_p = np.argmin(res)
        y_p = 2 * tip_y
        x_f = x_p + ico_width
        y_f = y_p + ico_height

        bg[y_p, x_p:x_f] = [255, 0, 255]
        bg[y_f, x_p:x_f] = [255, 0, 255]
        bg[y_p:y_f, x_p] = [255, 0, 255]
        bg[y_p:y_f, x_f] = [255, 0, 255]
        return width / bg_width * x_p

    def openai_choice(img: bytes):
        """
        openai gpt-4o图片识别能力
        """
        jpg_b64 = base64.b64encode(img).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{jpg_b64}"
        user_prompt = (
            "图中哪两个物体形状相同？\n" "给出他们的序号，序号是他们左上角的数字"
        )
        client = openai.Client(base_url=base_url, api_key=api_key)
        model = "gpt-4o"
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个有用的助手。你是一个聪明的图片处理助手，擅长给出满足条件图形的坐标。你总是遵循用户的条件来寻找特定图形。你被输入一些图片和指令，你需要按照指令的要求，根据图片中的信息做出响应。你需要尽可能仔细地观察图中的信息，比如坐标轴和辅助线。",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}},
                    ],
                },
            ],
        )

        reply = completion.choices[0].message.content
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个文字处理助手，你被输入一些文字和指令，你需要按照指令的要求，将输入格式为满足格式要求的 json。注意你只能修改原内容的格式，不能够修改原本的数据。你必须严格遵守 user prompt 要求的格式，不能随意篡改格式。将你的回复格式化为 json，你的响应必须是可解析的 json 内容。不可以出现多于的东西，比如 code block ```。你的输出必须只包含纯粹的 json。你的输出必须是可解析的 json。你的输出必须完全满足用户要求的格式。",
                },
                {"role": "assistant", "content": reply},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "从响应中提取两个点的序号\n"
                            "将你的回复格式化为 json，你的响应必须是可解析的 json 内容。不可以出现多于的东西，比如 code block ```\n"
                            "json 格式：\n"
                            "[p1, p2]\n",
                        }
                    ],
                },
            ],
        )
        result = json.loads(completion.choices[0].message.content)
        return result

    def get_choice(img_bytes: bytes, width: int, height: int):
        """
        抖音点选验证码
        """
        img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_h, img_w, _ = img.shape
        bl = cv2.GaussianBlur(img, (11, 11), 1)
        mask = np.var(bl, axis=2) < 35
        img[mask] = (255, 255, 255)
        mask = np.all(bl > 180, axis=2)
        img[mask] = (255, 255, 255)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        thresh1 = 255 - cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 777, 2
        )
        thresh1 = cv2.GaussianBlur(thresh1, (3, 3), 1)
        _, thresh1 = cv2.threshold(thresh1, 230, 255, cv2.THRESH_BINARY)
        tc = cv2.cvtColor(thresh1, cv2.COLOR_GRAY2RGB)
        img = np.bitwise_and(img, tc)
        # 以上去除图片元素，分离白色背景
        contours, _ = cv2.findContours(
            thresh1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        # 颜色分割
        c1 = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            i = img.copy()
            cv2.drawContours(i, [contour], -1, (0, 0, 0), -1)

            box = cv2.bitwise_xor(i, img)[y : y + h, x : x + w]
            box = cv2.cvtColor(box, cv2.COLOR_RGB2HSV)
            hue_channel = box[:, :, 0]
            hist = np.histogram(hue_channel.flatten(), 180, [0, 180])[0][1:]
            bins = np.where(hist > np.mean(hist[hist != 0]))[0] + 1
            if len(bins) <= 1:
                c1.append(contour)
                continue
            bins1 = []
            bins2 = []
            for i in range(len(bins)):
                bins2.append(bins[i])
                if i + 1 == len(bins) or abs(bins[i] - bins[i + 1]) > 5:
                    bins1.append(max(bins2))
                    bins2 = []
            if bins2:
                bins1.append(max(bins2))
            for bi in bins1:
                lower_range = np.array([bi - 2, 0, 0])
                upper_range = np.array([bi + 2, 255, 255])
                mask = cv2.inRange(box, lower_range, upper_range)
                mask = cv2.GaussianBlur(mask, (99, 99), 3)
                _, thresh = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
                cs, _ = cv2.findContours(
                    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                imsh = cv2.cvtColor(box, cv2.COLOR_HSV2RGB)
                for c in cs:
                    x1, y1, w1, h1 = cv2.boundingRect(c)
                    cv2.rectangle(imsh, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                    c1.append(c + [x, y])
        bounding_boxes = []
        for contour in c1:
            x, y, w, h = cv2.boundingRect(contour)
            # if w<10 or h <20:
            #     continue
            bounding_boxes.append((x, y, w, h))
        bounding_boxes_sorted = sorted(
            bounding_boxes, key=lambda x: (x[2] * x[3]), reverse=True
        )
        selected_boxes = []
        items = {}
        index = 0
        img[np.all(img == (0, 0, 0), axis=-1)] = (255, 255, 255)
        for i, box in enumerate(bounding_boxes_sorted):
            x, y, w, h = box
            overlap = False
            for selected_box in selected_boxes:
                x1, y1, w1, h1 = selected_box
                # if x < x1 + w1 and x + w > x1 and y < y1 + h1 and y + h > y1:
                #     overlap = True
                #     break
            if not overlap:
                # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                tid = index
                selected_boxes.append(box)
                items[tid] = (x + w // 2, y + h // 2)
                cv2.circle(img, (x + w // 2, y + h // 2), 2, (0, 0, 0), 2)
                cv2.putText(
                    img,
                    str(tid),
                    (x + w // 4, y + h // 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 0),
                    2,
                )
                cv2.putText(
                    img,
                    str(tid),
                    (x + w // 4, y + h // 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    1,
                )
                index += 1
        _, enc = cv2.imencode(".jpg", img)
        jpg_bytes = enc.tobytes()
        a = Douyin.openai_choice(jpg_bytes)
        i = [items[p] for p in a.json()]
        # [cv2.circle(img,(x,y),10,(0,0,255),3) for x,y in i]
        # cv2.imshow(' ',img)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        return [(width / img_w * x, height / img_h * y) for x, y in i]
