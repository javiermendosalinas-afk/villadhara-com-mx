"""Junta fotos de Villa Dhara desde la ficha de EasyBroker, villadhara.com.mx (GoDaddy) y villadhara.com (desarrollador), y arma hojas de contacto."""
import io, json, os, re, urllib.request
from PIL import Image, ImageDraw, ImageOps
UA = {"User-Agent": "Mozilla/5.0 (Acierta Max; sitio de comercializacion autorizada)"}
def get(u, binario=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
    return r if binario else r.decode("utf-8", "ignore")
fuentes = {
 "easybroker": ["https://www.easybroker.com/listings/el-departamento-mas-exclusivo-de-villa-dhara-terraza-privada-74-m-amueblado"],
 "sitio": ["https://villadhara.com.mx/"],
 "desarrollador": ["https://www.villadhara.com/", "https://www.villadhara.com/amenidades", "https://www.villadhara.com/departamentos", "https://www.villadhara.com/ubicacion", "https://www.villadhara.com/nosotros", "https://www.villadhara.com/por-que-invertir"],
}
patrones = {"easybroker": r"https://assets\.easybroker\.com/property_images/6057913/\d+/EB-WG7913\.png",
            "sitio": r"https://img1\.wsimg\.com/isteam/ip/[^\"'\s)]+?\.(?:jpe?g|png|webp)",
            "desarrollador": r"https://images\.squarespace-cdn\.com/content/v1/[^\"'\s)?]+?\.(?:jpe?g|png|webp)"}
os.makedirs("material/fotos", exist_ok=True); os.makedirs("material/hojas", exist_ok=True)
indice, vistos, n = [], set(), 0
for fuente, paginas in fuentes.items():
    urls = []
    for p in paginas:
        try:
            html = get(p).replace("&amp;", "&")
            for u in re.findall(patrones[fuente], html):
                if u not in urls: urls.append(u)
        except Exception as e:
            print("página no disponible:", p, type(e).__name__)
    for u in urls:
        try:
            ub = u + ("?format=1500w" if "squarespace" in u else "")
            datos = get(ub, True)
            im = ImageOps.exif_transpose(Image.open(io.BytesIO(datos))).convert("RGB")
            if im.width * im.height < 250_000: continue
            firma = im.resize((8, 8)).convert("L").tobytes()
            if firma in vistos: continue
            vistos.add(firma); n += 1
            im.thumbnail((1800, 1800)); ruta = f"material/fotos/{fuente[:3]}-{n:03d}.jpg"
            im.save(ruta, "JPEG", quality=80, optimize=True, progressive=True)
            indice.append({"n": n, "fuente": fuente, "archivo": ruta, "url": u, "ancho": im.width, "alto": im.height})
        except Exception as e:
            print("no se pudo:", u[:90], type(e).__name__)
json.dump(indice, open("material/indice.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for h in range(0, len(indice), 20):
    hoja = Image.new("RGB", (5 * 260, 4 * 200), (235, 235, 235)); dr = ImageDraw.Draw(hoja)
    for i, x in enumerate(indice[h:h + 20]):
        im = Image.open(x["archivo"]); im.thumbnail((250, 175)); px, py = (i % 5) * 260 + 5, (i // 5) * 200 + 5
        hoja.paste(im, (px, py)); dr.rectangle([px, py, px + 70, py + 22], fill=(30, 60, 50)); dr.text((px + 5, py + 5), f"{x['fuente'][:3].upper()} {x['n']}", fill=(255, 255, 255))
    hoja.save(f"material/hojas/hoja-{h // 20 + 1}.jpg", quality=72)
print(len(indice), "fotos:", {f: sum(1 for x in indice if x["fuente"] == f) for f in fuentes})
