"""Repackage the frozen Russian HTML translation with the current form example.

Python 3.12+, Beautiful Soup. No PHP/MySQL server is required to build a docset.
The frozen input is a previously published, openly licensed translation, not a
download of Kapeli's restricted metadata. Its search database was authored here.
"""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit, parse_qs, quote, urljoin
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import argparse
import base64
import gzip
import hashlib
import html
import json
import os
import plistlib
import re
import shutil
import sqlite3
import tarfile
import zipfile
import zlib

HERE = Path(__file__).resolve().parent
VERSION = '2026.11.19.1'
NAME = 'HTML_(Русский)'
BASE_URL = ('https://raw.githubusercontent.com/Omogobicoyu/html-forms-docset/'
            '2737dd5140181b94a91b0b0efeac4054fbcf7f70/HTML_RU.tgz')
BASE_SHA256 = 'f65e347d644670712522e8cc4d99f5b8ca519d40eb19167d8fe2eb2ccb6bf952'
CODE_FILES = ['database.sql', 'db.php', 'header.php', 'footer.php', 'index.php',
              'register.php', 'phone.js', 'create.php', 'requests.php',
              'admin.php', 'logout.php', 'style.css']
HOME = 'developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements.html'
FORM = 'developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/form.html'


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(target):
    print('Downloading frozen Russian HTML snapshot (about 83 MiB)...', flush=True)
    request = Request(BASE_URL, headers={'User-Agent': 'HTML-Russian-docset-builder'})
    with urlopen(request, timeout=90) as response, target.open('wb') as stream:
        shutil.copyfileobj(response, stream)


def extract(archive, output):
    with tarfile.open(archive) as tar:
        for member in tar:
            relative = PurePosixPath(member.name)
            if (relative.is_absolute() or '..' in relative.parts
                    or '\\' in member.name or relative.parts[0] != NAME + '.docset'
                    or not (member.isdir() or member.isfile())):
                raise RuntimeError('Unsafe archive entry: ' + member.name)
            target = output.joinpath(*relative.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as source, target.open('wb') as dest:
                    shutil.copyfileobj(source, dest)


def code(text):
    # Preserve the complete source, including its final newline. Never execute PHP/JS.
    return '<pre><code>' + html.escape(text) + '</code></pre>'


def page(title, body):
    return ('<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + html.escape(title) + '</title>'
            '<link rel="stylesheet" href="style.css"></head><body><main>'
            '<nav><a href="form-server.html">Файлы примера</a>'
            '<a href="database-guide.html">БД через phpMyAdmin</a>'
            '<a href="exam.html">Порядок написания</a></nav><h1>'
            + html.escape(title) + '</h1>' + body + '</main></body></html>')


def inline(text):
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)


def markdown(text):
    parts, table, block = [], [], None
    def flush_table():
        if table:
            rows = [row for row in table if not re.fullmatch(r'[\s|:-]+', row)]
            parts.append('<div class="table-scroll"><table>' + ''.join(
                '<tr>' + ''.join('<td>' + inline(cell.strip()) + '</td>'
                for cell in row.strip().strip('|').split('|')) + '</tr>'
                for row in rows) + '</table></div>')
            table.clear()
    for line in text.splitlines():
        if line.startswith('```'):
            if block is not None:
                parts.append(code('\n'.join(block)))
                block = None
            else:
                flush_table()
                block = []
        elif block is not None:
            block.append(line)
        elif line.startswith('|'):
            table.append(line)
        else:
            flush_table()
            if line.startswith('#'):
                level = min(len(line) - len(line.lstrip('#')), 4)
                parts.append(f'<h{level}>' + inline(line.lstrip('# ').strip()) + f'</h{level}>')
            elif line.strip():
                parts.append('<p>' + inline(line) + '</p>')
    flush_table()
    return '\n'.join(parts)


def build_example(docs):
    folder = docs / '_examples/forms'
    manifest = json.loads((HERE / 'site-manifest.json').read_text(encoding='utf-8'))
    for relative, expected in {**manifest['current_site_files'], **manifest['supplemental_files']}.items():
        if sha256(HERE / 'site' / relative) != expected:
            raise RuntimeError('Site snapshot changed: ' + relative)
    (folder / 'source-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    body = ('<p>Полный учебный пример HTML-форм с PHP и MySQL: портал «Конференции.РФ».</p>'
            '<p>Снимок от 19.11.2026: подробные комментарии, вход и регистрация по центру, '
            'телефон по маске <code>8(XXX)XXX-XX-XX</code> без букв. '
            'PHP и JavaScript ниже показаны как текст и в справочнике не выполняются.</p>'
            '<p>Файлы PHP, CSS и JavaScript точно соответствуют текущему сайту. '
            '<code>database.sql</code> — дополнительная схема для новой пустой базы; '
            'создать её вручную можно по инструкции phpMyAdmin.</p>'
            '<p><a href="database-guide.html">Создание БД через интерфейс phpMyAdmin</a> · '
            '<a href="source.zip">Скачать все файлы сайта ZIP</a></p><ol>')
    for name in CODE_FILES:
        body += '<li><a href="#' + name.replace('.', '-') + '">' + name + '</a></li>'
    body += '</ol>'
    for name in CODE_FILES:
        body += ('<details id="' + name.replace('.', '-') + '"><summary>' + name
                 + '</summary>' + code((HERE / 'site' / name).read_text(encoding='utf-8')) + '</details>')
    body += ('<p><a href="exam.html">Порядок самостоятельного написания</a> · '
             '<a href="source-manifest.json">Контрольные суммы файлов</a></p>')
    (folder / 'form-server.html').write_text(page('Формы: серверная обработка', body), encoding='utf-8')
    (folder / 'database-guide.html').write_text(page('Создание базы через phpMyAdmin',
        markdown((HERE / 'phpmyadmin-guide.md').read_text(encoding='utf-8'))), encoding='utf-8')
    (folder / 'exam.html').write_text(page('Порядок написания сайта',
        markdown((HERE / 'writing-order.md').read_text(encoding='utf-8'))), encoding='utf-8')
    with (folder / 'style.css').open('a', encoding='utf-8') as stream:
        stream.write('\nmain{box-sizing:border-box;min-width:0}pre{max-width:100%;box-sizing:border-box}'
                     '.table-scroll{overflow-x:auto}p,li,td,th{overflow-wrap:anywhere}\n')
    with zipfile.ZipFile(folder / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for source in sorted((HERE / 'site').rglob('*')):
            if source.is_file():
                info = zipfile.ZipInfo('conf/' + source.relative_to(HERE / 'site').as_posix(),
                                       date_time=(2026, 11, 19, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, source.read_bytes())
        for name in ['LICENSE-MIT.txt', 'BOOTSTRAP-LICENSE.txt']:
            archive.writestr('conf/' + name, (HERE / name).read_bytes())
    # Verify the displayed code and downloadable source against the input snapshot.
    soup = BeautifulSoup((folder / 'form-server.html').read_text(encoding='utf-8'), 'html.parser')
    blocks = soup.select('details pre code')
    assert len(blocks) == len(CODE_FILES)
    for name, block in zip(CODE_FILES, blocks):
        assert block.get_text() == (HERE / 'site' / name).read_text(encoding='utf-8'), name
    assert not soup.select('details[open]')
    with zipfile.ZipFile(folder / 'source.zip') as archive:
        assert archive.testzip() is None
        for source in (HERE / 'site').rglob('*'):
            if source.is_file():
                assert archive.read('conf/' + source.relative_to(HERE / 'site').as_posix()) == source.read_bytes()
    return manifest


def localize_examples(docs):
    """Rebuild remote mdnplay frames from the source already encoded in their URLs.

    No translation or network fetch is performed. External videos become ordinary
    labelled links; root-relative assets are pointed to existing mirrored files.
    """
    generated = []
    video_links = 0
    sample_dir = docs / '_offline_samples'
    sample_dir.mkdir(exist_ok=True)
    for path in list(docs.rglob('*.html')):
        text = path.read_text(encoding='utf-8', errors='strict')
        if not re.search(r'<iframe\b[^>]*\bsrc=["\']https?://', text):
            continue
        def frame(match):
            nonlocal video_links
            tag, target = match.group(0), html.unescape(match.group(2))
            url = urlsplit(target)
            if url.scheme not in ['http', 'https']:
                return tag
            if (url.hostname or '').endswith('.mdnplay.dev'):
                state = parse_qs(url.query).get('state', [None])[0]
                if not state:
                    raise RuntimeError('Remote MDN sample has no recorded source: ' + target)
                raw = base64.b64decode(state.replace(' ', '+') + '=' * (-len(state) % 4))
                data = json.loads(zlib.decompress(raw, -15))
                assert all(isinstance(data.get(key, ''), str) for key in ['html', 'css', 'js'])
                filename = hashlib.sha256(target.encode()).hexdigest()[:24] + '.html'
                css = data.get('css', '').replace('</style', '<\\/style')
                js = data.get('js', '').replace('</script', '<\\/script')
                content = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
                           '<meta name="viewport" content="width=device-width,initial-scale=1">'
                           '<title>Локальный пример MDN</title><style>' + css + '</style></head><body>'
                           + data.get('html', '') + '<script>' + js + '</script></body></html>')
                (sample_dir / filename).write_text(content, encoding='utf-8')
                relative = os.path.relpath(sample_dir / filename, path.parent).replace('\\', '/')
                generated.append({'page': path.relative_to(docs).as_posix(), 'source': target,
                                  'local': '_offline_samples/' + filename})
                return tag.replace(match.group(2), html.escape(relative, quote=True), 1)
            video_links += 1
            return ('<p class="ru-docset-notice">Внешнее видео или демонстрация (нужен интернет): '
                    '<a href="' + html.escape(target, quote=True) + '">Открыть источник</a></p>')
        text = re.sub(r'<iframe\b[^>]*\bsrc=(["\'])([^"\']+)\1[^>]*>.*?</iframe>',
                      frame, text, flags=re.S)
        path.write_text(text, encoding='utf-8')
    # Rewrite actual resource attributes and CSS URLs, leaving escaped source code alone.
    for path in list(docs.rglob('*.html')) + list(docs.rglob('*.css')):
        text = path.read_text(encoding='utf-8')
        def local_url(value):
            url = urlsplit(html.unescape(value))
            if url.scheme in ['data', 'javascript', 'mailto'] or not url.path:
                return value
            candidate = None
            if url.netloc:
                candidate = docs / url.netloc / unquote(url.path.lstrip('/'))
            elif url.path.startswith('/'):
                candidate = docs / 'developer.mozilla.org' / unquote(url.path.lstrip('/'))
            if candidate is not None and candidate.is_file():
                relative = os.path.relpath(candidate, path.parent).replace('\\', '/')
                return quote(relative, safe='/.-_') + ('#' + url.fragment if url.fragment else '')
            return value
        if path.suffix == '.css':
            def css_url(match):
                value = match.group(2)
                fixed = local_url(value)
                # HTTrack encoded an SVG fragment into a duplicated runner filename.
                if fixed == value and 'runner.html-' in value and '%23' in value:
                    fragment = value.rsplit('%23', 1)[1]
                    runners = list(path.parent.rglob('runner.html-*'))
                    if len(runners) == 1:
                        relative = os.path.relpath(runners[0], path.parent).replace('\\', '/')
                        fixed = quote(relative, safe='/.-_') + '#' + fragment
                return 'url(' + match.group(1) + fixed + match.group(1) + ')'
            text = re.sub(r'url\(\s*(["\']?)([^)\'"\s]+)\1\s*\)', css_url, text)
        else:
            def attribute(match):
                return match.group(1) + local_url(match.group(3)) + match.group(2)
            text = re.sub(r'(<(?:img|source|script|iframe|video|audio|link)\b[^>]*?\b(?:src|href|poster)=(["\']))([^"\']+)\2',
                          attribute, text, flags=re.I)
        path.write_text(text, encoding='utf-8')
    (docs / 'offline-examples.json').write_text(json.dumps(generated, ensure_ascii=False, indent=2), encoding='utf-8')
    return len(generated), video_links


def finish_offline_resources(docs):
    """Keep optional online media as labelled links; avoid missing webfont requests."""
    omitted_fonts = 0
    optional_media = 0
    reference_file = docs / 'offline-reference-links.json'
    references = json.loads(reference_file.read_text(encoding='utf-8')) if reference_file.exists() else []
    additional = HERE / 'offline-assets'
    target_assets = docs / '_offline_assets'
    target_assets.mkdir(exist_ok=True)
    sources = json.loads((additional / 'sources.json').read_text(encoding='utf-8'))
    for entry in sources:
        if 'error' in entry:
            raise RuntimeError('Unresolved offline asset: ' + entry['file'])
        assert sha256(additional / entry['file']) == entry['sha256']
        shutil.copy2(additional / entry['file'], target_assets / entry['file'])
    shutil.copy2(additional / 'sources.json', target_assets / 'sources.json')
    files = {}
    for resource in docs.rglob('*'):
        if resource.is_file():
            files.setdefault(resource.name, []).append(resource)
    def exists(path, value):
        url = urlsplit(html.unescape(value))
        if url.scheme or url.netloc or not url.path:
            return True
        return (path.parent / unquote(url.path)).is_file()
    for path in docs.rglob('*.css'):
        text = path.read_text(encoding='utf-8')
        def font_face(match):
            nonlocal omitted_fonts
            urls = re.findall(r'url\(["\']?([^\)\'"\s]+)', match.group(0))
            if any(not exists(path, value) for value in urls):
                omitted_fonts += 1
                return ''
            return match.group(0)
        text = re.sub(r'@font-face\s*\{[^{}]*\}', font_face, text)
        def css_asset(match):
            return match.group(0) if exists(path, match.group(2)) else 'none'
        text = re.sub(r'url\(\s*(["\']?)([^)\'"\s]+)\1\s*\)', css_asset, text)
        path.write_text(text, encoding='utf-8')
    for path in docs.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        def media(match):
            nonlocal optional_media
            block = match.group(0)
            targets = re.findall(r'(?<![-\w])(?:src|poster)=["\'](https?://[^"\']+)', block)
            if not targets:
                return block
            optional_media += 1
            block = re.sub(r'(?<![-\w])(src|poster)=(["\'])(https?://[^"\']+)\2', r'data-online-\1=\2\3\2', block)
            return (block + '<p>Медиафайл доступен онлайн: <a href="' + targets[0]
                    + '">Открыть источник</a>. Текст и код примера доступны без интернета.</p>')
        text = re.sub(r'<(?:video|audio)\b[^>]*>.*?</(?:video|audio)>', media, text, flags=re.S)
        def optional_frame(match):
            nonlocal optional_media
            optional_media += 1
            return '<p>Демонстрация внешнего сайта: <a href="' + match.group(2) + '">Открыть онлайн</a></p>'
        text = re.sub(r'<iframe\b[^>]*\bsrc=(["\'])(https?://[^"\']+)\1[^>]*>.*?</iframe>', optional_frame, text, flags=re.S)
        def image(match):
            value = html.unescape(match.group(3))
            if exists(path, value):
                return match.group(0)
            candidates = files.get(Path(urlsplit(value).path).name, [])
            if candidates:
                relative = quote(os.path.relpath(candidates[0], path.parent).replace('\\', '/'), safe='/.-_')
                return match.group(1) + relative + match.group(2)
            return match.group(0)
        text = re.sub(r'(<img\b[^>]*?\bsrc=(["\']))([^"\']+)\2', image, text)
        def srcset(match):
            parts = []
            for item in html.unescape(match.group(3)).split(','):
                fields = item.strip().split()
                if fields and not exists(path, fields[0]):
                    candidates = files.get(Path(urlsplit(fields[0]).path).name, [])
                    if candidates:
                        fields[0] = quote(os.path.relpath(candidates[0], path.parent).replace('\\', '/'), safe='/.-_')
                parts.append(' '.join(fields))
            return match.group(1) + html.escape(', '.join(parts), quote=True) + match.group(2)
        text = re.sub(r'(<(?:img|source)\b[^>]*?\bsrcset=(["\']))([^"\']+)\2', srcset, text)
        def stylesheet(match):
            tag = match.group(0)
            href = re.search(r'\bhref=(["\'])([^"\']+)\1', tag)
            if href and re.search(r'\brel=["\']stylesheet["\']', tag) and not exists(path, href.group(2)):
                return ''
            return tag
        text = re.sub(r'<link\b[^>]*>', stylesheet, text)
        def reference(match):
            value = html.unescape(match.group(3))
            if exists(path, value) or value.startswith('#'):
                return match.group(0)
            parts = path.relative_to(docs).parts
            hosts = [i for i, part in enumerate(parts[:-1]) if part.endswith(('.org', '.com', '.dev', '.io', '.net'))]
            if not hosts:
                return match.group(0)
            index = hosts[-1]
            source = 'https://' + parts[index] + '/' + '/'.join(parts[index + 1:])
            target = urljoin(source, value)
            references.append({'page': path.relative_to(docs).as_posix(), 'original': value, 'online': target})
            return match.group(1) + html.escape(target, quote=True) + match.group(2)
        # References outside the frozen mirror are ordinary online links, not broken local paths.
        text = re.sub(r'(<a\b[^>]*?\bhref=(["\']))([^"\']+)\2', reference, text)
        path.write_text(text, encoding='utf-8')
    reference_file.write_text(json.dumps(references, ensure_ascii=False, indent=2), encoding='utf-8')
    return omitted_fonts, optional_media


def make_archive(bundle, archive):
    def stable(member):
        member.uid = member.gid = member.mtime = 0
        member.uname = member.gname = ''
        member.mode = 0o755 if member.isdir() else 0o644
        return member
    with archive.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=9) as compressed:
        with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as tar:
            tar.add(bundle, arcname=bundle.name, filter=stable)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-archive', type=Path, help='Use a previously downloaded frozen snapshot (offline build).')
    parser.add_argument('--output', type=Path, default=HERE.parent / 'dist')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    bundle = out / (NAME + '.docset')
    if bundle.exists():
        raise RuntimeError('Choose an output directory without an existing docset: ' + str(out))
    base = args.base_archive
    if base is None:
        cache = HERE / '.cache'
        cache.mkdir(exist_ok=True)
        base = cache / 'HTML_RU-2026.11.17.2.tgz'
        if not base.exists():
            download(base)
    if sha256(base) != BASE_SHA256:
        raise RuntimeError('Frozen input SHA-256 mismatch')
    print('Extracting verified frozen snapshot...', flush=True)
    extract(base, out)
    docs = bundle / 'Contents/Resources/Documents'
    manifest = build_example(docs)
    dbpath = bundle / 'Contents/Resources/docSet.dsidx'
    connection = sqlite3.connect(dbpath)
    original_rows = connection.execute('SELECT name,type,path FROM searchIndex').fetchall()
    connection.close()
    anchors = {}
    pages = 0
    preserved = 0
    original_code = {}
    overrides = HERE / 'docset-overrides.css'
    shutil.copy2(overrides, docs / 'docset-overrides.css')
    for path in sorted((docs / 'developer.mozilla.org/en-US').rglob('*.html')):
        text = path.read_text(encoding='utf-8')
        if 'ru-docset-notice' not in text:
            continue
        soup = BeautifulSoup(text, 'html.parser')
        assert soup.html.get('lang') == 'ru', path
        anchors[path.relative_to(docs).as_posix()] = {
            value for tag in soup.find_all(True) for value in [tag.get('id'), tag.get('name')] if value
        }
        preserved += len(soup.select('pre,textarea'))
        if path.relative_to(docs).as_posix() == FORM:
            link = os.path.relpath(docs / '_examples/forms/form-server.html', path.parent).replace('\\', '/')
            detail = ('<details id="server-example"><summary>Практический пример: формы и серверный обработчик'
                      '</summary><p><a href="' + link + '">Открыть полный пример с файлами</a></p></details>')
            text, changed = re.subn(r'<details id="server-example".*?</details>', lambda _: detail, text, count=1, flags=re.S)
            assert changed == 1
        css = os.path.relpath(docs / 'docset-overrides.css', path.parent).replace('\\', '/')
        text = text.replace('</head>', '<link rel="stylesheet" href="' + css + '"/></head>', 1)
        if not re.match(r'\s*<!doctype', text, re.I):
            text = '<!DOCTYPE html>\n' + text
        # Only add an isolated stylesheet / example link: MDN's code remains byte-for-byte.
        before = re.findall(r'<(?:pre|textarea)\b[^>]*>.*?</(?:pre|textarea)>', path.read_text(encoding='utf-8'), re.S)
        original_code[path] = before
        after = re.findall(r'<(?:pre|textarea)\b[^>]*>.*?</(?:pre|textarea)>', text, re.S)
        assert before == after, 'MDN code modified: ' + str(path)
        path.write_text(text, encoding='utf-8')
        pages += 1
        if pages % 250 == 0:
            print('Checked translated pages:', pages, flush=True)
    offline_samples, external_video_links = localize_examples(docs)
    omitted_webfonts, optional_media = finish_offline_resources(docs)
    for path, before in original_code.items():
        after = re.findall(r'<(?:pre|textarea)\b[^>]*>.*?</(?:pre|textarea)>', path.read_text(encoding='utf-8'), re.S)
        assert before == after, 'MDN code modified while localizing resources: ' + str(path)
    # Recreate our own index, normalizing labels and validating every local target.
    connection = sqlite3.connect(dbpath)
    connection.executescript('DROP TABLE searchIndex; CREATE TABLE searchIndex(id INTEGER PRIMARY KEY,name TEXT,type TEXT,path TEXT);'
                             'CREATE UNIQUE INDEX anchor ON searchIndex(name,type,path);')
    repaired_fragments = 0
    for name, kind, target in original_rows:
        name = ' '.join(name.split())
        assert name and kind and target
        relative, separator, fragment = target.partition('#')
        assert (docs / relative).is_file(), target
        if separator and unquote(fragment) not in anchors.get(relative, set()):
            target = relative
            repaired_fragments += 1
        connection.execute('INSERT OR IGNORE INTO searchIndex(name,type,path) VALUES(?,?,?)', (name, kind, target))
    connection.commit()
    assert connection.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    count = connection.execute('SELECT COUNT(*) FROM searchIndex').fetchone()[0]
    connection.close()
    info = {'CFBundleIdentifier': 'local.HTML_RU', 'CFBundleName': 'HTML (Русский)',
            'DocSetPlatformFamily': 'htmlru', 'DashDocSetFamily': 'dashtoc',
            'isDashDocset': True, 'DashDocSetKeyword': 'htmlru', 'dashIndexFilePath': HOME,
            'isJavaScriptEnabled': True}
    (bundle / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
    (bundle / 'meta.json').write_text(json.dumps({'name': NAME, 'title': 'HTML (Русский)', 'version': VERSION}, ensure_ascii=False, indent=2), encoding='utf-8')
    for name in ['LICENSE-MIT.txt', 'BOOTSTRAP-LICENSE.txt']:
        shutil.copy2(HERE / name, bundle / name)
    with (bundle / 'LICENSES.txt').open('a', encoding='utf-8') as stream:
        stream.write('\nUpdate 2026-11-19: current PHP/MySQL teaching example, phone mask, Russian comments.\n'
                     'Build scripts and original example code: MIT (LICENSE-MIT.txt).\n'
                     'Bootstrap 5.3.3: MIT (BOOTSTRAP-LICENSE.txt). PT Sans: SIL OFL in source.zip.\n')
    license_path = bundle / 'LICENSES.txt'
    license_text = license_path.read_text(encoding='utf-8').replace(
        'Оригинальные клиентские ресурсы внутри Documents сохранены без изменений.',
        'Некоторые URL клиентских ресурсов исправлены для офлайн-работы; недоступные веб-шрифты используют системные замены. Изменённые клиентские CSS остаются под MPL-2.0.')
    license_text += ('\nAdditional MDN images: sources and SHA-256 in Documents/_offline_assets/sources.json.\n'
                     'Mozilla Contributors; MDN content licensing: CC BY-SA 2.5 / applicable MDN example licenses.\n'
                     'https://github.com/mdn/shared-assets/blob/main/LICENSE.md\n'
                     'Some optional audio/video is linked online rather than loaded automatically.\n')
    license_path.write_text(license_text, encoding='utf-8')
    archive = out / 'HTML_RU.tgz'
    print('Compressing docset...', flush=True)
    make_archive(bundle, archive)
    report = {'name': 'HTML (Русский)', 'version': VERSION, 'original_docset': 'HTML revision 157',
              'mdn_articles': pages, 'human_translated_intros': 233, 'machine_translation': True,
              'preserved_code_blocks': preserved, 'search_entries': count,
              'repaired_index_fragments': repaired_fragments,
              'offline_mdn_samples_restored': offline_samples, 'external_media_links': external_video_links,
              'optional_media_links': optional_media, 'unavailable_webfonts_removed': omitted_webfonts,
              'additional_offline_images': len(json.loads((HERE / 'offline-assets/sources.json').read_text(encoding='utf-8'))),
              'external_reference_links': len(json.loads((docs / 'offline-reference-links.json').read_text(encoding='utf-8'))),
              'demo_source_files_verified': len(CODE_FILES), 'current_site_files_verified': len(manifest['current_site_files']),
              'collapsed_example': True, 'archive_bytes': archive.stat().st_size,
              'sha256': sha256(archive), 'native_dash_import_verified': False,
              'base_snapshot_sha256': BASE_SHA256}
    (out / 'HTML_RU-build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (out / 'SHA256SUMS').write_text(report['sha256'] + '  HTML_RU.tgz\n', encoding='ascii')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
