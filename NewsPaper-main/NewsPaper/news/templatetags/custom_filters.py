from django import template

register = template.Library()


@register.filter(name='censor')
def censor(text):
    forbidden_vocabulary = ['nba', 'нба']

    for i in forbidden_vocabulary:
        text = text.replace(i, '<!запрещенная в РФ организация>')
        text = text.replace(i.upper(), '<!запрещенная в РФ организация>')

    return text
