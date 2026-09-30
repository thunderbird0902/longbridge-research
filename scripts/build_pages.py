"""Validate local HTML links and assemble the GitHub Pages artifact. No dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import shutil
from zipfile import ZIP_DEFLATED, ZipFile
from embed_offline import embed_report

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


class ReportStructure(HTMLParser):
    """Catch broken containers before a browser silently rearranges the report."""
    VOID = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self):
        super().__init__()
        self.stack = []
        self.ids = set()
        self.anchors = []
        self.cases = set()
        self.case_links = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        ident = attrs.get("id")
        if ident:
            if ident in self.ids:
                self.errors.append(f"Duplicate id: {ident}")
            self.ids.add(ident)
        href = attrs.get("href", "")
        if href.startswith("#") and len(href) > 1:
            self.anchors.append(href[1:])
        if "data-case-detail" in attrs:
            self.cases.add(attrs["data-case-detail"])
        for key in ("data-case-id", "data-open-case", "data-lineage-case"):
            if key in attrs:
                self.case_links.append(attrs[key])
        if self.stack and self.stack[-1][0] == "main":
            if tag != "nav" and "report-content" not in attrs.get("class", "").split():
                self.errors.append(f"Content escaped the report column: {tag} {ident or ''}")
        if tag not in self.VOID:
            self.stack.append((tag, ident))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1][0] != tag:
            self.errors.append(f"Mismatched closing {tag} at line {self.getpos()[0]}")
        else:
            self.stack.pop()

    def validate(self):
        if self.stack:
            self.errors.append("Unclosed report containers")
        self.errors.extend(f"Missing anchor: {x}" for x in set(self.anchors) - self.ids)
        self.errors.extend(f"Missing case: {x}" for x in set(self.case_links) - self.cases)
        return self.errors


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
        text = source.read_text(encoding="utf-8")
        parser.feed(text)
        if source.name == "longbridge-research.html":
            if embed_report(text) != text:
                errors.append("Offline content is stale. Run: python3 scripts/embed_offline.py")
            structure = ReportStructure()
            structure.feed(text)
            errors.extend(structure.validate())
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
