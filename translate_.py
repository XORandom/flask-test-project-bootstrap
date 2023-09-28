from googletrans import Translator


def get_language(txt):
    tr = Translator()
    return tr.detect(txt).lang


def translate(txt, source_lang, dest_lang):
    tr = Translator()
    res = tr.translate(txt, src=source_lang, dest=dest_lang)
    return res.text
