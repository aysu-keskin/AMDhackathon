# S: Fabrikalar için İş Güvenliği Olay Asistanı

**AMD Developer Hackathon ACT III · Intelligent Industry parkuru**
**Ekip:** Aysu, Çağrı, İlhan · **Kaynak:** İlhan'ın Claude oturumu · **Hazırlanma:** 10 Ekim 2026
**Durum:** Öneri. Veri indirildi ve öldürme testi çalıştırıldı. Temel iddia, düzeltilmiş testte geçti (aşağıdaki sapma notunu okuyun). Yedek plan F.

---

## Kısa cevap

| Soru | Cevap |
| --- | --- |
| Hangi parkur? | **Intelligent Industry** |
| Hangi alan? | **İş güvenliği:** fabrikadaki kaza raporlarını standart kodlara çevirmek, benzer vakaları bulmak ve düzeltici faaliyet önermek |
| Hangi veri? | ABD İş Güvenliği İdaresi'nin (**OSHA**) ağır iş kazası raporları (Severe Injury Reports): 106 bin gerçek kaza anlatısı. Her birini OSHA kendisi kodlamış. Üçte biri imalat |
| Veri kolay mı? | Evet. Tek bir 15 MB zip, hesap açmadan iniyor. ABD devlet eseri, telif yok |
| Veri işe yarıyor mu? | Evet, ölçtük. Kaza anlatısından olay türü, eğitimde görülmemiş bir yılda %84,2 doğrulukla bulunuyor. Model en emin olduğu %70'te %93,6 doğru. Hatalar, modelin emin olmadığı %20'de yaklaşık 5 kat (4,98) daha sık |
| Dürüstlük notu | OSHA Ocak 2024'te kod sistemini değiştirmiş. Bu yüzden ön kayıtlı test geçersiz oldu ve düzeltilmiş bir testle yeniden ölçtük. Ayrıntı "Kanıtlar" bölümünde |

---

## Tek paragrafta

Bir fabrikanın İSG uzmanı için kaza ve olay raporu asistanı. Uzman olayı kendi cümleleriyle, istediği dilde yazıyor. Sistem raporu OSHA'nın kullandığı standart sınıflandırmaya (OIICS) çeviriyor: ne oldu (olay), neye bağlı (kaynak), yaralanma türü, vücut bölgesi. Her kodun yanında bir güven etiketi var, emin olmadığı kodu insana bırakıyor. Ardından 106 bin gerçek OSHA vakası arasından en benzerlerini getiriyor, eksik bilgiyi soruyor ve ilgili OSHA standartlarına dayanan bir düzeltici faaliyet taslağı hazırlıyor. AMD MI300X üzerinde çalışan bir LLM ajanı ve ince ayarlı bir kodlayıcı bu işi yapıyor. Uzman taslağı düzeltip onaylıyor.

**Ana iddiamız:** "Kazaları önceden biliyoruz" değil. İddiamız şu: **"Dağınık kaza anlatılarını, OSHA'nın kendi kodlarına karşı ölçülmüş bir doğrulukla karşılaştırılabilir veriye çeviriyoruz. Emin olmadığımız yeri biliyoruz ve orada kararı insana bırakıyoruz."**

---

## Takvim ve kurallar

| | |
| --- | --- |
| Kayıt | **12 Ekim Pazartesi 18:00 TR** (15:00 UTC), kickoff anında kapanıyor |
| Geliştirme | 12-18 Ekim, online |
| Teslim | **18 Ekim Pazar 18:00 TR** (15:00 UTC) |
| Kredi | Yeni üyeye 100 $ AMD kredisi |

- İş yükünün anlamlı bir kısmı AMD'de çalışmalı ve bu kısım jüriye gösterilen üründe görünmeli.
- Gönderim özgün ve MIT uyumlu olmalı.
- Parkur, gerçekçi endüstriyel veriden uyarı, açıklama, öneri ya da aksiyon üreten çalışan bir ürün istiyor. Kimin kullanacağı ve neyi iyileştirdiği açık olmalı.
- Kayıt fikirden bağımsız; parkur teslim formunda seçiliyor.
- **Jüri kriterleri:** Teknolojinin uygulanması, sunum, iş değeri, özgünlük.

---

## Neden S?

### Nasıl seçtik?

Çağrı'nın üç kuralı aynen uygulandı: geçme şartı veriye bakmadan yazıldı, sonuçtan sonra eşik değiştirilmedi, sapmalar açıkça yazıldı. Ön kayıt dosyası (`ON_KAYIT.md`) parmak izi ve saatiyle ayrıca paylaşılıyor.

### Taranan alanlar

| Alan | Veri durumu | Karar |
| --- | --- | --- |
| **İş güvenliği** (Industry) | OSHA raporları: 106 bin kayıt, OSHA kodlu, kamu malı, 15 MB | **Seçildi** |
| Görsel kusur tespiti (Industry) | Veri bol (ör. MVTec AD, ama ticari olmayan lisans) | Görüntü işleme gerekiyor ve en kalabalık fikirlerden biri |
| Enerji verimliliği (Industry) | ABD Enerji Bakanlığı fabrika denetim verisi var | "Doğru öneri" iddiası G ve H'deki gibi riskli |
| Sağlık | Gerçek hasta notları (ör. MIMIC) onaylı erişim istiyor; açık olanlar küçük ya da sentetik | Kayda kadar erişim garantisi yok, güvenlik kuralları katı |
| Ticaret | Veri bol, lisanslar karışık | C ve H testte elendi; destek botu çok kalabalık |
| Yeni tür deneyim | Veri gerekmiyor | Ölçülebilir bir iddia kurmak zor |

### Elenen fikirler

| Fikir | Neden elendi | Temel rakam |
| --- | --- | --- |
| **C:** Ajanlara hazır katalog | Katalog zaten düzenliydi | WANDS'te düzeltilebilir eksik %0,7 (eşik %20) |
| **A:** Kompresör bakım kopilotu | Sinyal gürültüden ayrılmıyor, 3 arıza var | Haftada 2,13 yanlış alarm |
| **G:** Çelik tesisi enerji koçu | Tahmin kıl payı yetersiz | İyileşme %19,9 (eşik %20) |
| **H:** Toptan yeniden sipariş | Basit kural neredeyse aynı iyi | İlk %10'da +4,4 puan (eşik +5) |
| **I:** Araç saha kalitesi erken uyarı | Uyarılar şanstan pek iyi değil, çok fazla | Yakalama %39,5 (eşik %50); isabet 1,10 kat |

### F ile karşılaştırma

| | F: Hidrolik triyaj | S: İş güvenliği olay asistanı |
| --- | --- | --- |
| Veri | Test düzeneği, 2.205 döngü, arızalar elle ayarlanmış | 106 bin gerçek kaza raporu, OSHA kodlu |
| Testin sonucu | 4 bileşenin 2'si geçti (şart 3'tü) | Temel iddia geçti (T1, T3, T4); kaynak kodu "yaklaşık" |
| Zayıf yanı | Fabrikada çalışır diyemiyoruz | Kod sistemi değişikliği yüzünden test düzeltildi; veri ABD'den |
| Kullanıcı | Bakım teknisyeni | İSG uzmanı, tesis müdürü |
| AMD iş yükü | Küçük bir CNN ve ajan | 70 bin metinde ince ayar, LLM ajanı, embedding, toplu kodlama |
| İş değeri | Teknisyeni doğru kontrole yönlendirmek | Raporu saniyeler içinde kodlamak, insanın yalnızca belirsiz %30'a bakması, düzeltici faaliyet taslağı |

**Önerimiz S.** Veri gerçek, büyük ve uzmanlarca etiketli; temel iddia ölçüldü. F hazır bir yedek olarak kalıyor. Karar ekibin.

### S'nin sınırları (saklamıyoruz)

- **Test düzeltildi.** Ön kayıtlı test, OSHA'nın Ocak 2024'teki kod sistemi değişikliği yüzünden geçersiz çıktı. Geçme kararı, sonuç görüldükten sonra tanımlanan düzeltilmiş teste dayanıyor. Bu, temiz bir ön kayıtlı geçişten daha zayıf bir kanıt.
- **T3 kıl payı geçti.** En emin %70'te doğruluk 0,9357; eşik 0,93. %95 güven aralığı 0,924-0,946.
- **Kaynak kodu zayıf.** Kaynakta doğruluk 0,6625 (şart 0,70, zorunlu değildi). Ürün kaynağı "yaklaşık" gösterir, insan seçer.
- **Yeni kod sistemiyle sınırlı veri var.** 2024'ten bu yana yaklaşık 18 bin kayıt var. Sadece 2024 ile eğitilen temel model, 2025'te olay türünde 0,806 doğruluk aldı, ama T3'te 0,923 ile eşiğin biraz altında kaldı.
- **Veri ABD'den ve yalnızca ağır kazaları içeriyor.** Türkiye'deki bir fabrikanın raporları farklı olabilir. Çok dilli giriş bunu kısmen kapatır, ama ölçülmedi.

---

## Veri

### 1. OSHA Severe Injury Reports (ana veri)

- **Ne:** 1 Ocak 2015'ten bu yana işverenlerin OSHA'ya bildirdiği ağır iş kazaları. Ampütasyon, hastaneye yatış ya da göz kaybı 24 saat içinde bildirilmek zorunda.
- **Kapsam:** Federal OSHA yetki alanı. Kendi planını uygulayan eyaletler dahil değil.
- **Dosya:** `January2015toNovember2025.zip` (15,47 MB). İçinde tek CSV: 57,4 MB, 105.996 satır, 28 sütun, UTF-8.
- **Lisans:** data.gov kaydına göre ABD devlet eseri ("U.S. Government Work"). Telif koruması yok. Veri repoya konmaz, indirme betiği verilir.
- **Kodlama:** OSHA, raporları kişisel bilgilerden arındırıp OIICS sınıflandırmasıyla kodluyor.

| Sütun grubu | İçerik |
| --- | --- |
| Kimlik ve yer | ID, işveren, adres, eyalet, enlem-boylam |
| Olay | Olay tarihi, birincil NAICS (sektör), hastaneye yatış, ampütasyon, göz kaybı, OSHA denetim numarası |
| Anlatı | **Final Narrative** (ortalama 199 karakter) |
| OSHA kodları | Nature (yaralanma türü), Part of Body (vücut bölgesi), Event (olay), Source (kaynak), Secondary Source, hepsi başlıklarıyla |

**Rakamlar (2015-Kasım 2025):**
- 105.993 kullanılabilir kayıt. Yılda 8.700-11.200 arası.
- **İmalat: 34.472 kayıt (%32,5).** İmalat kazalarının **%44,7'si ampütasyon.**
- İmalat kayıtlarının %46,7'sinde OSHA denetim numarası var (bütün kayıtlarda %33,5).
- En çok kayıt veren imalat alt sektörleri: gıda (311), metal ürünler (332), ulaşım araçları (336), makine (333), ana metal (331), ahşap (321).
- 2015-2023 imalat kayıtlarında olay türü dağılımı: **makineye ya da nesneye sıkışma/ezilme %46,0**, nesne çarpması %15,3, alt seviyeye düşme %8,2, aynı seviyede düşme %6,9, nesneye çarpma %4,7, sıcak madde/yüzey %4,5.

**Önemli bulgu: kod sistemi Ocak 2024'te değişti.** 2015-2023 arasında kodlar OIICS 2.01'e göre ve oranlar yıldan yıla sabit. Ocak 2024'ten itibaren yeni bir OIICS sürümü kullanılıyor ve aynı iki haneli numaralar başka anlamlara geliyor:

| Olay grubu numarası | 2023'teki payı | 2024'teki payı | Yeni sistemdeki anlamı (örnek başlık) |
| --- | --- | --- | --- |
| 65 | %0,2 | %23,7 | Çalışan makine parçasının çarpması |
| 41 | %0,3 | %17,9 | Alt seviyeye düşme |
| 62 | %17,7 | %0,9 | (eski sistemde nesne çarpması) |
| 42 | %12,5 | %1,0 | (eski sistemde aynı seviyede düşme) |

Ürün iki sistemi ayrı ele almalı. Gelecekteki veriler yeni sistemde geleceği için asıl model yeni sistemle eğitilmeli.

### 2. OSHA ITA vaka verisi (demo ve sektör kıyası için)

- 100 ve daha fazla çalışanı olan, yüksek riskli sektörlerdeki işyerlerinin kaza defterleri (Form 300/301). 2023, 2024 ve 2025 dosyaları var.
- Her vakada Form 300 ve 301'den gelen anlatı alanları var: yer, olay açıklaması, olaydan hemen önce ne yapıldığı, ne olduğu, yaralanma ve zarar veren nesne. Kişisel bilgiler OSHA tarafından ayıklanmış.
- İşyeri bazında toplam çalışma saati de var. Bu sayede "100 tam zamanlı çalışan başına" oranla sektör kıyası yapılabilir.
- 2023-2024 dosyalarındaki OIICS kodları uzman kodu değil, BLS'nin otomatik kodlayıcısından geliyor ve yalnızca iki haneli. Bu yüzden değerlendirmede değil, demoda ve kıyasta kullanılır.
- Dosyalar büyük. Hackathon'da AMD makinesinin hızlı bağlantısıyla indirilecek.

### 3. OSHA standartları (ajanın bilgi kaynağı)

- 29 CFR 1910 (genel sanayi). Örnek: makine koruyucuları (1910.212), kilitleme/etiketleme (1910.147), mekanik presler (1910.217), forkliftler (1910.178), kişisel koruyucu donanım (1910.132).
- ABD federal düzenlemesi, kamuya açık metin. Ajan bu metinden numaralı alıntı yapar.

### 4. OSHA ihlal kayıtları (hackathon'da değerlendirme için, henüz denenmedi)

- ABD Çalışma Bakanlığı'nın denetim verisinde, her denetimde hangi standarttan ceza kesildiği yazıyor. SIR'deki denetim numarasıyla birleştirilebilir.
- Bununla "ajanın önerdiği standartlar, OSHA'nın gerçekte ceza kestiği standartlarla örtüşüyor mu?" ölçülebilir. Birleştirmenin çalıştığı henüz doğrulanmadı.

---

## Kanıtlar

### Test düzeni

- **Görev:** Anlatıdan dört kodu (olay, kaynak, yaralanma türü, vücut bölgesi) iki hane düzeyinde bulmak.
- **Model:** Kelime ve ikili kelime özellikleri (TF-IDF) + lojistik regresyon. Bilerek basit seçildi; bu bir alt sınır.
- **Bölme:** Zamana göre. Eğitim 2015-2021, test sonraki yıllar. Model, test yıllarındaki hiçbir kaydı görmedi.
- **Ölçüm:** İmalat test kümesinde.
- **Doğrulama:** Tarayıcıda çalışan model önce başka bir veride (AG News) scikit-learn ile karşılaştırıldı: doğruluk 0,902'ye karşı 0,904, en emin %70'te 0,971'e karşı 0,972.

### Ön kayıtlı test: geçersiz

Test 2023-Kasım 2025'te çalıştırıldı. İmalatta olay türü doğruluğu **0,374** çıktı. İnceleyince sebep görüldü: test penceresinin 35 ayından 23'ü yeni kod sisteminde. Eski sistemle eğitilen modelin cevapları yeni sistemin numaralarıyla karşılaştırılıyordu. Bu bir model başarısızlığı değil, karşılaştırılamaz etiketler. Test ne geçti ne kaldı: **geçersiz**.

### Düzeltilmiş test (ön kayıttan sapma)

Aynı eğitim, aynı model, aynı eşikler. Test yalnızca **2023** (eski sistemin son yılı; imalatta 2.911 kayıt). Bu sapma, düzeltilmiş testin sonucu görülmeden önce yazılıp kaydedildi.

| Kod | Ölçü | Eşik | Sonuç | |
| --- | --- | --- | --- | --- |
| T1 | Olay türü doğruluğu | ≥ 0,80 | **0,842** | ✅ |
| T2 | Kaynak doğruluğu | ≥ 0,70 | **0,6625** | ❌ (zorunlu değil) |
| T3 | En emin %70'te olay türü doğruluğu | ≥ 0,93 | **0,9357** | ✅ (kıl payı) |
| T4 | Az emin %20'deki hata oranı / kalan %80'deki | ≥ 3 | **4,98** (%43,8'e karşı %8,8) | ✅ |
| T5 | Etiketler gizliyken Claude'un olay türü uyumu | ≥ 0,80 | **0,829** (41 kayıtta 34) | ✅ (küçük örneklem) |
| Veri kapıları | Test büyüklüğü ve sınıflandırılabilir kod oranı | ≥ 1.000 ve ≥ %90 | 2.911; en düşük %91,6 | ✅ |

**Karar kuralına göre (T1, T3, T4 ve veri kapıları): geçti.**

Diğer kodlar, aynı testte (imalat):

| Kod | Doğruluk | En emin %70'te | Hata oranları oranı |
| --- | --- | --- | --- |
| Yaralanma türü (Nature) | 0,926 | 0,995 | 25,9 |
| Vücut bölgesi (Part) | 0,8875 | 0,987 | 13,7 |
| Kaynak (Source) | 0,6625 | 0,787 | 2,6 |

Olay türünde sınıf bazında (imalat, en sık gruplar): sıkışma/ezilme 0,949 (1.285 kayıt), nesne çarpması 0,808, alt seviyeye düşme 0,935, aynı seviyede düşme 0,847, sıcak madde 0,860. **Zayıf nokta:** "nesneye çarpma" 0,455 (çoğu çalışan makine parçasına temas) ve "belirtilmemiş temas" 0,019.

### T5: LLM eğitim verisi olmadan ne kadar iyi?

- Rastgele 100 imalat anlatısı etiketler gizliyken kodlandı. Cevaplar etiketler görülmeden kaydedildi. Bu 100 kaydın 41'i 2023'e düşüyor ve yalnızca onlar puanlanabildi.
- **Claude: 41'de 34 (0,829, %95 güven aralığı 0,69-0,92).** Aynı 41 kayıtta temel model de 34 doğru buldu.
- Claude'un 7 hatasının çoğu OIICS kurallarından geliyor. Örneğin OSHA, sabit testereye eli kaptırmayı "sıkışma" değil "çalışan makine parçasına çarpma" olarak kodluyor. Ürün bu yüzden LLM'e benzer kodlu OSHA vakalarını örnek olarak verecek.
- İki yöntem farklı kayıtlarda hata yaptı. Birlikte kullanmak umut verici, ama ölçülmedi.
- Hackathon'da kullanılacak açık model Claude'dan zayıf olabilir. Bu sonuç bir üst tahmindir; açık model kickoff'ta ölçülecek.

### Keşif: yeni kod sistemi (karara etkisiz)

Sadece 2024 verisiyle (9.034 kayıt) aynı ayarlarla eğitilen model, 2025 Ocak-Kasım'da (imalat 2.625 kayıt):

| Kod | Doğruluk | En emin %70'te | Hata oranları oranı |
| --- | --- | --- | --- |
| Olay türü | 0,806 | 0,923 | 4,61 |
| Yaralanma türü | 0,871 | 0,973 | 8,0 |
| Vücut bölgesi | 0,786 | 0,947 | 6,9 |
| Kaynak | 0,584 | 0,728 | 2,4 |

Yeni sistem de öğrenilebiliyor. Ama tek yıllık veriyle olay türü T3'ü (0,93) biraz kaçırıyor. AMD'de eğitilecek model bu açığı kapatmalı.

---

## Ürünün kapsamı: sistem ne söyler, ne söylemez

| Alan | Sistemin davranışı | Dayanağı |
| --- | --- | --- |
| **Olay türü** | Kodu söyler; güven etiketiyle | 2023 testinde 0,842; en emin %70'te 0,9357 |
| **Yaralanma türü** | Kodu söyler | 0,926 |
| **Vücut bölgesi** | Kodu söyler | 0,8875 |
| **Kaynak** | "Yaklaşık" gösterir, ilk üç seçeneği sunar, insan seçer | 0,6625 |
| **Kök neden** | Hüküm vermez. Eksik bilgiyi sorar, benzer vakaları gösterir | Veride doğrulanmış kök neden etiketi yok |
| **Mevzuat** | "Şu standart ilgili olabilir" der, "ihlal var" demez | Hukuki hüküm sistemin işi değil |
| **Tıbbi konu** | Teşhis ya da tedavi önermez | — |

**Güven etiketi:**
- **Güvenilir:** Olay türü, yaralanma türü, vücut bölgesi; model o tahminde de emin olmalı. Sınır eğitim verisinde belirlenir.
- **Yaklaşık:** Kaynak, ya da modelin emin olmadığı durumlar.
- **İnsana bırakıldı:** Az emin %20 (hatalar burada yaklaşık 5 kat daha sık). İlk kullanımlarda bütün kayıtlar insan onayından geçer.

---

## Kullanıcı ve akış

**Kullanıcı:** Fabrikanın İSG uzmanı ve tesis müdürü.

1. **Rapor girişi.** Uzman olayı serbest metinle yazar ya da formu yükler. Örnek (Türkçe): "Pres operatörü kalıba sıkışan parçayı elle almaya çalışırken pres çalıştı, sağ işaret parmağının ucu koptu."
2. **Kodlar.** Sistem dört kodu ve güven etiketlerini gösterir: olay "çalışan makineye sıkışma" (güvenilir), yaralanma "ampütasyon" (güvenilir), vücut bölgesi "parmak" (güvenilir), kaynak "metal işleme makinesi" (yaklaşık).
3. **Benzer vakalar.** OSHA'nın 106 bin vakası içinden en benzer beşi, OSHA kodlarıyla.
4. **Eksik bilgi.** Ajan sorar: "Pres kilitlenmiş miydi? Işık perdesi ya da iki el kumandası var mıydı?"
5. **Düzeltici faaliyet taslağı.** Kontrol hiyerarşisine göre: mühendislik önlemi (koruyucu, ışık perdesi), idari önlem (kilitleme/etiketleme prosedürü), eğitim. Her öneri, numarasıyla bir OSHA standardına dayanır (ör. 1910.212, 1910.217, 1910.147).
6. **Onay.** Uzman düzeltir ve onaylar. Kayıt tesis paneline geçer.
7. **Tesis paneli.** Tesisin kaza profili ve aynı sektördeki işyerleriyle kıyas (ITA verisi). Örnek: "Bu tesiste el yaralanmaları sektör ortalamasının üstünde."

---

## Mimari

```
Olay raporu (serbest metin, herhangi bir dil; form, e-posta ya da PDF)
   │
   ▼
1. Alım ── LLM (vLLM, MI300X): dili algılar, İngilizce özet çıkarır, eksik alanları işaretler
   │
   ▼
2. Kodlayıcı ── olay, kaynak, yaralanma türü, vücut bölgesi + olasılıklar
   ├─ TF-IDF + lojistik regresyon: kanıtı olan temel model (CPU)
   └─ ince ayarlı çok dilli kodlayıcı (PyTorch + ROCm, MI300X)
      (ürüne ancak önceden yazılmış kuralı geçerse girer)
   │
   ▼
3. Güven katmanı ── güvenilir / yaklaşık / insana bırakıldı (eşikler eğitim verisinden)
   │
   ▼
4. Benzer vakalar ── bge-m3 embedding (MI300X), OSHA vakaları arasında en yakın 5'i
   │
   ▼
5. Kanıt paketi (JSON) ── kodlar, olasılıklar, benzer vakalar, sektör kıyası
   │
   ▼
6. Ajan (vLLM, MI300X) ──► araçlar: benzer vaka ara │ standart ara │ sektör kıyası │ faaliyet taslağı
   │
   ▼
7. Doğrulayıcı ── her standart numarası indekste var mı? her sayı pakette mi?
   │               "ihlal var", teşhis ya da tedavi cümlesi var mı? (varsa reddet)
   ▼
8. Arayüz ── rapor girişi, kod kartları, benzer vakalar, faaliyet planı, onayla/düzelt,
              tesis paneli, ölçüm sayfası, AMD çalışma kaydı
```

### Katmanlar

- **Alım.** Türkçe ya da İtalyanca raporu İngilizce özete çevirir. Kodlayıcı hem özgün metni hem özeti görür. Eksik alanlar (makine, iş, yer) işaretlenir.
- **Kodlayıcı.** Temel model testteki modeldir. İnce ayarlı çok dilli kodlayıcı (ör. XLM-RoBERTa ailesi) dört kodu tek ağda öğrenir. Mimari ve eğitim ayarları eğitimden önce sabitlenir. Eski ve yeni kod sistemleri için ayrı çıkış başlıkları olur.
- **Güven katmanı.** Sabit kurallarla çalışır, LLM'in o anki fikrine bırakılmaz.
- **Benzer vakalar.** Hem kullanıcıya kanıt hem LLM'e örnek. T5 hatalarının çoğu OIICS kurallarından geldiği için bu, LLM'i kurallara alıştırmanın en ucuz yolu.
- **Ajan.** Sabit bir araç döngüsü. Araçlar:

| Araç | Yaptığı |
| --- | --- |
| Benzer vaka ara | OSHA vakalarında embedding araması yapar, kodlarıyla birlikte döner |
| Standart ara | 29 CFR 1910 metninde BM25 + embedding araması yapar, numaralı alıntı döner |
| Sektör kıyası | NAICS koduna göre ITA verisinden oran ve dağılım getirir |
| Faaliyet taslağı | Kontrol hiyerarşisine göre adımlar, sorumlu, termin ve ilgili standart |

- **Doğrulayıcı.** Ajanın uyduramayacağı yerler sabittir: standart numaraları indekste, sayılar kanıt paketinde olmalı. Hukuki hüküm ve tıbbi tavsiye cümleleri reddedilir.
- **Arayüz.** Streamlit ya da basit bir web arayüzü.

---

## AMD'de ne çalışıyor?

| İş | Nerede | Üründe nasıl görünüyor |
| --- | --- | --- |
| Çok dilli kodlayıcının ince ayarı (70 bin + 18 bin anlatı) | MI300X, PyTorch + ROCm | Ölçüm sayfası, AMD çalışma kaydı |
| Kodlayıcı çıkarımı | MI300X | Her raporda dört kod |
| LLM ajanı | MI300X, vLLM | Alım, sorular, faaliyet taslağı |
| Embedding (vakalar ve standartlar) | MI300X | Benzer vakalar, kaynaklı öneriler |
| Toplu kodlama (ITA anlatıları) | MI300X | Tesis paneli ve verim ölçümü (saniyede rapor, 1.000 rapor başına maliyet) |

**Kredi planı (kabaca):** Toplam yaklaşık 30 saat; önceki belgelerdeki hesapla 100 $ kredi yaklaşık 50 saat ediyor.
- Geliştirme küçük modelle ya da yerelde yapılır. GPU eğitim, toplu işler, entegrasyon ve çekim için açılır.
- **Makine kapalıyken de ücret işler. İş bitince silinmeli.**
- vLLM uç noktası `--api-key` ile korunur. Anahtarlar ortam değişkeninde tutulur, repoya girmez.

---

## Hackathon içindeki değerlendirme planı

Bütün kurallar kickoff'tan önce kesinleşir.

- **Bölme:** Her zaman zamana göre. Eski sistem: eğitim 2015-2021, test 2023. Yeni sistem: eğitim 2024, test 2025. Rastgele bölme yalnızca "sızıntı neden yanıltır" karşılaştırması için gösterilir.
- **İnce ayarlı kodlayıcı için tek ve kontrollü test. Önerilen kural:**
  - Olay türü ve kaynakta, iki test kümesinde de temel modeli en az **+0,03** doğrulukla geçmeli.
  - Yeni sistemin test kümesinde (2025) olay türü için T1, T3 ve T4 eşiklerini geçmeli. Temel model burada T3'ü 0,923 ile kaçırdı.
  - Hepsi sağlanırsa ürüne ince ayarlı model girer, sağlanmazsa temel model kalır.
  - Test bir kez çalıştırılır. Beğenilmezse ayar değiştirilip tekrar denenmez.
- **Açık LLM'in sıfırdan kodlaması:** Yeni sistemden 200 rastgele anlatı, benzer vaka örnekleriyle. Uyum oranı raporlanır.
- **Standart önerilerinin ölçümü (veri birleşirse):** OSHA'nın denetlediği vakalarda, ajanın ilk üç önerisinden en az biri OSHA'nın ceza kestiği standartlar arasında mı? Eşik kickoff'tan önce yazılır.
- **Çok dilli kontrol:** 100 test anlatısı ayrı bir modelle Türkçeye çevrilir, kodların değişip değişmediğine bakılır. Sentetik olduğu açıkça yazılır.

---

## Gereksinim kontrolü

| Gereksinim | Nasıl karşılanıyor |
| --- | --- |
| Parkur: "Help factories spot problems earlier and operate better" | Dağınık raporları karşılaştırılabilir veriye çevirmek; tesis panelinde tekrar eden tehlikeleri görmek |
| Parkurun amacı: güvenlik | Ağır iş kazaları ve düzeltici faaliyet |
| Parkurun fikir listesi | "Monitor safety conditions", "Explain production anomalies", "Recommend ... actions" |
| Gerçekçi endüstriyel veriden uyarı, açıklama, öneri, aksiyon | Gerçek OSHA raporları → kodlar ve güven → benzer vakalar → kaynaklı faaliyet taslağı → onay |
| Sadece dashboard değil, çalışan ürün | Rapor girişinden onaya kadar akış |
| Ölçülebilir iyileşme | OSHA kodlarına karşı doğruluk; insanın bakması gereken rapor oranı; rapor başına süre |
| AMD'nin anlamlı ve görünür kullanımı | İnce ayar, LLM, embedding ve toplu kodlama MI300X'te; çalışma kaydı arayüzde |
| Özgün ve MIT uyumlu | Kendi kodumuz, MIT lisanslı repo; veri ABD devlet eseri, indirme betiğiyle |

| Jüri kriteri | Güçlü yanımız |
| --- | --- |
| Teknolojinin uygulanması | AMD'de ince ayar, araç kullanan ajan, kaynaklı arama, doğrulayıcı |
| Sunum | Bir rapordan onaylı faaliyet planına 2 dakikalık akış |
| İş değeri | İmalattaki ağır kazaların %44,7'si ampütasyon; raporu saniyeler içinde kodlamak, insanı belirsiz vakalara yönlendirmek |
| Özgünlük | Metinden güvenlik zekâsı (alan genelde kamera tabanlı); "neyi bilmediğini bilen" tasarım; kod sistemi değişikliğini yakalayan dürüst ölçüm |

**İsteğe bağlı: Evolus ödülü.** Olay raporu alımı, Evolus'un örnek kullanım biçimine uyuyor: e-posta ya da PDF olarak gelen rapor → belge çıkarıcı → AMD'deki kendi modelimiz → bilgi kütüphanesindeki standartlar → belirsizse insana devir. Şartlar: Evolus etkinlik çalışma alanı, ana ajanın AMD'deki kendi vLLM uç noktamızda çalışması, en az iki Evolus yapı taşı, Evolus API'si, konteynerli uygulama. Ek iş getirdiği için ancak Salı akşamı plan önündeyse girilir.

---

## Sunum

**Söyleyeceklerimiz:**
- "OSHA'nın 106 bin gerçek ağır kaza raporuyla çalışıyoruz. Her birini OSHA kodlamış; doğruluğumuzu bu kodlara karşı ölçtük."
- "Sistem emin olmadığı raporları biliyor. Hataların çoğu orada, ve oraya insan bakıyor."
- "Ölçerken OSHA'nın 2024'te kod sistemini değiştirdiğini yakaladık. Bu yüzden ürün iki sistemi ayrı tanıyor."

**Söylemeyeceklerimiz:**
- "Kazaları önceden tahmin ediyoruz."
- "İhlal tespit ediyoruz" ya da "yasal uyumu garanti ediyoruz."
- "Türkiye'deki fabrikalarda kanıtlandı." Veri ABD'den.
- "Şu kadar kazayı önler." Veride buna dair bilgi yok.

**Demo senaryosu (2-3 dakika):**
1. **Problem (20 sn):** "2015-2023 arasında OSHA'ya bildirilen ağır imalat kazalarının %46'sı makineye ya da nesneye sıkışma. Raporlar serbest metin; kimse onları karşılaştırılabilir hale getirecek zamanı bulamıyor."
2. **Rapor (40 sn):** Türkçe bir pres kazası raporu girilir. Kodlar ve güven etiketleri gelir. Kaynak "yaklaşık" görünür, uzman seçer.
3. **Kanıt ve öneri (50 sn):** Benzer 5 OSHA vakası. Ajan eksik bilgiyi sorar, standart numaralarıyla faaliyet taslağı hazırlar. Uzman düzeltip onaylar.
4. **Tesis paneli (20 sn):** Sektör kıyası.
5. **Dürüst ölçüm (30 sn):** Ölçüm sayfasında zamana göre bölünmüş test, güven etiketi sonuçları, kod sistemi değişikliğinin grafiği ve AMD çalışma kaydı.

---

## Yol haritası

### Kickoff öncesi (10-12 Ekim)

| İş | Ne zamana kadar |
| --- | --- |
| Bu belgeyi ekiple okumak; S mi F mi kararı | 11 Ekim |
| Üçümüz AMD AI Developer Program'a katılıyoruz, krediyi kontrol ediyoruz | 11 Ekim |
| 1 saatlik vLLM denemesi: model açma, araç çağrısı, makineyi silme | 11 Ekim |
| İnce ayarlı kodlayıcı kuralını ve diğer değerlendirme eşiklerini kesinleştirmek | 11 Ekim |
| BLS'nin yeni OIICS kod listesini indirmek (eski ve yeni sistem başlıkları için) | 11 Ekim |
| **Kayıt** | **12 Ekim, 18:00'den önce** |

### Geliştirme haftası (12-18 Ekim)

| Gün | İş | Geçiş koşulu |
| --- | --- | --- |
| **Pzt 12 akşam** | Kickoff, kuralların ve Evolus belgelerinin kontrolü, repo iskeleti, AMD makinesinin denenmesi | Repo ve uç nokta hazır |
| **Sal 13** | Veri hattı (SIR + ITA + standartlar); temel modelin ürün koduyla yeniden üretilmesi; arayüz iskeleti; vLLM uç noktası | Testteki rakamlar yeniden üretildi |
| **Çar 14** | **Kodlayıcının MI300X'te tek kontrollü ince ayarı**; embedding indeksleri; ajan araçları | Kodlayıcı kararı verildi |
| **Per 15** | Güven katmanı; kanıt paketi; doğrulayıcı; uçtan uca bir senaryo; açık LLM'in sıfırdan kodlama ölçümü | Bir rapordan onaylı plana akış çalışıyor |
| **Cum 16** | Arayüzün tamamı; tesis paneli; ölçüm sayfası; AMD çalışma kaydı | Demo baştan sona çalışıyor |
| **Cmt 17** | Öğlen özellik dondurma; kayıttan oynatma modu; canlı modda video; sunum; README | Video çekildi |
| **Paz 18** | Tampon; teslim **15:00 gibi** (son saat 18:00) | Teslim edildi |

### Karar noktaları
- **11 Ekim:** S mi F mi.
- **Çarşamba gecesi:** İnce ayarlı kodlayıcı kuralı geçmezse temel model kalır. Sonuç ölçüm sayfasında dürüstçe gösterilir.
- **Perşembe akşamı:** İhlal verisiyle birleştirme çalışmazsa standart önerileri yalnızca kaynaklı alıntıyla sunulur, ölçüm iddiası yapılmaz.
- **Perşembe akşamı:** Araç çağırma kararsızsa sorular sabit bir forma bağlanır, LLM yalnızca özet ve taslak yazar.

### İş bölümü (üç kol)

| Kol | İçerik |
| --- | --- |
| **1. Veri ve model** | Veri hattı, iki kod sistemi, temel model, ince ayarlı kodlayıcı (ROCm), güven katmanı, ölçüm sayfası |
| **2. Ajan ve bilgi** | vLLM, alım, embedding indeksleri, standart araması, ajan araçları, doğrulayıcı |
| **3. Uygulama, altyapı, sunum** | Arayüz, tesis paneli, kayıttan oynatma, AMD makine yönetimi, video, sunum, README |

İlhan'ın daha önce bge-m3 ile kurduğu RAG asistanı, ikinci kolun büyük kısmına doğrudan benziyor. Kimin hangi kolu alacağı ekip içinde konuşulacak.

---

## Riskler ve önlemler

| Risk | Önlem |
| --- | --- |
| Kod sistemi değişikliği | İki sistem için ayrı çıkış başlıkları; asıl model yeni sistemde; ölçüm sayfasında açıkça gösterilir |
| Kaynak kodu zayıf | "Yaklaşık" etiketi ve ilk üç seçenek; insan seçer |
| Yeni sistemde veri az | 2024 ve 2025'i birlikte kullanmak; ince ayarlı model; benzer vaka örnekleriyle LLM |
| Açık LLM, Claude'dan zayıf kodlar | Kodlayıcı ana yol; LLM özet, soru ve taslak için |
| Jüri "BLS'nin zaten otomatik kodlayıcısı var" der | Baştan söyleriz. Bizim ürünümüz fabrika tarafında: rapor girişi, güven, benzer vakalar, faaliyet planı, onay |
| Jüri "bu bir sınıflandırıcı" der | Ajan, kaynaklı öneriler, sektör kıyası ve onay akışı demoda görünür |
| Ajan standart uydurur | Doğrulayıcı indekste olmayan numarayı reddeder |
| Hukuki ya da tıbbi tavsiye riski | "İlgili olabilir" dili; doğrulayıcı hüküm cümlelerini reddeder; her şey insan onayından geçer |
| Kişisel veri | Anlatılarda işçi adı yok; işveren adları demoda gösterilmez; ITA anlatıları OSHA'ca ayıklanmış |
| GPU kredisi biter | Küçük modelle geliştirme; toplu işler bir kez; makine iş bitince silinir; kayıttan oynatma yedekte |

## Kapsam dışı

Kamera ile denetim, gerçek zamanlı sensör, kaza tahmini, hukuki uyum denetimi, gerçek bir İSG yazılımıyla entegrasyon, mobil uygulama.

## Açık kararlar (ekip)

1. S mi F mi.
2. İnce ayarlı kodlayıcı kuralının kesinleşmesi (önerisi yukarıda).
3. LLM modelinin seçimi (araç çağırma ve JSON şemalı çıktı şart).
4. Evolus ödülüne girilip girilmeyeceği.
5. Kol dağılımı.
6. Ürün adı.

---

## Veri doğrulama raporu

10 Ekim 2026'da yapılan kontroller:

| Kontrol | Sonuç |
| --- | --- |
| Dosya yayında mı? | **Evet.** OSHA'nın SIR sayfasında `January2015toNovember2025.zip` bağlantısı var |
| İndirildi mi? | **Evet.** 15,47 MB, tek denemede, 6 saniyede |
| İçerik | Tek CSV: 57,4 MB, 105.996 satır, 28 sütun, UTF-8; bozuk satır yok |
| Tarih aralığı | 2015-2025 (Kasım 2025'e kadar) |
| Anlatı | 3 satır dışında hepsi en az 20 karakter; ortalama 199 karakter |
| Kodların biçimi | Hiyerarşik, başında sıfır yok; iki haneli grup ilk iki haneden okunuyor |
| Sınıflandırılabilir kod oranı | Olay %99,2, kaynak %97,1, yaralanma türü %99,97, vücut bölgesi %91,6 |
| Kod sistemi | 2015-2023 sabit; **Ocak 2024'te değişiyor** (aylık dağılımla görüldü) |
| Lisans | data.gov kaydı: ABD devlet eseri |
| ITA vaka verisi | Sayfası ve veri sözlüğü incelendi: beş anlatı alanı; 2023-2024 kodları BLS otomatik kodlayıcısından, iki haneli. **Dosyalar indirilmedi** |
| Test kodu | Önce başka bir veride scikit-learn ile karşılaştırıldı; ön kayıt ve cevap dosyalarının parmak izleri saatleriyle kaydedildi |

**Doğrulanamayanlar:**
- ITA dosyalarının boyutu ve kodlarının hangi OIICS sürümünde olduğu.
- BLS'nin eski ve yeni OIICS sistemleri arasında resmî bir eşleme tablosu yayımlayıp yayımlamadığı.
- İhlal verisiyle SIR denetim numaralarının birleşmesi.
- Açık modelin (Qwen vb.) sıfırdan kodlama başarısı.

**Tekrar üretmek için:** `sir.js` ve `sir_run.js` (tarayıcıda ya da Node'da çalışır), `ON_KAYIT.md` (ön kayıt ve sapmalar), `t5_cevaplar.json` (etiketler görülmeden verilen cevaplar), `sonuclar.json` (bütün rakamlar). Kod, osha.gov'da açılmış bir tarayıcı sekmesinde çalıştırıldı; dosya diske yazılmadan bellekte işlendi.

---

## Kaynaklar

- [AMD Developer Hackathon ACT III](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii) ve [canlı sayfa](https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii/live)
- [OSHA Severe Injury Reports](https://www.osha.gov/severeinjury) ve [SIR panosu, indirme bağlantısı](https://www.osha.gov/severe-injury-reports)
- [data.gov: Severe Injury Report (SIR) Data](https://catalog.data.gov/dataset/severe-injury-report-sir-data-68a35)
- [OSHA: Severe Injury Report, yedi yıllık değerlendirme (2015-2021)](https://www.osha.gov/sites/default/files/severe-injury-report-2015to2021.pdf)
- [OSHA ITA işyeri verisi](https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data) ve [vaka verisi sözlüğü](https://www.osha.gov/sites/default/files/case_detail_data_dictionary.pdf)
- [BLS OIICS kılavuzu ve kod listeleri](https://www.bls.gov/iif/definitions/occupational-injuries-and-illnesses-classification-manual.htm), [Olay kodları (2.01)](https://www.bls.gov/iif/definitions/oiics-manual-2010-section-3-4.pdf)
- [The Oregonian: OSHA denetim ve ihlal verisi işleme](https://github.com/TheOregonian/osha) (ihlal dosyasındaki "standard" sütunu)
- [lablab: AMD Developer Cloud'da vLLM](https://lablab.ai/ai-tutorials/amd-developer-cloud-host-llm-vllm)
- Ekip belgeleri: `F-Hidrolik-Saglik-Triyaji.md`, `I-Saha-Kalitesi-Erken-Uyari.md`
