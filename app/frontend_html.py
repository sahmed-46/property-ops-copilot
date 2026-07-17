from __future__ import annotations

import re
from pathlib import Path

from fastapi.responses import HTMLResponse


def build_index_html(index_file: Path) -> str:
    html = index_file.read_text(encoding="utf-8")
    match = re.search(r'<script type="module"[^>]*src="([^"]+)"[^>]*></script>', html)
    if not match:
        return html

    js_path = match.group(1)
    loader = f"""
<div id="boot-status" style="font-family:sans-serif;padding:24px;text-align:center;color:#4b647a">
  Waking Property Ops Copilot (free-tier cold start can take up to 60s)...
</div>
<script type="module">
(async () => {{
  const status = document.getElementById("boot-status");
  for (let i = 0; i < 18; i++) {{
    try {{
      const response = await fetch("/ready", {{ cache: "no-store" }});
      if (response.ok) {{
        if (status) status.remove();
        await import("{js_path}");
        return;
      }}
    }} catch (error) {{
      console.warn("API preflight failed", error);
    }}
    if (status) {{
      status.textContent = `Waking Property Ops Copilot... attempt ${{i + 1}}/18`;
    }}
    await new Promise((resolve) => setTimeout(resolve, 4000));
  }}
  if (status) {{
    status.textContent = "API still offline. Refresh the page or try again in a minute.";
  }}
}})();
</script>
"""
    html = re.sub(r'<script type="module"[^>]*src="[^"]+"[^>]*></script>', "", html)
    return html.replace("<div id=\"root\"></div>", f"<div id=\"root\"></div>{loader}")


def index_response(index_file: Path) -> HTMLResponse:
    return HTMLResponse(build_index_html(index_file))
