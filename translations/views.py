import json
import logging

from django.template import loader
from django.http import *
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist

from models import WordZH, WordPL, WordTranslation

logger = logging.getLogger(__name__)


def dictionary(request, source_language):
    """
    Word dictionary. It translates words from source language.
    :param request: HTTP request
    :param source_language: language to translate words from
    :return: HTTP response
    """
    if request.method == 'POST':
        word_to_search = request.POST['word_to_search']
        translations = []
        matching_words = []
        if request.POST['source_language'] == "polish":
            matching_words = WordPL.objects.filter(word=word_to_search)
        elif request.POST['source_language'] == "chinese":
            matching_words = WordZH.objects.filter(word=word_to_search)
        if matching_words:
            translations = matching_words[0].get_translations().values_list('word', flat=True)
        return HttpResponse(json.dumps({'translations': list(translations)}), mimetype='application/javascript')
    template = loader.get_template('translations/dictionary.html')
    context = RequestContext(request, {'source_language': source_language})
    return HttpResponse(template.render(context))


def words_translations_management(request, source_language):
    """
    Manage words translations. Allow selecting words to edit.
    If exist display available translations.
    :param request: HTTP request
    :param source_language: language to translate words from
    :return: HTTP response
    """
    if request.is_ajax() and request.method == 'POST':
        print request.POST
        source_word_model = language_name_to_word_model(source_language)
        if 'translations' in request.POST:
            delete_translations(request.POST['word_to_translate'], source_word_model)
            add_translations(request.POST['word_to_translate'],
                             source_word_model,
                             json.loads(request.POST['translations']))
            return HttpResponse('{}', content_type='application/javascript')
        elif 'word_to_search' in request.POST:
            matching_words = source_word_model.objects.filter(word__startswith=request.POST['word_to_search']).values_list('word', flat=True)
            return HttpResponse(json.dumps({'matching_words': list(matching_words)}), content_type='application/javascript')
        elif 'word_to_translate' in request.POST:
            translations = get_translations_if_word_exists(request.POST['word_to_translate'], source_word_model)
            print 'tr'
            print translations
            return HttpResponse(json.dumps({'translations': translations}), content_type='application/javascript')
        else:
            return HttpResponse('Unrecognized AJAX request', content_type='application/javascript')
    template = loader.get_template('translations/word_translations_management.html')
    context = RequestContext(request, {'source_language': source_language})
    return HttpResponse(template.render(context))


def language_name_to_word_model(language_name):
    if language_name == "polish":
        return WordPL
    elif language_name == "chinese":
        return WordZH
    else:
        raise Exception("Unknown language: " + language_name)


def get_translations_if_word_exists(word_to_search, word_model):
    try:
        if word_model == WordZH:
            return list(WordZH.objects.get(word=word_to_search).wordpl_set.values('word'))
        elif word_model == WordPL:
            return list(WordPL.objects.get(word=word_to_search).wordzh_set.values('word', 'pinyin'))
        else:
            logger.error("Unknown word model: " + word_model)
            return list()
    except ObjectDoesNotExist:
        return list()


def delete_translations(word_to_translate, source_word_model):
    if source_word_model == WordPL:
        WordPL.objects.get(word=word_to_translate).wordzh_set.clear()
    else:
        WordZH.objects.get(word=word_to_translate).wordpl_set.clear()


def add_translations(word_to_translate, source_word_model, translations):
    if source_word_model == WordPL:
        word_to_translate = WordPL.objects.get_or_create(word=word_to_translate)[0]
        for translation in translations:
            new_word_zh = WordZH.objects.get_or_create(word=translation['word'], pinyin=translation['pinyin'])[0]
            WordTranslation.objects.get_or_create(word_zh=new_word_zh, word_pl=word_to_translate)
    else:
        word_to_translate = WordZH.objects.get_or_create(word=word_to_translate)[0]  # TODO: user should specify pinyin of source word?
        for translation in translations:
            new_word_zh = WordZH.objects.get_or_create(word=translation['word'])[0]
            WordTranslation.objects.get_or_create(word_zh=new_word_zh, word_pl=word_to_translate)