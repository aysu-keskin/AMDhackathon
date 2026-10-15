"""Download OSHA Severe Injury Reports (SIR) into data/raw.

OSHA's file server rejects requests that lack a session cookie and referer,
so we visit the SIR page first and reuse its cookies for the zip.

Usage: python -m backend.pipeline.download
"""
import hashlib
import http.cookiejar
import urllib.request
import zipfile

from .paths import RAW_DIR, SIR_CSV, SIR_ZIP

PAGE_URL = "https://www.osha.gov/severe-injury-reports"
ZIP_URL = "https://www.osha.gov/sites/default/files/January2015toNovember2025.zip"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"


def download() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if SIR_CSV.exists():
        print(f"Already present: {SIR_CSV}")
        return

    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    opener.addheaders = [("User-Agent", USER_AGENT)]
    opener.open(PAGE_URL, timeout=60).read()

    request = urllib.request.Request(ZIP_URL, headers={"Referer": PAGE_URL})
    with opener.open(request, timeout=300) as response:
        SIR_ZIP.write_bytes(response.read())

    if not zipfile.is_zipfile(SIR_ZIP):
        SIR_ZIP.unlink()
        raise RuntimeError("OSHA returned something other than a zip (blocked or moved?).")

    with zipfile.ZipFile(SIR_ZIP) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if len(names) != 1:
            raise RuntimeError(f"Expected one CSV in the zip, found: {names}")
        SIR_CSV.write_bytes(archive.read(names[0]))

    digest = hashlib.sha256(SIR_ZIP.read_bytes()).hexdigest()
    print(f"Saved {SIR_CSV} ({SIR_CSV.stat().st_size / 1e6:.1f} MB), zip sha256={digest}")


if __name__ == "__main__":
    download()
