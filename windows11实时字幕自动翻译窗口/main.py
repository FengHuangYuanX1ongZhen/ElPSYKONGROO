# ****请将window11的实时字幕字体设置为非等宽有衬线,背景设置为不透明,一次翻译三行,不要一次性翻译太多,可能会被ban

# 用于消除paddleocr中的调试信息
import logging

logging.disable(logging.DEBUG)

import win32gui
from PIL import ImageGrab
from PIL import ImageChops
from PIL import Image
from paddleocr import PaddleOCR
import translators
import tkinter
import threading


# from transformers import pipeline, AutoModelWithLMHead, AutoTokenizer
# import warnings
# warnings.filterwarnings('ignore')


# def translate(sentence):  # 旧版有道翻译，被玩没了，不知道ban多久
#     api = 'http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i='
#     response = requests.get(f'{api}{sentence}').json()
#     chinese = " "
#     for sub in response['translateResult'][0]:
#         chinese += sub['tgt']
#         print(sub['tgt'], end="")  # 将翻译结果显示出来
#     return chinese

def translate(
        english):  # 利用translators库进行翻译，里面包含了google,deepl,baidu,youdao等等，具体信息可以print(translators.translate_pool)查看,有频率限制
    if english:
        chinese = translators.translate_text(english, from_language='en', to_language='zh',
                                             translator='caiyun')  # 试了几个translator，感觉caiyun比较好
        # print(chinese) #测试用代码
        return chinese


def detect_change(x1, y1, x2, y2):  # 检测字幕窗口的变化
    global flag
    while True:
        img_after = ImageGrab.grab((x1, y1, x2, y2))  # 截图
        # img_after.show()  # 展示
        image_before = Image.open("content.PNG")
        diff = ImageChops.difference(image_before, img_after)
        if diff.getbbox() is not None:  # 当字幕有变化再中止循环,继续执行程序
            img_after.save("content.PNG")
            flag = True
        else:
            flag = False


def caption(ocr):  # 从截取下来的图片中取字
    if flag:
        text = ocr.ocr('content.PNG', cls=False)  # 打开图片文件
        # print(text) #测试用代码
        # 打印所有文本信息
        english = ""
        for t in text[0]:
            english += t[1][0] + " "
            # print(t[1][0]) #测试用代码
        # print(english) #测试用代码
        return english


def final_function():  # 整合函数
    english = caption(ocr)
    result = translate(english)
    # print(result) #测试用代码
    if result:
        content.set(result)
    window.after(30, final_function)  # 一个流程跑完暂停300ms,不要为了中英文同步,作死调低导致ip被ban,我有一个朋友......


if __name__ == '__main__':
    # 部署本地翻译模型，翻译准确性较低
    # modelName = 'Helsinki-NLP/opus-mt-en-zh'
    # model = AutoModelWithLMHead.from_pretrained(modelName)
    # tokenizer = AutoTokenizer.from_pretrained(modelName)
    # translation = pipeline('translation_en_to_zh', model=model, tokenizer=tokenizer)

    handle = win32gui.FindWindow("LiveCaptionsDesktopWindow", "实时辅助字幕")  # 获取窗口句柄
    (x1, y1, x2, y2) = win32gui.GetWindowRect(handle)
    ocr = PaddleOCR(use_angle_cls=False, lang="en", enable_mkldnn=False, use_gpu=True, gpu_mem=2000,
                    rec_model_dir='./inference/en_PP-OCRv3_rec_infer',
                    det_model_dir='./inference/en_PP-OCRv3_det_infer')

    flag = True  # 记录字幕窗口是否有变化
    # 创造一个线程来运行对字幕窗口是否有变化的实时检测
    det = threading.Thread(target=detect_change, args=(x1 + 500, y1 + 200, x2 - 200, y2 + 230))
    det.start()

    window = tkinter.Tk()  # 生成一个主窗口对象
    window.title("垃圾机翻")
    window.geometry('600x120')
    # 创建绑定字符串
    content = tkinter.StringVar()
    content.set("Hello, world!")
    # 实例化标签组件
    label = tkinter.Label(window, textvariable=content, font=("微软雅黑", 15, 'bold'))
    label.config(wraplength=500, justify=tkinter.LEFT)
    label.pack()

    # 创造一个线程来运行主流程
    run = threading.Thread(target=final_function)
    run.start()

    window.mainloop()
