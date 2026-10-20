import re, os, sys
CDN = os.environ.get('IMG_CDN','https://cdn.jsdelivr.net/gh/Nalukai-Foundation/site-assets@main/img/')

src = open('page/past-programs.source.html', encoding='utf-8').read()

css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
js = re.search(r'<script>(.*?)</script>', src, re.S).group(1)
body_html = re.search(r'<main id="main" data-cols="3">(.*?)</main>', src, re.S).group(1)

# ---- scope CSS under .pp ----
def scope_selector(s):
    s = s.strip()
    if s.startswith('body::before'):
        return None
    if s in (':root', 'body'):
        return '.pp'
    if s == '*':
        return '.pp *'
    if s.startswith('main['):
        return '.pp' + s[4:]
    if s.startswith('main '):
        return '.pp ' + s[5:]
    return '.pp ' + s

def process(block):
    out, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j == -1:
            out.append(block[i:]); break
        head = block[i:j]
        # find matching brace
        depth, k = 1, j + 1
        while depth and k < len(block):
            if block[k] == '{': depth += 1
            elif block[k] == '}': depth -= 1
            k += 1
        inner = block[j+1:k-1]
        h = head.strip()
        if h.startswith('@media'):
            out.append(h + ' {\n' + process(inner) + '\n}')
        else:
            sels = [scope_selector(x) for x in h.split(',')]
            sels = [x for x in sels if x]
            if sels:
                out.append(', '.join(sels) + ' {' + inner + '}')
        i = k
    return '\n'.join(out)

# strip comments and rules for the stand-in header/footer
css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
scoped = process(css)
# drop stand-in chrome rules
keep = []
for rule in re.split(r'\n(?=[^\s}])', scoped):
    if re.search(r'\.site-(head|nav|foot)|\.wordmark|\.donate', rule.split('{')[0]):
        continue
    keep.append(rule)
scoped = '\n'.join(keep)
# toolbar sits at the top of its container inside Squarespace
scoped = scoped.replace('top: env(safe-area-inset-top, 0px)', 'top: 0')

# ---- html ----
body_html = body_html.replace('id="rows"', 'id="pp-rows"').replace('id="count"', 'id="pp-count"')
body_html = body_html.replace('id="seglabel"', 'id="pp-seglabel"').replace('aria-labelledby="seglabel"', 'aria-labelledby="pp-seglabel"')
body_html = body_html.replace('id="cols2"', 'id="pp-cols2"').replace('id="cols3"', 'id="pp-cols3"')

# ---- js ----
js = js.replace('getElementById("rows")', 'getElementById("pp-rows")')
js = js.replace('getElementById("count")', 'getElementById("pp-count")')
js = js.replace('getElementById("main")', 'getElementById("pp-main")')
js = js.replace('".seg button"', '"#pp-main .seg button"')
# embed images as data URIs
def embed(m):
    return '"' + CDN + m.group(1)[4:] + '"'
js = re.sub(r'"(img/[\w.-]+\.jpg)"', embed, js)

html = f'''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&family=Poppins:wght@700&display=swap">
<style>
{scoped}
</style>
<div class="pp" id="pp-main" data-cols="3">
{body_html}
</div>
<script>
{js}
</script>
'''
out = os.environ.get('OUT','./past-programs-squarespace.html')
open(out, 'w', encoding='utf-8').write(html)
open('/tmp/claude-0/ss.js', 'w', encoding='utf-8').write(js)
print(len(html) // 1024, 'KB')

# ---- ASCII-safe output (Squarespace code blocks may mis-decode UTF-8) ----
s = open(out, encoding='utf-8').read()
i = s.index('<script>') + 8; j = s.index('</script>')
def ent(t): return ''.join(c if ord(c) < 128 else '&#x%X;' % ord(c) for c in t)
def esc(t):
    r = []
    for c in t:
        o = ord(c)
        if o < 128: r.append(c)
        elif o < 0x10000: r.append('\\u%04X' % o)
        else:
            o -= 0x10000; r.append('\\u%04X\\u%04X' % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
    return ''.join(r)
s = ent(s[:i]) + esc(s[i:j]) + ent(s[j:])
open(out, 'w', encoding='ascii').write(s)
print('ascii ok')
