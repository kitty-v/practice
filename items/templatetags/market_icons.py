from django import template

register = template.Library()

# Maps keywords found in a category's name to one of the <symbol id="icon-cat-*">
# entries defined in templates/_icons.html. Falls back to a generic tag icon so
# any admin-created category (not just the seeded ones) still gets a sensible,
# minimal line icon instead of a free-form emoji.
_KEYWORDS = [
    (('电子', '数码', '手机', '电脑'), 'electronics'),
    (('服装', '鞋', '包', '衣'), 'clothing'),
    (('家居', '家具', '生活'), 'home'),
    (('图书', '文具', '书'), 'books'),
    (('运动', '户外', '健身'), 'sports'),
    (('美妆', '个护', '化妆'), 'beauty'),
    (('母婴', '婴', '儿童'), 'baby'),
    (('乐器', '音乐'), 'music'),
]


@register.filter
def cat_icon(name):
    name = name or ''
    for keywords, icon_id in _KEYWORDS:
        if any(k in name for k in keywords):
            return icon_id
    return 'other'
