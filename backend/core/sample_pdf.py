"""Write the sample incident-report PDFs that the UI can send to the Evolus document extractor.

The reports are written by the team (synthetic, not OSHA records): one in English and one in Italian, the
Italian one showing that the extractor returns an English narrative the classifier can read. Plain PDF 1.4 with
the standard Helvetica fonts, so no PDF library is needed.

Usage: python -m backend.core.sample_pdf   # writes frontend/public/samples/*.pdf
"""
import textwrap

from backend.pipeline.paths import ROOT

OUT = ROOT / "frontend" / "public" / "samples"

SAMPLES = {
    "incident-report-en.pdf": {
        "title": "Incident Report Form",
        "note": "Sample written by the DarkSea28 team for the demo - not an OSHA record",
        "fields": [
            ("Company", "Example Metal Parts Ltd. (fictional)"),
            ("Site / department", "Stamping shop, press line 3"),
            ("Date and time of incident", "14 September 2026, 10:40"),
            ("Employee", "[withheld]        Job title: press setup technician"),
            ("What was the employee doing just before the incident?",
             "Changing the die on a 150-ton mechanical power press and adjusting the stock feed."),
            ("What happened?",
             "The technician switched off the light curtain with the key switch to reach the feed rollers while "
             "the press was still in single-stroke mode. He pressed the foot pedal by mistake and the ram came "
             "down on his left hand. The tips of his index and middle fingers were partially amputated."),
            ("What was the injury?", "Partial amputation of two fingertips"),
            ("Part of body affected", "Left hand, index and middle fingers"),
            ("Object or substance that harmed the employee", "Mechanical power press, ram and die"),
            ("Treatment", "Taken to the emergency room and admitted to hospital overnight"),
            ("Reported by", "[withheld], EHS coordinator"),
        ],
    },
    "incident-report-it.pdf": {
        "title": "Modulo di segnalazione infortunio",
        "note": "Esempio scritto dal team DarkSea28 per la demo - non è un record OSHA",
        "fields": [
            ("Azienda", "Logistica Esempio S.r.l. (fittizia)"),
            ("Reparto", "Magazzino spedizioni, corsia 4"),
            ("Data e ora dell'infortunio", "2 ottobre 2026, 07:15"),
            ("Lavoratore", "[omesso]        Mansione: addetto al magazzino"),
            ("Che cosa stava facendo il lavoratore?",
             "Camminava lungo la corsia per prelevare un pallet da spedire."),
            ("Descrizione dell'accaduto",
             "Un collega alla guida di un carrello elevatore ha fatto retromarcia con un carico alto, senza "
             "segnalatore a terra, e ha investito il lavoratore che attraversava la corsia. Il lavoratore è "
             "caduto e il carrello gli è passato sulla gamba sinistra."),
            ("Tipo di lesione", "Frattura della tibia"),
            ("Parte del corpo", "Gamba sinistra"),
            ("Agente materiale", "Carrello elevatore a forche"),
            ("Primo soccorso / cure", "Trasportato in pronto soccorso e ricoverato"),
            ("Compilato da", "[omesso], RSPP"),
        ],
    },
}


def escape(text: str) -> bytes:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("cp1252")


def page_stream(sample: dict) -> bytes:
    ops, y = [], 790

    def text(font: str, size: int, value: str, x: int = 56) -> None:
        nonlocal y
        ops.append(b"BT /" + font.encode() + b" %d Tf %d %d Td (" % (size, x, y) + escape(value) + b") Tj ET")

    text("F2", 18, sample["title"]); y -= 20
    text("F1", 9, sample["note"]); y -= 12
    ops.append(b"0.5 w 56 %d m 539 %d l S" % (y, y)); y -= 24
    for label, value in sample["fields"]:
        text("F2", 10, label); y -= 15
        for line in textwrap.wrap(value, 88):
            text("F1", 11, line, 66); y -= 15
        y -= 5
        ops.append(b"0.85 G 0.4 w 56 %d m 539 %d l S 0 G" % (y + 2, y + 2)); y -= 14
    return b"\n".join(ops)


def build_pdf(sample: dict) -> bytes:
    content = page_stream(sample)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
    ]
    out, offsets = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"), []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return bytes(out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, sample in SAMPLES.items():
        (OUT / name).write_bytes(build_pdf(sample))
        print(f"  {name}: {(OUT / name).stat().st_size} bytes")


if __name__ == "__main__":
    main()
