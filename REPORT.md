# TuringLab — Mini Rapor

**Öğrenci:** [Reyhan Sevda Aygün]  
**Ders:** Hesaplama Kuramı  
**Tarih:** 20 Mayıs 2026

---

## 1. Giriş

TuringLab, deterministic tek-şeritli Turing makinelerini (DTM) çalıştıran
bir Python kütüphanesidir. YAML formatında tanımlanan Turing makinelerini
okur, simüle eder ve her adımın kaydını tutar. Proje üç bölümden oluşur:
TM motoru (Bölüm 1), 4 TM tasarımı (Bölüm 2) ve bu rapor ile demo video
(Bölüm 3).

---

## 2. Mimari

Proje iki ana modülden oluşur:

**turinglab/tm_engine.py** — Dört sınıf içerir:

- `Tape`: Şeridi `dict[int, str]` (sparse) olarak tutar. Bu yapı seçildi
  çünkü Python'da `list[-1]` listenin sonunu döndürür — negatif indeks
  tuzağına düşmemek için sparse dict kullanıldı. Hem bellek verimli hem
  de sola sonsuz genişlemeye izin verir.

- `Configuration`: Tek bir adımın anlık durumunu tutar (state, tape, head).
  `dataclass` olarak tanımlandı — otomatik `__init__` ve `__repr__` sağlar.

- `RunResult`: `run()` fonksiyonunun döndürdüğü sonuç nesnesi. `accepted`,
  `reason`, `final_tape`, `steps` ve `history` alanlarını içerir.

- `SingleTapeTM`: Ana makine sınıfı. `from_yaml()` ile YAML'dan yüklenir,
  `run()` ile çalıştırılır. Geçiş fonksiyonu `dict[(state, symbol)]`
  yapısında tutulur — O(1) lookup sağlar.

**Önemli tasarım kararları:**
- Blank sembolü olarak `B` seçildi (görünür karakter, debug kolaylığı).
- Head < 0 durumu hata değil — sola sonsuz genişleme desteklenir.
- Timeout, no_transition, reject kenar durumları ayrı `reason` string'leri
  ile raporlanır.

---

## 3. Tasarlanan TM'ler

**TM-1 (unary_to_binary):** En zorlu tasarım. Her turda bir '1' işaretlenip
binary sayaç artırılıyor. Overflow durumu (tüm bitler 1'di) için 3 ekstra
durum gerekti. O(n²) karmaşıklık.

**TM-2 (binary_compare):** İki binary sayıyı '#' ayracıyla karşılaştırıyor.
MSB'den bit bit karşılaştırma yapılıyor. Eşit uzunluktaki sayılarda doğru
çalışıyor. O(n²) karmaşıklık.

**TM-3 (string_copy):** Dizgiyi kopyalayıp '#' ile ayırıyor. Her harf için
ayrı işaretleme sembolleri (Q, W) kullanıldı. O(n²) karmaşıklık.

**TM-4 (student_choice):** Parantez denge kontrolü. İç içe '()' çiftlerini
teker teker silerek çalışıyor. En az durumla (7) çözülen TM. O(n²) karmaşıklık.

En zor tasarım TM-1 oldu — overflow durumu birçok deneme gerektirdi.

---

## 4. Kavramsal Tartışma

**Soru (c): Modern bir programlama dili (Python) ile TM arasındaki "boşluk" nedir?**

Python ve Turing makinesi teorik olarak eşdeğer hesaplama gücüne sahiptir —
her ikisi de Turing-complete'tir. Ancak pratikte aralarında derin farklar var.

Python'da bir değişkene `x = 1011` yazmak tek bir işlem. Turing makinesinde
aynı sayıyı şeride yazmak için onlarca geçiş kuralı gerekiyor. Python'da
`+`, `-`, `//` gibi operatörler yerleşik — TM'de toplama bile ayrı bir makine
tasarımı gerektiriyor.

Bu "boşluğun" özü şu: Python yüksek seviyeli soyutlamalar sunar (değişkenler,
fonksiyonlar, veri yapıları), TM ise hesaplamayı en temel birimine — tek bir
sembol okuma/yazma — indirgemiştir. TuringLab'ı geliştirirken bu farkı somut
olarak hissettim: Python'da `binary_count += 1` yazmak yerine carry yayan
10 geçiş kuralı tasarlamak gerekti.

Ama bu "boşluk" aynı zamanda TM'nin gücünü gösteriyor: bu kadar basit bir
model, tüm modern yazılımların yapabildiği her şeyi yapabiliyor. Church-Turing
tezi bunu güvence altına alıyor.

---

## 5. Sınırlar ve İleri Çalışma

**Eksik kalanlar:**
- TM-2 farklı uzunluktaki sayıları karşılaştırmada sınırlı
- Görselleştirici yok — her adımı görsel olarak takip etmek zor
- Çok-şeritli TM desteği yok

**Bir hafta daha olsaydı:**
- Bonus A (Multi-tape TM) eklenirdi — TM-2 çok daha temiz olurdu
- Görselleştirici (PNG/GIF) eklenirdi
- TM-2 farklı uzunluklu sayılar için düzeltilirdi

---

## 6. Kaynakça

- Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.)
- Python Documentation: https://docs.python.org
- PyYAML Documentation: https://pyyaml.org/wiki/PyYAMLDocumentation
- Ders notları: Dr. Ali Çetinkaya, Selçuk Üniversitesi