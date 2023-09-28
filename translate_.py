from googletrans import Translator


def get_language(txt):
    tr = Translator()
    res = tr.detect(txt)
    return res.lang


def translate(txt, source_lang, dest_lang):
    tr = Translator()
    print(txt)
    res = tr.translate(txt, src=source_lang, dest=dest_lang)
    return res.text


if __name__ == '__main__':
    print(get_language('0xA'))
    #print(translate('Hello', 'en', 'ru'))