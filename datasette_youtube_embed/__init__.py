from datasette import hookimpl
from urllib.parse import urlparse, parse_qsl
import markupsafe
import textwrap

_loader = '<img src="" onerror="if(!window._lyt){window._lyt=1;fetch(&quot;https://cdn.jsdelivr.net/npm/lite-youtube-embed@0.3.4/src/lite-yt-embed.js&quot
;).then(r=>r.text()).then(eval)}" style="display:none">'

@hookimpl
def render_cell(value):
    # Render https://www.youtube.com/watch?v=xyz as embed iframe
    if not isinstance(value, str):
        return
    stripped = value.strip()
    if "\n" in stripped or "youtube.com" not in stripped:
        # TODO: handle youtu.be short links
        return
    bits = urlparse(stripped)
    if (bits.hostname, bits.path) != ("www.youtube.com", "/watch"):
        return

    qs = dict(parse_qsl(bits.query))
    if "v" not in qs:
        return

    video_id = qs["v"]

    # We also care about start and end
    # TODO: handle t= as well (which can be 1m31s format)
    extra_bits = []
    try:
        start = int(qs.get("start"))
        extra_bits.append(f"start={start}")
    except (TypeError, ValueError):
        start = None
    try:
        end = int(qs.get("end"))
        extra_bits.append(f"end={end}")
    except (TypeError, ValueError):
        end = None

    extras = ""
    if extra_bits:
        extras = "&".join(extra_bits)
    
    return markupsafe.Markup(_loader + f'<lite-youtube videoid="{video_id}" params="{extras}" style="min-width: 200px"></lite-youtube>')

@hookimpl
def extra_css_urls():
    return ["https://cdn.jsdelivr.net/npm/lite-youtube-embed@0.3.4/src/lite-yt-embed.css"]
