from django import template

register = template.Library()


@register.simple_tag
def instagram():
    return 'https://instagram.com/igormundstock/'


@register.simple_tag
def twitter():
    return 'https://twitter.com/igor_mundstock'


@register.simple_tag
def youtube():
    return 'https://www.youtube.com/user/IgorMundstock'


@register.simple_tag
def linkedin():
    return 'https://www.linkedin.com/in/igormundstock/'


@register.simple_tag
def telegram():
    return 'https://t.me/igormundstock/'