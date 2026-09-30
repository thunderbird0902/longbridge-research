"""Validate local HTML links and assemble the GitHub Pages artifact. No dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
FILES = (
    "index.html", "longbridge-research.html", "longform-library.html",
    "focused-delivery-manifest.json", "local-library-manifest.json", ".nojekyll",
    "README-离线使用.txt",
)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        self.urls.extend(value for key, value in attrs
                         if key in ("href", "src", "action") and value)


def main():
    sources = [ROOT / name for name in FILES]
    sources.extend(sorted((ROOT / "library").glob("*.html")))
    if not (ROOT / "library").is_dir() or not any(
            file.parent.name == "library" for file in sources):
        raise SystemExit("Missing or empty library directory")
    archive_name = "longbridge-research-offline.zip"
    allowed = set(sources) | {ROOT / archive_name}
    errors = []
    count = 0
    for source in sources:
        if not source.is_file() or source.is_symlink():
            errors.append(f"Missing file or unsupported symlink: {source}")
            continue
        if source.suffix != ".html":
            continue
        parser = Links()
        parser.feed(source.read_text(encoding="utf-8"))
        for url in parser.urls:
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            count += 1
            target = (source.parent / unquote(parsed.path)).resolve()
            if parsed.path.startswith("/") or target not in allowed:
                errors.append(f"{source.relative_to(ROOT)}: invalid local link {url}")
    if errors:
        raise SystemExit("\n".join(errors))
    if OUTPUT.is_symlink():
        raise SystemExit("Refusing to replace symlink _site")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    for source in sources:
        destination = OUTPUT / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    with ZipFile(OUTPUT / archive_name, "w", ZIP_DEFLATED) as archive:
        for source in sources:
            archive.write(source, source.relative_to(ROOT))
    print(f"Prepared {len(sources)} files; verified {count} local links in _site")


if __name__ == "__main__":
    main()
