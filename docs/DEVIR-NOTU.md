# DarkSea28 · Devir Notu

**Tarih:** 16 Ekim 2026, Cuma akşamı
**Yazan:** Aysu ve Claude (Aysu'nun bilgisayarındaki oturum)
**Kimin için:** Çağrı ve İlhan. Kalan işler sizin bilgisayarlarınızdan yapılacak.

Bu not, 16 Ekim'de yapılan her şeyi ve kalan işleri adım adım anlatıyor. Önce baştan sona bir kez okuyun, sonra
**6. Kalan işler** bölümünden sırayla ilerleyin. Takıldığınız yerde önce **11. Sık karşılaşılan sorunlar**
bölümüne bakın.

---

## 0. Bir bakışta

| | Durum |
|---|---|
| Canlı arayüz (teslimdeki "Demo Application URL") | ✅ https://am-dhackathon.vercel.app |
| Canlı API | ✅ https://amdhackathon-production.up.railway.app (sunucu uyuyor, ilk istekte uyanması 45 saniyeyi bulabilir) |
| Evolus çalışma alanı **DarkSea28** | ✅ Açık, üçümüz de üyeyiz |
| Evolus'ta AMD Token Factory model bağlantısı | ✅ 13 Ekim'de kuruldu |
| Evolus bilgi kütüphanesi **OSHA 29 CFR 1910 (selected)** | ✅ Oluşturuldu, ❌ **içi boş** (36 dosya yüklenecek, İş 1) |
| Evolus ajanı **Corrective Action Drafter** | ✅ Oluşturuldu, talimatı girildi, kütüphaneye bağlandı |
| Evolus API anahtarı | ❌ **Oluşturulacak** (İş 2) |
| Backend'de Evolus bağlantısı | ✅ Kod hazır ve push edildi, ❌ gerçek Evolus'la henüz denenmedi (anahtar yok, İş 3) |
| Railway'de Evolus değişkenleri | ❌ Eklenecek (İş 4) |
| Arayüzde "taslağı Evolus ajanı yazdı" bilgisi | ❌ Yapılacak (İş 5) |
| README'nin son hali, demo videosu, sunum, teslim formu | ❌ Yapılacak (İş 6–9) |

**Önemli:** Evolus ayarlanmadıkça canlı sistem eskisi gibi çalışır, taslağı doğrudan Token Factory yazar. Bu push
canlı sistemde hiçbir şeyi değiştirmiyor. Bu, 16 Ekim'de iki ayrı canlı analizle denendi (bkz. 5.6).

---

## 1. Son teslim ve iş sırası

- Başta teslim tarihini **18 Ekim Pazar 18:00 (TR)** varsaymıştık. Ama lablab'in /live sayfası geliştirme süresinin
  **17 Ekim Cumartesi** bittiğini yazıyor. **Kesinleşene kadar 17 Ekim Cumartesi'yi son gün sayın.**
  Hackathon sayfası: https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii
- Sabit bir iş bölümü yok, işleri kendiniz seçin. Ama bazı işler birbirine bağlı:

| Sıra | İş | Tahmini süre | Önce bitmesi gereken | Kimin hesabı gerekir |
|---|---|---|---|---|
| 1 | Kütüphaneye 36 dosya (önce 1 dosyayla kredi testi) | 10–15 dk | Yok | Evolus üyeliği (yetki yetmezse Aysu) |
| 2 | Evolus API anahtarı | 2 dk | Yok | Evolus, "New key" yetkisi (yetmezse Aysu) |
| 3 | Evolus ile canlı test (kendi bilgisayarınızda) | 10–15 dk | 2, kurulum (bölüm 3); 1 en azından başlamış olsun | Kendi Token Factory anahtarınız |
| 4 | Railway'e Evolus değişkenleri | 5 dk | 3 başarılı olmalı | **Aysu'nun Railway hesabı** (ya da davet) |
| 5 | Arayüzde Evolus'u göstermek | 30–45 dk | 3 (yeni alanları görmek için) | Yok (main'e push = Vercel'e otomatik yayın) |
| 6 | README'nin son hali | 30 dk | 3–5 bitince kesinleşir | Yok |
| 7 | Demo videosu | 1–2 sa | Evolus videoda görünecekse 4 ve 5 | Yok |
| 8 | Sunum | 1–2 sa | Yok, hemen başlanabilir | Yok |
| 9 | Teslim formu | 15 dk | Hepsi | lablab hesabı |

**Öneri:** Biriniz 1→5'i yürütürken diğeri sunuma ve README taslağına başlasın. Video en sona kalsın ve her şey
çalışırken çekilsin.

---

## 2. 16 Ekim'de neler yapıldı (sırasıyla)

1. **Önceki oturumda "A seçeneği" seçildi.** Buna göre Evolus hesabı, çalışma alanı ve anahtarlar ekipte kalıyor.
   Claude hesap açamaz, sitelere şifre ya da anahtar giremez, bilgisayarınızdan siteye dosya yükleyemez. Claude
   yüklenecek dosyaları hazırladı (commit `4631c7f`):
   - `deploy/evolus/standards/`: 36 dosya, her biri bir 29 CFR 1910 maddesi. API'nin alıntıladığı 36 maddeyle
     aynı. Toplam yaklaşık 1 MB (1.031.793 bayt). Kaynak eCFR, kamu malı.
   - `deploy/evolus/agent_instructions.md`: Ajanın talimatı. `backend/core/analyze.py` içindeki `DRAFT_SYSTEM`
     ile birebir aynı.
   - İkisi de `python -m backend.core.evolus_files` ile yeniden üretilebilir.
2. **Önceki oturumda verilen 5 adımlık Evolus kurulumu ve bugünkü durumu:**

   | Adım | Ne | Durum |
   |---|---|---|
   | 1 | Çalışma alanını açmak (etkinlik kodu **AMDACT3**), takımı davet etmek | ✅ Zaten yapılmıştı (13–14 Ekim). DarkSea28 açık, Çağrı ve İlhan katıldı |
   | 2 | Modeli bağlamak (Token Factory, DeepSeek-V4-Flash) | ✅ Zaten yapılmıştı (13 Ekim) |
   | 3 | Bilgi kütüphanesini kurup 36 dosyayı yüklemek | 🟡 Kütüphaneyi 16 Ekim'de Claude oluşturdu, dosyalar yüklenmedi |
   | 4 | Ajanı oluşturmak (ad, model, talimat, kütüphane) | ✅ 16 Ekim'de Claude oluşturdu |
   | 5 | API anahtarını oluşturup `.env` dosyasına yazmak | ❌ Yapılmadı (İş 2) |

3. **Evolus API'sinin kullanımı çözüldü.** İlk bakışta herkese açık bir belge bulunamadı (`docs.evolus.ai`
   adresi açılmıyor). Bu yüzden ajanı çağırma yolu önce app.evolus.ai'nin JavaScript kodundan çıkarıldı:
   `/agents/{id}/ask`. Anahtar başlığı ve Application ID, çalışma alanının "Developer keys" sayfasından
   doğrulandı. Sonra Evolus'un herkese açık geliştirici rehberi bulundu (https://evolus.ai/en/developers). Rehber
   ajanla konuşmanın resmi yolu olarak OpenAI uyumlu **agent chat** uç noktasını gösteriyor:
   `POST https://api.evolus.ai/v1/chat/completions`. Kod artık **varsayılan olarak bu belgelenmiş yolu**
   kullanıyor; `/ask` yolu yedek seçenek olarak duruyor (`EVOLUS_ENDPOINT=ask`). Ayrıntılar bölüm 5'te.
4. **Backend Evolus'a bağlandı** (commit `a9958bb`). Anahtar başlığının adı sonradan `X-APIKEY` olarak düzeltildi
   (commit `aaeed04`). Bu commit'le varsayılan yol, belgelenmiş agent chat oldu.
5. **Claude, Aysu'nun Evolus oturumunu kullanarak** (Claude uygulamasının tarayıcı paneli) şunları yaptı:
   - Kütüphaneyi ve ajanı oluşturdu, talimatı yapıştırdı.
   - Kütüphaneyi ajana bağladı ve ajanın sıcaklığını 0 yaptı.
   - Application ID'yi ve ajan ID'sini Aysu'nun `.env` dosyasına yazdı.
6. **Testler** (Aysu'nun bilgisayarında, 16 Ekim):
   - Evolus ayarlı değilken tam analiz: çalışıyor.
   - Sahte anahtarla: Evolus 401 döndü, taslağı otomatik olarak Token Factory yazdı.
   - Gerçek Evolus çağrısı: **yapılamadı**, çünkü anahtar yok.
7. **Bu commit'le gelenler:**
   - Ajan, Evolus'un belgelenmiş agent chat uç noktasından çağrılıyor (varsayılan). `/ask` yolu
     `EVOLUS_ENDPOINT=ask` ile seçilebilir.
   - `backend/core/evolus_check.py`: Evolus'u tek komutla denemek için.
   - Evolus hata mesajına ajanın cevabının ilk kısmı eklendi; sorun teşhisi kolaylaşıyor.
   - Bu not.

---

## 3. Kendi bilgisayarınızda kurulum

### 3.1 Gerekenler

- Git, **Python 3.12** (3.13 değil) ve arayüz için Node.js.
- Neden 3.12: Windows'ta Python 3.13.13, SciPy'nin lineer cebir modülü yüklendiği anda asyncio içinde çöküyor
  (access violation) ve API sunucusunu düşürüyor. scipy ya da numpy sürümünü düşürmek bunu çözmüyor.
- Kendi **AMD Token Factory anahtarınız** (`rc-...`). AMD mentoru herkesin kendi anahtarını almasını (redeem)
  istedi.

### 3.2 Kodu almak

```bash
git clone https://github.com/aysu-keskin/AMDhackathon.git
cd AMDhackathon
```

Depo zaten bilgisayarınızdaysa `git pull` yeterli. Depo şu an gizli (private). "Repository not found" hatası
alırsanız Aysu sizi GitHub'da depoya ekler (Settings → Collaborators).

### 3.3 Python ortamı

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
copy .env.example .env
```

macOS ya da Linux'ta: `python3.12 -m venv .venv`, `source .venv/bin/activate`, `cp .env.example .env`.

Veri indirmeniz gerekmiyor. API, depodaki `deploy/bundle` paketini kullanıyor (model, vaka dilimi, standart
alıntıları; yaklaşık 37 MB). Veri indirme ve yeniden eğitim yalnızca modeli baştan üretmek için gerekir:
`backend.pipeline.download`, `backend.pipeline.prepare`, `backend.model.baseline` (sonuncusu yaklaşık 25 dk).

### 3.4 `.env` dosyası

`.env` git'e girmez (`.gitignore`'da), herkes kendi bilgisayarında doldurur. `.env.example`'dan kopyalayınca
`LLM_MODEL` ve `LLM_FALLBACK_MODEL` boş gelir. Onları da doldurun, yoksa API "Set LLM_MODEL in .env" hatası
verir. Dosya şöyle olmalı:

```dotenv
# AMD Token Factory
TOKEN_FACTORY_BASE_URL=https://developer.amd.com.cn/radeon/api/v1
TOKEN_FACTORY_API_KEY=rc-...                      # KENDİ anahtarınız
LLM_MODEL=Gemma-4-31B-IT
LLM_FALLBACK_MODEL=DeepSeek-V4-Flash
LLM_DRAFT_MODEL=DeepSeek-V4-Flash

# Evolus
EVOLUS_BASE_URL=https://api.evolus.ai/api/v1
EVOLUS_API_KEY=                                   # İş 2'de oluşturulacak (evo_...)
EVOLUS_APP_ID=b727ec74-30fa-4028-a791-1ee16118cf34
EVOLUS_AGENT_ID=b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1
# İsteğe bağlı:
# EVOLUS_ENDPOINT=chat                            # "chat" (varsayılan, belgelenmiş yol) ya da "ask"
# EVOLUS_TIMEOUT=150                              # Evolus'un kaç saniye bekleneceği (varsayılan 150)
# EVOLUS_AGENT_MODEL=DeepSeek-V4-Flash            # arayüzde görünen model adı (varsayılan bu)
```

- `EVOLUS_APP_ID` ve `EVOLUS_AGENT_ID` gizli değil, anahtar olmadan bir işe yaramazlar.
- `TOKEN_FACTORY_API_KEY` ve `EVOLUS_API_KEY` **gizli**. Git'e, WhatsApp grubuna ya da Claude sohbetine yazmayın.

### 3.5 Çalıştırmak

İki ayrı terminalde:

```bash
uvicorn backend.api.main:app --port 8000
```

```bash
npm --prefix frontend install
npm --prefix frontend run dev
```

- API modelleri 3–10 saniyede yükler. Kontrol: http://localhost:8000/api/health adresi `{"ok":true}` döndürmeli.
- Arayüz http://localhost:5173 adresinde açılır ve `/api` isteklerini 8000 numaralı porta yönlendirir.
- Arayüzde bir örnek rapor seçip **Run live** ile canlı analiz yapabilirsiniz. Bir analiz 1–2 dakika sürer.

---

## 4. Evolus'un şu anki durumu

### 4.1 Adresler

| Ne | Adres |
|---|---|
| Hackathon sayfası (Join, kod **AMDACT3**) | https://evolus.ai/en/hackathon |
| Uygulama (giriş) | https://app.evolus.ai |
| Şirket paneli | https://app.evolus.ai/company |
| Model bağlantıları ("Your models") | https://app.evolus.ai/own-models |
| Kütüphaneler | https://app.evolus.ai/libraries |
| Ajanlar | https://app.evolus.ai/agents |
| Bizim ajan | https://app.evolus.ai/agents/b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1 |
| API anahtarları ("Developer keys") | https://app.evolus.ai/company/api-keys |
| Uygulama içi API belgesi (çağrılar oradan denenebilir) | https://app.evolus.ai/company/api-docs |
| **Herkese açık geliştirici rehberi** (agent chat, REST, MCP, sınırlar) | https://evolus.ai/en/developers |
| Agent chat API (OpenAI uyumlu, bizim varsayılanımız) | https://api.evolus.ai/v1 |
| REST API (`/ask` yolu bu adreste) | https://api.evolus.ai/api/v1 |
| Krediler | https://app.evolus.ai/company/billing/credits |

### 4.2 Çalışma alanı

- Ad **DarkSea28**. Panelde "YOUR COMPANY · DARKSEA28" yazıyor.
- Plan: **Developer Event · Free trial until 16/11/2026**. Geliştirici rehberi, etkinlik çalışma alanlarının
  **15 Kasım 2026 23:59'a (İtalya saati)** kadar ücretsiz olduğunu yazıyor.
- Rehberdeki sınırlar: çalışma alanı başına **50.000 platform kredisi**, **dakikada 60 API isteği**, en fazla
  6 kişi.
- Kişiler: 6 koltuktan 3'ü dolu; Aysu (AK), Çağrı (ÇK), İlhan (İÖ). Üçü de 14 Ekim'de etkinlik koşullarını
  kabul etti.
- Application ID: `b727ec74-30fa-4028-a791-1ee16118cf34`. Her API isteğinde `X-Application-Id` başlığında gider.

### 4.3 Model bağlantısı ("Your models")

- Bağlantının adı **AMD Token Factory**. Türü "OpenAI-compatible (vLLM on AMD, …)", durumu **Active**, adresi
  `https://developer.amd.com.cn/radeon/api/v1`.
- Son test 13/10/2026 21:37'de yapıldı; 12 modelden 8'i çalışıyor.
  - **DeepSeek-V4-Flash**: araç kullanıyor ("Uses tools"), akıl yürütüyor ("Reasons"), bağlamı 1049K.
  - **Gemma-4-31B-IT**: Evolus'un testinde **"Doesn't answer"**.
  - Ajanın modelinin DeepSeek olmasının bir nedeni bu. Diğer nedeni, Gemma'nın uzun taslakta 1–4 dakika sürmesi.
- Bu bağlantı, 13 Ekim'de kim kurduysa onun Token Factory anahtarını kullanıyor. Ajanın çağrıları o anahtarın
  günlük limitinden düşer (bkz. bölüm 7).
- Bu ayarlara **dokunmayın**:
  - "Use my connections for Evolus's internal functions too": **Kapalı** (Evolus'un önerisi).
  - "If my key doesn't answer": **Stop**. Token Factory yanıt vermezse istek durur ve Evolus kredisi harcanmaz.
    Bizim backend bu durumda zaten Token Factory'yi doğrudan dener.
- Bu çalışma alanında ajanlar yalnızca bizim bağladığımız modellerle çalışıyor. Evolus bunu "In this space agents,
  extractors and AI blocks of workflows run only on your models" diye yazıyor.

### 4.4 Kütüphaneler

| Kütüphane | Durum | Not |
|---|---|---|
| **OSHA 29 CFR 1910 (selected)** | 16 Ekim'de Claude oluşturdu. Türü **RAG library**: belgeler bölümlere ayrılıp dizinlenir, ajan içinde arama yapar. Tür sonradan değiştirilemez. Okuma motoru `openai/text-embedding-3-small`, depolama Database, PDF okuma "Let Evolus decide". **0 belge.** Ajana bağlı. | 36 dosya buraya yüklenecek (İş 1) |
| DarkSea28Memory1 | 13 Ekim'den kalma; boş, hiçbir ajan kullanmıyor | Kodu etkilemiyor. Silebilir ya da bırakabilirsiniz |

Bir kütüphane, onu kullanan ajan varken silinemez. Silinince içindeki belgeler de gider.

### 4.5 Ajan: Corrective Action Drafter

| Alan | Değer |
|---|---|
| ID | `b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1` |
| Ad | Corrective Action Drafter |
| Açıklama | Drafts OSHA-grounded corrective actions (EN/IT JSON) for a workplace incident report. |
| Talimat | `deploy/evolus/agent_instructions.md` dosyasının içeriği, birebir (958 karakter) |
| Model | DeepSeek-V4-Flash ("Your model" rozeti) |
| Motor | MICROSOFT_FRAMEWORK (Evolus'un varsayılanı) |
| Yaratıcılık (temperature) | 0 ("Precise"). Doğrudan Token Factory çağrısında da sıcaklık 0 |
| Reasoning | Model default |
| Real-time answers (streaming) | Açık (varsayılan) |
| Interactive replies in chat (widgets) | Açık (varsayılan). Ajanın cevabı JSON olarak çözülemezse kapatın (bkz. bölüm 11) |
| Kendi (kişisel) kütüphanesi | Boş, kullanmıyoruz |
| Bağlı kütüphane ("Other libraries") | OSHA 29 CFR 1910 (selected) |
| Skills, WebAPI, MCP, alt ajanlar, formlar | Yok |
| Nerede çalışıyor ("Where it works") | "Available in Chat" açık, şirketteki herkes konuşabilir. API için ayrı bir ayar yok; anahtarın yetkisi yetiyor |

"Test Asistani" adlı ajan 13 Ekim'deki bağlantı denemesinden kaldı. Kodu etkilemiyor, kalabilir.

### 4.6 API anahtarları

- Sayfa: https://app.evolus.ai/company/api-keys
- Çalışma alanında "Default API Key" adında bir anahtar var (13/10/2026, hiç kullanılmamış). **Bir anahtarın tam
  değeri yalnızca oluşturulduğu anda görünür.** Bunu kimse kaydetmediği için kullanılamıyor; yeni anahtar
  gerekiyor (İş 2).
- Aynı anahtar iki yolda farklı başlıklarla gönderiliyor:
  - **Agent chat** (bizim varsayılanımız): `Authorization: Bearer <anahtar>`. Application ID ayrı bir başlıkta
    değil, model adının içinde gidiyor: `"<applicationId>:<agentId>"`.
  - **REST API** (`/ask` yolu): sayfadaki "Details for developers" bölümüne göre anahtar **`X-APIKEY`**,
    Application ID **`X-Application-Id`** başlığında. Rehber aynı başlığı `X-ApiKey` diye yazıyor; HTTP başlık
    adlarında büyük/küçük harf fark etmez.
- Anahtar yetkisi varsayılan olarak "All employees", yani tüm ajanlar. İsterseniz yeni anahtarı yalnızca
  Corrective Action Drafter ile sınırlayabilirsiniz ("RESTRICT TO SPECIFIC AI EMPLOYEES").

---

## 5. Backend'deki Evolus bağlantısı

### 5.1 Akış

```
Olay raporu (İngilizce)
  │
  ├─ Yerelde: sınıflandırıcı (OIICS kodları) + BM25 ile benzer vakalar + BM25 ile standart alıntıları
  │           (en iyi 5 madde, ayrıca her zaman 1910.147 ve 1910.132)
  │
  ├─ İkinci görüş (olay ve kaynak kodu): doğrudan AMD Token Factory, Gemma-4-31B-IT        ← DEĞİŞMEDİ
  │     Gemma yanıt vermezse DeepSeek devreye girer; o durumda olay kodundaki "trusted" etiketi
  │     yalnızca sınıflandırıcının ölçülmüş kuralına göre verilir
  │
  └─ Önlem taslağı (ikinci görüşle aynı anda):
        EVOLUS_API_KEY, EVOLUS_APP_ID ve EVOLUS_AGENT_ID doluysa
            → Evolus ajanı "Corrective Action Drafter" → DeepSeek-V4-Flash @ AMD Token Factory
        Evolus hata verirse, süreyi aşarsa, JSON dönmezse, cevapta "actions" yoksa ya da Evolus ayarlı değilse
            → doğrudan AMD Token Factory: DeepSeek-V4-Flash, o da olmazsa Gemma-4-31B-IT
  │
  └─ Doğrulayıcı: her önlem, prompt'ta verilen alıntılardan TAM OLARAK BİR maddeye atıf yapmalı ve
     hüküm ya da teşhis dili içermemeli. Uymayanlar "rejected" listesine düşer.
```

### 5.2 Evolus çağrısı (`backend/llm/evolus.py`)

İki yol var. Hangisinin kullanılacağını `EVOLUS_ENDPOINT` belirliyor.

**a) `chat`: varsayılan, Evolus'un belgelediği yol** (https://evolus.ai/en/developers, "Agent chat")

- Uç nokta: `POST https://api.evolus.ai/v1/chat/completions` (OpenAI uyumlu).
- Başlıklar: `Authorization: Bearer <anahtar>`, `Content-Type: application/json`.
- Gövde:
  `{"model": "b727ec74-30fa-4028-a791-1ee16118cf34:b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1", "messages": [{"role": "user", "content": "<taslak prompt'u>"}]}`.
  Model adı `<applicationId>:<agentId>` biçiminde.
- `X-Conversation-Id` göndermiyoruz. Bu yüzden her rapor yeni bir sohbet olarak başlıyor ve geçmiş taşınmıyor.
- Yanıt OpenAI biçiminde; kod `choices[0].message.content`'i okuyor.
- Rehberden önemli bir not: "Model settings come from the agent: request parameters such as temperature are not
  applied." Yani sıcaklık gibi ayarlar istekten değil, ajanın Evolus'taki sayfasından geliyor. Ajanın sıcaklığı
  bu yüzden 0 yapıldı.
- Rehberde akışlı (`"stream": true`) kullanım ve ajanları listeleyen `GET https://api.evolus.ai/v1/models` da var.
  Akışlı kullanımı biz kullanmıyoruz.
- Bu yolda kütüphane kaynakları (citations) dönmüyor.
- 16 Ekim'de sahte anahtarla denendi. Cevap `HTTP 401: Invalid API key for the specified application` oldu: model
  adı (iki ID) kabul edildi, yalnızca anahtar reddedildi. Gerçek anahtarla çalışması bekleniyor.

**b) `ask`: Evolus web uygulamasının kendi kullandığı yol** (`EVOLUS_ENDPOINT=ask`)

- Uç nokta: `POST https://api.evolus.ai/api/v1/agents/{EVOLUS_AGENT_ID}/ask`
- Başlıklar: `X-APIKEY: <anahtar>`, `X-Application-Id: b727ec74-30fa-4028-a791-1ee16118cf34`,
  `Content-Type: application/json`.
- Gövde: `{"content": "<taslak prompt'u>", "skipChatHistory": true}`. Her rapor bağımsız gider, geçmiş yok.
- Yanıt JSON'unun alanları:
  - `answer`: ajanın metni.
  - `citations`: kütüphaneden gelen kaynaklar. Bu yolun artısı bu.
  - Diğerleri: `conversationId`, `agentId`, `question`, `title`, `threadId`, `totalTokenCount`, `fromGPT`,
    `parentConversationId`.
- Rehber, REST API'nin kapsamını "workflows, extractors, AI Tools, libraries" diye sayıyor; ajan sohbeti bu listede
  yok. Bu uç noktanın uygulama anahtarıyla çalışıp çalışmayacağı bu yüzden belirsiz.
- Akışlı bir sürümü de var (`/agents/{id}/ask-stream`); kullanmıyoruz.

**Her iki yolda ortak olanlar:**

- Ajanın cevabı JSON olarak okunuyor (önce ```json çiti temizleniyor) ve içinde `actions` listesi aranıyor.
- Bekleme sınırı `EVOLUS_TIMEOUT`, varsayılan 150 saniye.
- Ajana gönderilen prompt, doğrudan Token Factory'ye gönderilenin aynısı: rapor, tahmin edilen kodlar, 3 benzer
  vaka ve 5–7 standart alıntısı. Talimat (system prompt) ise Evolus'ta, ajanın içinde duruyor.
- Yeni bir bağımlılık yok; yalnızca Python'un standart kütüphanesi (urllib) kullanılıyor.

### 5.3 `/api/analyze` yanıtına eklenen alanlar

Taslak çağrısı (`amd.calls[1]`):

- `model`: Evolus yolunda `"DeepSeek-V4-Flash (Evolus agent)"`, doğrudan yolda `"DeepSeek-V4-Flash"` (ya da Gemma).
- `via`: `"evolus"` ya da `"token_factory"`.
- `evolus_error`: Evolus denendi ama olmadıysa nedeni (HTTP kodu ve hata gövdesinin başı; sorun JSON'daysa
  ajanın cevabının ilk 200 karakteri; yanıtın biçimi beklenmedikse `unexpected response shape`). Sorun yoksa
  `null`.

Ayrıca `amd.evolus` alanı Evolus'un ayarlı olup olmadığını gösterir (`true` ya da `false`).

Eski kayıtlarda (replay) bu alanlar yok. Arayüz bunları isteğe bağlı kabul etmeli.

### 5.4 Dosyalar

| Dosya | Ne yapar |
|---|---|
| `backend/llm/evolus.py` | Evolus istemcisi (`EvolusAgent`) |
| `backend/core/analyze.py` | `Analyzer.draft()`: önce Evolus, olmazsa Token Factory. `DRAFT_SYSTEM` talimatı da burada |
| `backend/core/evolus_check.py` | Tek komutla canlı test (İş 3) |
| `backend/core/evolus_files.py` | `deploy/evolus/` dosyalarını yeniden üretir |
| `deploy/evolus/standards/*.md` | Kütüphaneye yüklenecek 36 dosya |
| `deploy/evolus/agent_instructions.md` | Ajanın talimatı |
| `.env.example` | Evolus değişkenleri eklendi |

### 5.5 Dikkat edilmesi gereken üç nokta

1. **Talimat iki yerde duruyor.** `backend/core/analyze.py` içindeki `DRAFT_SYSTEM` değişirse:
   `python -m backend.core.evolus_files` komutunu çalıştırın, yeni `deploy/evolus/agent_instructions.md`
   içeriğini Evolus'ta ajanın **What it does → Instructions** alanına yapıştırın ve **Save changes** deyin.
   Yapmazsanız Evolus yolu ile doğrudan yol farklı davranır. 36 maddenin listesi değişirse aynı komutla dosyaları
   yeniden üretip kütüphaneye yeniden yükleyin; `python -m backend.core.bundle` ile dağıtım paketini de yenileyin.
2. **Atıf kuralı.** Doğrulayıcı yalnızca prompt'ta verilen alıntılardaki maddeleri kabul ediyor. Ajan kütüphanede
   arayıp, 36 madde arasında olan ama prompt'taki 5–7 alıntıda olmayan bir maddeye atıf yaparsa, o önlem
   "standard not in the provided excerpts" gerekçesiyle reddedilir. Testte bu sık olursa ekip karar versin:
   - Kural aynen kalabilir: güvenli ve ölçülen davranış bu.
   - Ya da bilinen 36 maddenin hepsi kabul edilebilir (`analyze.py` içindeki `allowed` kümesi).

   Ekip karar vermeden değiştirmeyin.
3. **Kaynaklar (citations) arayüze gelmiyor.** Kaynaklar yalnızca `ask` yolunda dönüyor; varsayılan `chat`
   yolunda yok. Gelirse taslak verisinin içinde `_citations` olarak duruyor ama API yanıtına eklenmiyor.
   Göstermek isterseniz `analyze.py`'de `action_plan`'a ekleyip arayüzde gösterin (isteğe bağlı).

### 5.6 Neler test edildi, neler edilmedi

| Test (16 Ekim, Aysu'nun bilgisayarında) | Sonuç |
|---|---|
| Evolus ayarlı değil, tam analiz ("press" örneği) | ✅ İkinci görüş Gemma 38,7 sn; taslak doğrudan DeepSeek 69,5 sn; toplam 73,1 sn; 4 önlem kabul, 0 ret |
| Sahte Evolus anahtarı, tam analiz (`evolus_check`, o sırada `ask` yolu) | ✅ Evolus hemen 401 döndü, taslağı doğrudan DeepSeek yazdı (104,6 sn); toplam 108,1 sn; 4 önlem. Gemma o anda yanıt vermediği için ikinci görüşü DeepSeek verdi (9,2 sn) |
| Sahte anahtar, `chat` yolu, yalnızca `draft()` | ✅ `HTTP 401: Invalid API key for the specified application` (iki ID kabul edildi), yedek Token Factory'ye geçildi |
| Sahte anahtar, `chat` yolu, tam analiz (`evolus_check fryer`, son sürüm) | ✅ 401, yedek devreye girdi: taslak doğrudan DeepSeek 105,4 sn; toplam 109,0 sn; 5 önlem kabul, 0 ret. İkinci görüşü yine DeepSeek verdi (7,8 sn); Gemma 16 Ekim akşamı iki testte de yanıt vermedi |
| Sahte anahtar, `ask` yolu, yalnızca Evolus çağrısı | ✅ `HTTP 401: Authentication required` |
| Evolus ayarlı değil, yalnızca `draft()` | ✅ Doğrudan Token Factory kullanıldı |
| **Gerçek anahtarla Evolus ajanı** | ❌ **Denenmedi** (İş 3) |
| Railway'de Evolus | ❌ Değişkenler yok (İş 4) |

---

## 6. Kalan işler, adım adım

### İş 1: 36 dosyayı Evolus kütüphanesine yüklemek (önce kredi testi)

**Neden önce tek dosya:** Kütüphaneye yükleme ve dizinleme Evolus'un kendi modelleriyle yapılıyor ve
**çalışma alanının kredisinden düşüyor**. Evolus dosya başına fiyat göstermiyor. Maliyetin metnin uzunluğuyla
arttığını varsayıyoruz; bu yüzden test dosyası çok küçük değil, orta boy olmalı. (Sohbette önce 1910.212
denmişti. O dosya 2,6 KB, maliyeti olduğundan düşük gösterir; bu yüzden 1910.147 seçildi.)

1. https://app.evolus.ai/company/billing/credits adresinde bakiyeyi not edin. 16 Ekim akşamı **50.000** krediydi,
   hiç harcanmamıştı.
2. https://app.evolus.ai/libraries adresinde, üstteki açılır listede **OSHA 29 CFR 1910 (selected)** seçili olsun
   (**DarkSea28Memory1 değil**).
3. **Upload a document** ile yalnızca `deploy/evolus/standards/29CFR_1910.147.md` dosyasını yükleyin. Dosya 31 KB,
   yani toplamın yaklaşık 1/33'ü. Bu madde zaten her analizde kullanılıyor.
4. Belgenin işlenmesini bekleyin; listede görünür ve durumu tamamlanır. Birkaç dakika sürebilir.
5. Krediler sayfasındaki "What happened to your credits → Movements" bölümünden (ya da "See usage" bağlantısından)
   harcanan krediye bakın.
6. **Hesap:** harcanan kredi × 33 ≈ 36 dosyanın toplam maliyeti.
   - **10.000'in altındaysa** (aylık 50.000'in %20'si) kalan 35 dosyayı yükleyin.
   - **Üstündeyse** durun ve ekip olarak karar verin. Seçeneklerden biri yalnızca şu 10 maddeyi yüklemek (yaklaşık
     234 KB): `1910.147, 1910.132, 1910.212, 1910.219, 1910.217, 1910.178, 1910.138, 1910.133, 1910.22, 1910.28`.
     Bu seçimin gerekçesi:
     - 147 ve 132 her analizde prompt'a ekleniyor.
     - 132, 147, 178, 217 ve 219 kayıtlı demo sonuçlarında atıf alan maddeler.
     - 212 genel makine koruması.
     - 138, 133, 22 ve 28 sık rastlanan KKD ile zemin ve düşme maddeleri.
   - Kütüphane hiç doldurulmasa da sistem çalışır, çünkü alıntılar zaten prompt'ta gidiyor. Kütüphane, Evolus
     ödülündeki "en az iki yapı taşı" şartı ve kaynak göstermek için önemli.
7. Kalan dosyalar için **Upload a document**'a basın, `deploy\evolus\standards` klasörünü açın ve **Ctrl+A** ile
   hepsini seçin. 147'yi bir daha yüklememek için Ctrl+tık ile seçimden çıkarın.
   - Pencere tek dosya kabul ediyorsa, dosyaları klasörden sürükleyip kütüphane kartının üzerine bırakmayı deneyin.
   - O da olmazsa dosyaları tek tek yükleyin.
8. Bittiğinde kütüphane kartında **DOCUMENTS (36)** yazmalı ve kütüphanenin ajan tarafından kullanıldığı görünmeli.

**Dikkat, yanlış yere yüklemeyin:** Ajan sayfasının **What it knows** sekmesinin en üstündeki büyük "Drag your
documents here / + Upload document" alanı ajanın **kişisel** kütüphanesidir; oraya yüklemeyin. Ajan sayfasından
yükleyecekseniz aynı sekmedeki **Other libraries → OSHA 29 CFR 1910 (selected) → Upload** düğmesini kullanın.

Kabul edilen biçimler: metin, Markdown, CSV, JSON, XML, HTML, PDF ve Word (.docx); dosya başına en fazla 50 MB.
Bizim dosyalar .md uzantılı; en büyüğü 272 KB (1910.1200).

### İş 2: Evolus API anahtarı oluşturmak

1. https://app.evolus.ai/company/api-keys adresinde **New key**'e basın.
2. Bir ad verin, örneğin `darksea28-backend`. İsterseniz yetkiyi yalnızca **Corrective Action Drafter** ile
   sınırlayın.
3. **Tam anahtar yalnızca bir kez gösterilir.** Hemen kopyalayın.
4. Kendi `.env` dosyanıza yazın: `EVOLUS_API_KEY=evo_...`
5. Aynı değer İş 4'te Railway'e girilecek. Takımla paylaşmanız gerekirse yalnızca birebir özel mesajla paylaşın;
   grup sohbetine, git'e ya da Claude sohbetine yazmayın.
6. **New key** düğmesini görmüyorsanız rolünüzün yetkisi yetmiyor demektir. Aysu ya anahtarı kendisi oluşturur ya
   da https://app.evolus.ai/company adresinde "Change someone's role" ile rolünüzü değiştirir.
7. Eski "Default API Key"e dokunmanız gerekmiyor; hiç kullanılmadı. Silmek isterseniz aynı sayfada
   Danger zone → Delete.

### İş 3: Evolus ile canlı test (kendi bilgisayarınızda)

Başlamadan önce: kurulum (bölüm 3) tamamlanmış olmalı, `.env`'de Token Factory anahtarınız ve üç Evolus değişkeni
dolu olmalı, İş 1 en azından başlamış olmalı.

**Önce anahtarı hızlıca kontrol edin** (isteğe bağlı; Token Factory harcamaz). Rehberdeki ajan listesi çağrısı:

```powershell
Invoke-RestMethod -Uri https://api.evolus.ai/v1/models -Headers @{ Authorization = "Bearer evo_ANAHTARINIZ" }
```

Listede `b727ec74-30fa-4028-a791-1ee16118cf34:b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1` görünüyorsa anahtar ve ajan
doğru. 401 dönüyorsa anahtar yanlış. (Bu komut anahtarı PowerShell geçmişine yazar; paylaşılan bir bilgisayarda
yapmayın.)

Sonra tam test:

```bash
python -m backend.core.evolus_check
```

Başka bir örnekle denemek için örneğin `python -m backend.core.evolus_check forklift`. Seçenekler: press, forklift,
conveyor, fryer. Test bir analiz kadar Token Factory harcar (iki çağrı) ve 1–3 dakika sürer.

Başarılı bir çıktı şöyle görünür (süreler örnek; kendi sürenizi not edin):

```
Evolus configured: True
...
Draft:          DeepSeek-V4-Flash (Evolus agent) | 85.0 s | via: evolus | error: None
Actions kept: 4 | rejected: 0 | total 88.0 s
RESULT: OK, the draft came from the Evolus agent.
```

Çıktıyı yorumlamak için:

| Çıktıda ne yazıyor | Anlamı | Ne yapmalı |
|---|---|---|
| `RESULT: OK` | Evolus yolu çalışıyor | Süreyi not edin, İş 4'e geçin |
| `missing in .env: ...` | `.env`'de bir değişken eksik | Eksik değişkeni doldurun |
| `HTTP 401` (`Invalid API key for the specified application` ya da `Authentication required`) | Anahtar yanlış ya da eksik kopyalanmış, ya da başka bir çalışma alanının anahtarı | Anahtarı yeniden kopyalayın, gerekirse yeni anahtar oluşturun |
| `HTTP 400: Invalid model format` | `EVOLUS_APP_ID` ya da `EVOLUS_AGENT_ID` boş veya bozuk | İki ID'yi bu nottaki değerlerle karşılaştırın |
| `HTTP 403` | Anahtarın yetkisi bu ajanı kapsamıyor | Anahtar sayfasında yetkiyi "All employees" yapın ya da bu ajanı ekleyin |
| `HTTP 404` | Ajan ID'si ya da Application ID yanlış | `.env`'deki iki ID'yi bu nottaki değerlerle karşılaştırın |
| Anahtar doğru olduğu halde `chat` yolu sürekli hata veriyor | Bu yol beklenmedik biçimde çalışmıyor | `.env`'e `EVOLUS_ENDPOINT=ask` yazıp tekrar deneyin; `ask` de olmazsa `chat`'e geri dönün |
| `unexpected response shape` | Evolus beklenmedik biçimde bir JSON döndürdü | Hata metnindeki yanıtın başına bakın; diğer yolu deneyin (`EVOLUS_ENDPOINT`) |
| `HTTP 402` | Kredi ya da ödeme sorunu | Krediler sayfasına bakın |
| `HTTP 429` | Çok sık istek gönderilmiş | Bir dakika bekleyip tekrar deneyin |
| `HTTP 5xx` | Evolus'ta ya da Token Factory'de geçici hata | Biraz sonra tekrar deneyin; "Your models" sayfasında **Test again** |
| `unparseable JSON; answer began: ...` | Ajan JSON dışında bir şey yazdı | Bölüm 11'deki JSON maddesine bakın |
| `no actions in the agent's answer` | JSON geldi ama içinde `actions` yok | Talimat eksik ya da yanlış yapıştırılmış olabilir; yeniden yapıştırın |
| `TimeoutError` ya da `timed out` | Ajan `EVOLUS_TIMEOUT` süresinde cevap vermedi | Aşağıdaki hız kararına bakın |
| Çok sayıda `rejected ...: standard not in the provided excerpts` | Ajan prompt'ta olmayan maddelere atıf yapıyor | Bölüm 5.5'teki 2. madde: ekip kararı |

**Testten sonra hız kararı:**

- 2–3 test yapıp Evolus'un taslak süresini not edin. Doğrudan yol bugün 70–105 saniye sürdü.
- `EVOLUS_TIMEOUT`'u gözlediğiniz en uzun sürenin yaklaşık 1,3 katına ayarlayın; örneğin en uzun süre 100 saniyeyse
  130. Çok kısa tutarsanız başarılı Evolus cevapları kesilir ve sistem her seferinde yedeğe düşer.
- En kötü durumda kullanıcı yaklaşık `EVOLUS_TIMEOUT` + 70–105 saniye bekler: önce Evolus'un süresi dolar, sonra
  yedek çağrı yapılır. Varsayılan ayarla bu yaklaşık 4 dakika eder.
- Evolus sürekli çok yavaş kalırsa iki seçenek var; ekip karar versin:
  - (a) Evolus'u yalnızca demo ve video için açık tutmak. Railway'den `EVOLUS_API_KEY` silinince sistem doğrudan
    yola döner.
  - (b) Yavaşlığı kabul edip arayüzde bekleme mesajı göstermek.

**İsteğe bağlı hızlı kontrol (API anahtarı gerekmez):** Ajan sayfasının **Try it** sekmesine bir örnek rapor
yapıştırıp cevabın JSON olarak gelip gelmediğine bakabilirsiniz. Bu yalnızca kaba bir kontrol; backend daha uzun
bir prompt gönderiyor (kodlar, benzer vakalar, alıntılar).

### İş 4: Railway'e Evolus değişkenlerini eklemek

Railway hesabı Aysu'da. Bu işi ya Aysu yapar ya da sizi projeye davet eder.

1. https://railway.com adresinde **diplomatic-rejoicing** projesini açın, API servisini seçin (GitHub'daki
   `aysu-keskin/AMDhackathon`'dan kurulu) ve **Variables** sekmesine gidin.
2. Şunları ekleyin:
   - `EVOLUS_API_KEY`: İş 2'deki anahtar
   - `EVOLUS_APP_ID`: `b727ec74-30fa-4028-a791-1ee16118cf34`
   - `EVOLUS_AGENT_ID`: `b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1`
   - İsterseniz `EVOLUS_TIMEOUT`: İş 3'te karar verdiğiniz değer
   - Yalnızca İş 3'te `ask` yolu seçildiyse `EVOLUS_ENDPOINT` = `ask`
   - `EVOLUS_BASE_URL` ve `EVOLUS_CHAT_URL` gerekmiyor, kodda varsayılan değerleri var.
3. Mevcut 5 değişkene dokunmayın: `TOKEN_FACTORY_BASE_URL`, `TOKEN_FACTORY_API_KEY`, `LLM_MODEL=Gemma-4-31B-IT`,
   `LLM_FALLBACK_MODEL=DeepSeek-V4-Flash`, `LLM_DRAFT_MODEL=DeepSeek-V4-Flash`.
4. Railway, değişikliklerin uygulanması için yeniden yayın ister. Çıkan **Deploy** düğmesine basın ve servis
   "Online" olana kadar bekleyin.
5. Kontrol edin:
   - https://amdhackathon-production.up.railway.app/api/health adresi `{"ok":true}` döndürmeli. Sunucu uyuyorsa
     45 saniyeye kadar sürebilir.
   - Arayüzde (https://am-dhackathon.vercel.app) bir örnek rapor seçip **Run live**'a basın. "What ran on AMD"
     panelinde taslak satırı `DeepSeek-V4-Flash (Evolus agent)` olmalı.
   - Ya da PowerShell'den:

     ```powershell
     $body = @{ text = "A press operator was trying to remove a stuck part from the die by hand when the mechanical power press cycled. The tip of his right index finger was amputated." } | ConvertTo-Json
     $r = Invoke-RestMethod -Method Post -Uri https://amdhackathon-production.up.railway.app/api/analyze -ContentType "application/json" -Body $body -TimeoutSec 600
     $r.amd.calls | Format-List
     ```

6. **Geri almak için:** `EVOLUS_API_KEY` değişkenini silip yeniden yayınlayın. Sistem doğrudan Token Factory'ye
   döner.

### İş 5: Arayüzde Evolus'u göstermek

Amaç: Hakem, taslağı Evolus ajanının yazdığını ve çalışma alanının adını görsün.

1. `frontend/src/lib/api.ts` (32. satır): `amd` tipine isteğe bağlı alanları ekleyin:

   ```ts
   amd: {
     endpoint: string
     evolus?: boolean
     calls: { purpose: string; model: string; seconds: number; error: string | null
              via?: "evolus" | "token_factory"; evolus_error?: string | null }[]
   }
   ```

   Alanlar isteğe bağlı olmalı, çünkü eski kayıtlarda (replay, `frontend/public/data/replay.json`) yoklar.
2. `frontend/src/pages/Analyze.tsx` içindeki `AmdPanel` (yaklaşık 340–360. satırlar):
   - `c.via === "evolus"` ise satırın altına küçük bir rozet ya da metin ekleyin: Evolus ajanı ve çalışma alanı
     **DarkSea28**.
   - `c.evolus_error` doluysa kısa bir not gösterin: Evolus yanıt vermedi, taslak doğrudan Token Factory'de yazıldı.
3. `frontend/src/lib/i18n.tsx`: metinleri iki dilde ekleyin. İngilizce blokta `amdTitle`/`amdHelp` yaklaşık
   49–50. satırlarda, İtalyanca blokta yaklaşık 125–126. satırlarda. Önerilen metinler:
   - EN: `Drafted by our Evolus agent “Corrective Action Drafter” (workspace DarkSea28), running DeepSeek-V4-Flash on AMD Token Factory.`
     ve `Evolus did not answer; drafted directly on AMD Token Factory.`
   - IT: `Bozza redatta dal nostro agente Evolus “Corrective Action Drafter” (workspace DarkSea28), con DeepSeek-V4-Flash su AMD Token Factory.`
     ve `Evolus non ha risposto; bozza redatta direttamente su AMD Token Factory.`
4. `npm --prefix frontend run build` ve `npm --prefix frontend run lint` hatasız geçmeli. **main'e push etmek,
   Vercel'e otomatik yayın demek.** Build'i kendi bilgisayarınızda geçirmeden push etmeyin.
5. İsteğe bağlı, kayıtları Evolus'la yenilemek. İş 4'ten sonra ve `.env`'de Evolus değişkenleri doluyken:

   ```bash
   python -m backend.core.samples        # 4 örneği canlı analiz eder → reports/demo_replay.json
   python -m backend.core.export_static  # arayüzün çevrimdışı verisini yeniler → frontend/public/data/
   ```

   Sonra `reports/demo_replay.json` ve `frontend/public/data/*.json` dosyalarını commit'leyin. Mevcut kayıtlar
   15 Ekim tarihli ve Evolus kullanılmadan alındı.
6. İsteğe bağlı: Evolus'un kaynaklarını (`citations`) göstermek (bölüm 5.5'teki 3. madde).

### İş 6: README'nin son hali (İngilizce)

Eklenecekler:

- Bir **Evolus** bölümü (aşağıdaki taslak).
- "Deployment" bölümündeki Railway değişken listesine `EVOLUS_API_KEY`, `EVOLUS_APP_ID`, `EVOLUS_AGENT_ID` ve
  isteğe bağlı `EVOLUS_TIMEOUT`.
- Canlı bağlantılar: arayüz ve API.
- Test komutu: `python -m backend.core.evolus_check`.

Taslak (gerektiği gibi uyarlayın):

```markdown
## Evolus

The corrective-action draft is written by our Evolus agent **Corrective Action Drafter** (workspace DarkSea28).
Its model is DeepSeek-V4-Flash served by AMD Token Factory, connected in Evolus as our own OpenAI-compatible
vLLM endpoint, and its knowledge library holds the same 36 OSHA 29 CFR 1910 sections the API cites
(`deploy/evolus/standards`). The API calls the agent through Evolus's OpenAI-compatible agent chat
(`POST https://api.evolus.ai/v1/chat/completions`, model `<applicationId>:<agentId>`);
if Evolus is unavailable it drafts directly on AMD Token Factory, and the UI shows which path was used.
Evolus building blocks used: a specialized agent, a document (RAG) library and the Evolus API.
```

Ölçüm sayfasına ve ölçüm notlarına dokunmayın. Katı (strict) skorlamanın başarısız olması ve önceden bildirilen
sapma orada açıkça gösteriliyor (bkz. bölüm 10).

### İş 7: Demo videosu

Videoda gösterilmesi önerilenler:

- Sorun: fabrika iş güvenliği sorumlusu, serbest metin olay raporu.
- Örnek bir raporla **Run live**: OIICS kodları ve güven etiketleri (trusted / approximate / human).
- Benzer gerçek OSHA vakaları.
- OSHA atıflı önlem taslağı; düzenleme, onaylama ve indirme.
- "What ran on AMD" paneli: Token Factory ve Evolus ajanı.
- Evolus ekranları: model bağlantısı, ajan, kütüphane.
- Ölçüm sayfası, katı skorlamanın başarısızlığı ve sapmanın açıkça gösterildiği bölümüyle birlikte.
- EN/IT dil geçişi.

İpuçları:

- API uyuyor. Çekimden bir dakika önce health adresini açın.
- Canlı bir analiz 1–2 dakikadan uzun sürebilir. Çekip sonra kesin. Kayıtlı sonuçları gösterecekseniz arayüz
  onları zaten "kayıt" diye etiketliyor; bunu saklamayın.

### İş 8: Sunum

Kullanılabilecek ölçülmüş sonuçlar (kaynak dosyaları `reports/` altında; rakamları oradan doğrulayın):

- **Güven etiketleri, B seçeneği** (`reports/confidence_test.json`, 2025 imalat test seti):
  - Olay kodu: raporların %69,1'i "trusted", doğruluk %92,8 (%95 GA 91,6–93,9).
  - Yaralanma türü: %77,6 "trusted", doğruluk %96,9.
  - Vücut bölgesi: yaklaşık %80 "trusted", doğruluk %94,5.
  - Kaynak (source) hiçbir zaman "trusted" değil; ilk 3 öneri gösteriliyor, seçimi insan yapıyor.
  - En düşük %20 ve nadir sınıflar insana gidiyor.
- **LLM ikinci görüş** (`reports/llm_second_opinion*.json`, 500 rapor, Gemma-4-31B-IT, önceden kayıt
  `reports/PREREG-llm-second-opinion.md`):
  - Önceden kaydedilen katı skorlama **başarısız** oldu, çünkü Gemma "65" yerine "65: başlık" yazdı.
  - Açıkça bildirilen sapmayla (cevabın başındaki kodu okumak) kural A: %65,4 "trusted", doğruluk %94,8.
    Kural B: %71,4 "trusted", doğruluk %94,4. Karar B.
  - LLM tek başına %83,8, sınıflandırıcı tek başına %79,6.
  - **İki sonuç da raporlanmalı.**
- AMD kullanımı: bütün LLM çağrıları AMD Token Factory'den geçiyor (Gemma-4-31B-IT ve DeepSeek-V4-Flash). Kod,
  Token Factory adresini açıkça çağırıyor (`backend/llm/token_factory.py`).
- Evolus: ajan, RAG kütüphanesi ve API. Model AMD'de.
- PII: maskeleme yok, bilinçli bir karar. Uygulama işveren, adres ve koordinatları göstermiyor. Sunumda en fazla
  bir "sonraki adımlar" satırı.

### İş 9: Teslim formu (lablab)

- **Demo Application URL:** https://am-dhackathon.vercel.app. Mentorun söylediği gibi bu, doğrudan canlı
  uygulamanın bağlantısı olmalı.
- Kol: Intelligent Industry. Ek ödüller: Evolus ödülü ve Google DeepMind "Best use of Gemma" (Gemma'yı Token
  Factory üzerinden kullanmamız bu ödüle uygun).
- **Depo şu an gizli.** Form herkese açık bir repo istiyorsa, teslimden önce Aysu depoyu herkese açsın
  (GitHub → Settings → Danger Zone → Change visibility). 16 Ekim'de git geçmişi tarandı: `.env` hiç commit'lenmemiş
  ve geçmişte anahtar yok. Herkese açmadan önce yeni commit'leri de kontrol edin.
- Video ve sunum bağlantıları.

---

## 7. Kredi ve maliyet

| Ne | Neyden harcar | Not |
|---|---|---|
| Kütüphaneye yükleme ve dizinleme (embedding) | **Evolus kredisi** | Dosya başına fiyat gösterilmiyor. İş 1'deki tek dosyalık testle ölçülecek |
| Taranmış belge okuma, AI Tools, güvenlik kontrolleri | **Evolus kredisi** | Evolus'un kendi ifadesi: "Reading scans, libraries, AI Tools and safety checks stay on Evolus models and use the credits of the space." |
| Ajanın cevap yazması (DeepSeek, bizim bağlantımız) | Evolus kredisi **harcamaz**, Token Factory'den düşer | "Requests made with your keys use no credits and no Evolus fee: you only pay your provider." |
| Token Factory yanıt vermezse | Hiçbir şey; istek durur | "If my key doesn't answer = Stop" sayesinde. Backend kendi yedeğine geçer |
| Backend'in doğrudan çağrıları | Token Factory (`.env`'deki ya da Railway'deki anahtar) | |

- **Evolus API sınırı:** çalışma alanı başına dakikada 60 istek (rehber). Bir analiz Evolus'a 1 istek atıyor.
- **Evolus kredisi:** 50.000. Aylık; 13/11/2026'da sıfırlanıyor. Ekstra kredi 0. Bu planda kredi satın alma
  fiyatı tanımlı değil, yani biterse yenisi alınamıyor. 16 Ekim akşamı itibarıyla hiç harcanmadı.
- **Token Factory:** anahtar başına günde 1 dolar sınırı, dakikada 20 istek, aynı anda 8 istek. Embedding uç
  noktası yok. Bir analiz 2 çağrı. 500 çağrılık test yaklaşık 0,014 dolar tuttu; yani para değil, dakika başı
  istek sınırı önemli.
- Evolus ajanının çağrıları, Evolus'taki bağlantıya girilmiş Token Factory anahtarından düşer. Backend'in
  doğrudan çağrıları ise `.env`'deki ya da Railway'deki anahtardan düşer. Bu ikisi farklı anahtarlar olabilir.

---

## 8. Zaman ve hız

| Ölçüm | Süre |
|---|---|
| 500 raporluk testte Gemma ikinci görüşü | medyan 14,8 sn, 90. yüzdelik 70,4 sn |
| Railway'de canlı analiz (16 Ekim öğlen) | Gemma 3,5 sn, DeepSeek taslağı 79 sn |
| Yerel analiz 1 (16 Ekim akşam, Evolus kapalı) | Gemma 38,7 sn, taslak 69,5 sn, toplam 73,1 sn |
| Yerel analiz 2 (sahte anahtar, Evolus 401) | İkinci görüş DeepSeek 9,2 sn, taslak 104,6 sn, toplam 108,1 sn |
| Yerel analiz 3 (sahte anahtar, `chat` yolu, 401) | İkinci görüş DeepSeek 7,8 sn, taslak 105,4 sn, toplam 109,0 sn |
| Evolus ajanıyla taslak | **Henüz ölçülmedi** (İş 3) |
| Railway'in uyanması | 45 saniyeye kadar (arayüz bu sürede "bağlanıyor" mesajı gösteriyor) |

- İki LLM çağrısı aynı anda gidiyor, toplam süreyi uzun olan belirliyor (genelde taslak).
- Evolus'a kütüphane araması da eklendiği için Evolus yolunun daha yavaş olması beklenir. En kötü durum için
  İş 3'teki hız kararına bakın.
- Arayüzün analiz isteğinde zaman sınırı yok. Yalnızca sağlık kontrolü 45 saniye bekliyor.

---

## 9. "Şimdi mi yükleyelim, önce backend'e mi bakalım?" kararı

Bu soru 16 Ekim akşamı konuşuldu. Karşılaştırma şöyleydi:

| | **A) Dosyaları şimdi yüklemek** | **B) Önce backend'i gözden geçirmek** |
|---|---|---|
| Zaman | 5 dakikalık iş; dizinleme arka planda sürer, bu arada incelemeye geçilir | Evolus testi incelemenin sonuna kalır; sorun çıkarsa son güne sıkışır |
| Teslim riski | Düşük; Evolus uçtan uca bugün denenir, sorun varsa bugün görülür | Yüksek; teslim büyük ihtimalle 17 Ekim ve en riskli parça geç anlaşılır |
| Kredi | Az olması bekleniyor; tek dosyalık testle ölçülür | Aynı maliyet, yalnızca daha sonra |
| Boşa gitme riski | Yalnızca 36 maddelik liste değişirse yeniden yüklemek gerekir; liste 15 Ekim'de kararlaştırıldı | Yok |
| Evolus ödülü | Ajan ve kütüphane bugünden çalışır durumda olur | Son güne kalır |

**Karar: A.** Dosyalar yüklenirken backend paralel olarak gözden geçirilebilir. İkisi birbirini beklemiyor.
B yalnızca gözden geçirmede 36 maddelik listenin ya da ajan talimatının gerçekten değişmesi bekleniyorsa mantıklı.

Hız riski her iki seçenekte de aynı. Testi erken yapmanın asıl nedeni bu riski erken görmek.

---

## 10. Daha önce alınmış kararlar (değiştirmeyin)

- **AMD kullanımı yalnızca Token Factory'den.** İnce ayar yok, droplet yok. AMD mentoru (Discord, Maharshi),
  Token Factory'nin Evolus'un "kendi vLLM'iniz" şartını karşıladığını ve resmi "anlamlı AMD kullanımı" olduğunu
  söyledi. Ekibin parası yok; her şey ücretsiz kalmalı.
- **Ürün modeli** yeni kod sistemi (2024-01-01 sonrası) üzerinde, bütün sektörlerle eğitildi:
  - Ayrım: 2024 eğitim, 2025 test (imalat). Son ürün modeli 2024 ve 2025 birlikte kullanılarak yeniden eğitildi.
  - Tahmin edilenler: olay, kaynak ve vücut bölgesi için 2 haneli grup; yaralanma türü için 3 hane.
  - Eğitimde 30'dan az örneği olan sınıflar insana bırakılıyor.
  - Eski sistem modeli yalnızca ölçüm sayfasında kullanılıyor.
- **Güven etiketleri B seçeneği** (bölüm 6, İş 8). Eşikler test setine bakılarak yeniden ayarlanmayacak.
- **İkinci görüş kuralı B**, Gemma ile ölçüldü; Gemma'nın prompt'u test edilen haliyle aynen kalıyor. Gemma
  yanıt vermezse DeepSeek'in seçimi gösteriliyor, ama olay kodundaki "trusted" etiketi yalnızca sınıflandırıcının
  kuralına göre veriliyor.
- **Taslağı DeepSeek-V4-Flash yazıyor**, çünkü daha hızlı. Gemma yedek. Evolus ajanı da DeepSeek kullanıyor.
- Ölçüm sayfası katı skorlamanın başarısızlığını ve sapmayı **açıkça** gösteriyor; bu kalmalı.
- Girdi yalnızca İngilizce. Benzer vakalar BM25 ile, yalnızca yeni sistem vakalarından bulunuyor. Standartlar
  eCFR'den seçilmiş 36 madde.
- Arayüz: Analiz ve Ölçüm sayfaları, EN/IT geçişi, önlemlerde düzenle/onayla/indir (veritabanı yok), örnek
  raporlar ve etiketli kayıtlar.
- Barındırma: API Railway'de (ücretsiz deneme), arayüz Vercel Hobby'de. API'ye ulaşılamazsa arayüz paketli
  kayıtları ve ölçümleri gösteriyor. 37 MB'lık `deploy/bundle` bilinçli olarak commit'lendi.
- **PII maskeleme yok.** Uygulama işveren, adres ve koordinatları göstermiyor.
- Mimari: Bizim backend Evolus ajanını API ile çağırıyor. Başta düşünülen "Evolus ajanı bizim MCP sunucumuzu
  çağırsın" yönü kullanılmıyor. `api.evolus.ai/mcp`, Evolus'un kodlama ajanlarına açtığı bir sunucu; bizim
  kullandığımız bir şey değil.

---

## 11. Sık karşılaşılan sorunlar

| Sorun | Neden ve çözüm |
|---|---|
| API açılırken çöküyor (access violation) | Python 3.13 kullanılıyor. Python 3.12 ile venv'i yeniden kurun |
| `Set LLM_MODEL in .env` | `.env`'de `LLM_MODEL` boş. Bölüm 3.4'e bakın |
| `Set TOKEN_FACTORY_BASE_URL and TOKEN_FACTORY_API_KEY in .env` | `.env` yok ya da anahtar boş |
| Gemma'dan 503 ya da çok yavaş cevap | Token Factory'de Gemma zaman zaman kesiliyor. Kod otomatik olarak DeepSeek'e geçer (bölüm 10) |
| 429 (Token Factory) | Dakikada 20 istek sınırı. Kod bekleyip tekrar deniyor |
| Canlı API ilk istekte cevap vermiyor | Railway uyuyor; 45 saniyeye kadar bekleyin |
| Ajan JSON dışında bir şey yazıyor (`unparseable JSON`) | 1) Ajanın **Advanced settings** sekmesinde **Interactive replies in chat (widgets)** ayarını kapatın, Save changes deyin. 2) Talimatın birebir yapıştırıldığını kontrol edin. 3) `evolus_error` içindeki "answer began" kısmına bakın. Kod ```json çitini zaten temizliyor |
| Dosyalar yanlış kütüphaneye yüklendi | Ajanın kişisel kütüphanesi değil, **OSHA 29 CFR 1910 (selected)** olmalı (İş 1'deki dikkat notu) |
| Kütüphane silinmiyor | Bir ajan kullanırken silinemez. Önce ajandan ayırın |
| Push sonrası canlı site bozuldu | main'e push, Railway ve Vercel'e otomatik yayın demek. Önceki commit'e dönüp push edin; push'tan önce `npm --prefix frontend run build` ve yerel API testi yapın |
| Windows konsolunda garip karakterler | Konsolun kodlaması yüzünden; sonucu etkilemez |

---

## 12. Claude Code ile devam etmek

- Depo klasörünü Claude Code'da açın ve ilk mesajda şunu yazın: "docs/DEVIR-NOTU.md dosyasını oku, İş N'den devam
  edelim."
- Claude'un **yapamadıkları:** hesap açmak, sitelere şifre ya da API anahtarı girmek, bilgisayarınızdan siteye
  dosya yüklemek. Bunları siz yaparsınız. API anahtarını Claude sohbetine yazmayın.
- Claude'un **yapabildikleri:** kod değişikliği, test ve build. Siz Claude uygulamasının tarayıcı panelinde
  Evolus'a giriş yaptıktan sonra, gizli bilgi içermeyen Evolus ayarları da (ajan, kütüphane, talimat) yapılabilir.
  16 Ekim'deki kurulum böyle yapıldı.
- Aysu'nun bilgisayarındaki Claude'un bu projeyle ilgili kalıcı notları var; sizin bilgisayarınızdakinde yok. Bu
  dosya o notların yerini tutuyor.

---

## 13. Hızlı başvuru

| Ne | Değer |
|---|---|
| Canlı arayüz | https://am-dhackathon.vercel.app (Vercel projesi `am-dhackathon`, kök klasör `frontend`, `VITE_API_URL` tanımlı) |
| Canlı API | https://amdhackathon-production.up.railway.app (Railway projesi `diplomatic-rejoicing`, port 8080, Serverless açık) |
| Otomatik yayın | main'e her push'ta hem Railway hem Vercel yeniden yayınlanır |
| GitHub | https://github.com/aysu-keskin/AMDhackathon (şu an gizli) |
| Token Factory adresi | https://developer.amd.com.cn/radeon/api/v1 |
| Evolus agent chat (varsayılan yol) | `POST https://api.evolus.ai/v1/chat/completions`, `Authorization: Bearer <anahtar>`, model `b727ec74-30fa-4028-a791-1ee16118cf34:b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1` |
| Evolus REST (`EVOLUS_ENDPOINT=ask`) | `POST https://api.evolus.ai/api/v1/agents/{agentId}/ask`, başlıklar `X-APIKEY` ve `X-Application-Id` |
| Evolus geliştirici rehberi | https://evolus.ai/en/developers |
| Evolus çalışma alanı | DarkSea28 (etkinlik kodu AMDACT3; deneme 16/11/2026'ya kadar, rehbere göre 15/11/2026 23:59 İtalya saati) |
| Evolus Application ID | `b727ec74-30fa-4028-a791-1ee16118cf34` |
| Evolus ajanı | Corrective Action Drafter, `b8f7164e-89b7-4b13-83d2-cbbdc3f2e1d1` |
| Evolus kütüphanesi | OSHA 29 CFR 1910 (selected), RAG |
| Yüklenecek dosyalar | `deploy/evolus/standards/` (36 dosya, yaklaşık 1 MB) |
| Ajan talimatı | `deploy/evolus/agent_instructions.md` (= `DRAFT_SYSTEM`) |
| Evolus testi | `python -m backend.core.evolus_check [press\|forklift\|conveyor\|fryer]` |
| İlgili commit'ler | `4631c7f` (Evolus dosyaları), `a9958bb` (Evolus taslağı ve yedek), `aaeed04` (`X-APIKEY` başlığı), ardından bu notun commit'i (belgelenmiş agent chat yolu, kontrol betiği) |
| Proje özeti ve plan | `docs/S-Is-Guvenligi-Olay-Asistani.md` |
