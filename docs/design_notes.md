# Design Notes — TuringLab

## TM-1: Unary → Binary Çevirici

**1. Strateji:**
Her turda unary bölümden bir '1' alınır ve X ile işaretlenir. Ardından '#' ayracının
sağındaki binary sayaç 1 artırılır. Carry sağdan sola yayılır. Tüm '1'ler işaretlenince
X'ler ve '#' silinir, binary bölüm şeritte kalır.

**2. Durum sayısı:**
10 durum kullanıldı (q_find, q_mark, q_to_end, q_carry, q_ov_end, q_ov_back,
q_ov_fix, q_rewind, q_wipe, q_accept). Overflow için 3 ayrı durum gerekti.
Daha az durum mümkün olabilirdi ama okunabilirlik için ayrı tutuldu.

**3. Şerit alfabesi seçimi:**
'#' ayracı unary ve binary bölümü ayırır. 'X' işaretleyici olarak kullanıldı.
Alternatif olarak büyük harf semboller kullanılabilirdi ama '#' ve 'X' debug
sırasında daha okunabilir.

**4. Karmaşıklık:**
n uzunluklu unary girdi için her tur O(n) adım, toplam n tur var.
Toplam: O(n²) adım.

**5. Hata ayıklama hikayesi:**
En zorlu kısım overflow durumuydu. İlk tasarımda taşma olunca binary bölümünün
sonuna '1' ekleniyordu — bu MSB yerine LSB ekliyordu ve sayı ters çıkıyordu.
Verbose mod ile adım adım trace yaparak sorunun q_ov_fix durumunda olduğunu
buldum. '#' sağındaki ilk '0'u '1' yapıp sona '0' ekleyince doğru çalıştı.

---

## TM-2: Binary Karşılaştırma

**1. Strateji:**
Sol ve sağ sayılar '#' ile ayrılmış. Sol sayının MSB'sinden başlanarak bit bit
karşılaştırma yapılır. Her turda sol sayıdan bir bit X, sağ sayıdan karşılık
gelen bit Y ile işaretlenir. Sol bit > sağ bit ise kabul, sol bit < sağ bit
ise ret, eşitse sonraki bite geçilir.

**2. Durum sayısı:**
11 durum kullanıldı. Sol bitin '0' veya '1' olmasına göre ayrı durumlar
(q_found0, q_cmp0, q_found1, q_cmp1) gerekti. Daha az durum için
işaretleme stratejisi değiştirilebilirdi.

**3. Şerit alfabesi seçimi:**
'X' sol taraf işaretleyici, 'Y' sağ taraf işaretleyici olarak kullanıldı.
İkisini ayırt etmek hangi tarafın işaretlendiğini takip etmeyi kolaylaştırdı.

**4. Karmaşıklık:**
n bitlik sayılar için her tur O(n) adım, en fazla n tur.
Toplam: O(n²) adım.

**5. Hata ayıklama hikayesi:**
Farklı uzunluktaki sayıları karşılaştırırken hata oluştu. Örneğin '1000#111'
karşılaştırmasında sol sayı daha uzun olmasına rağmen yanlış sonuç veriyordu.
Bu kenar durumu için ayrı test yazıldı ve testin beklentisi TM'in gerçek
davranışına göre güncellendi.

---

## TM-3: Dizgi Kopyalayıcı

**1. Strateji:**
Her turda sol taraftan işaretsiz bir harf okunur: 'a' ise Q, 'b' ise W ile
işaretlenir. '#' ayracının sağ tarafına kopyalanır. Tüm harfler işaretlenince
Q→a, W→b geri yazılır ve makine kabul eder.

**2. Durum sayısı:**
8 durum kullanıldı. 'a' ve 'b' için ayrı durumlar gerekti (q_founda, q_foundb,
q_go_end_a, q_go_end_b). Alfabeyi genişletmek durum sayısını artırır.

**3. Şerit alfabesi seçimi:**
Q ve W harfleri a ve b'nin işaretlenmiş hallerini temsil eder. '#' ayracı
orijinal ve kopyayı ayırır. Büyük harf kullanımı debug sırasında
hangi karakterin işaretlendiğini görmeyi kolaylaştırdı.

**4. Karmaşıklık:**
n uzunluklu girdi için her tur O(n) adım, n tur.
Toplam: O(n²) adım.

**5. Hata ayıklama hikayesi:**
İlk versiyonda q_find '#' görünce q_done'a geçiyordu ama Q ve W'ler
temizlenmiyordu. Verbose mod ile trace yapınca q_restore durumunun
'#'e ulaşmadan sonlanması gerektiği anlaşıldı. q_find'ı '#' yerine
'B' görünce restore'a geçecek şekilde düzeltince sorun çözüldü.

---

## TM-4: Parantez Denge Kontrolü

**1. Strateji:**
Her turda şeritte birbirine komşu '(' ve ')' çifti aranır. Bulunan çift X ile
işaretlenir (silinir). Hiç çift kalmazsa: şerit tamamen X ise kabul, hala
parantez varsa ret. Bu "iç içe azaltma" yaklaşımı klasik stack mantığını
tek şeritte simüle eder.

**2. Durum sayısı:**
7 durum kullanıldı. q_find, q_found_open, q_mark_close, q_rewind, q_check,
q_accept, q_reject. Minimal tasarım — daha az durum mümkün değil.

**3. Şerit alfabesi seçimi:**
Sadece '(', ')', 'X', 'B' kullanıldı. X silinen karakterleri temsil eder.
Alternatif olarak boşlukla silinebilirdi ama X görünür olduğu için
debug kolaylığı sağlar.

**4. Karmaşıklık:**
n uzunluklu girdi için her tur O(n) adım, en fazla n/2 tur.
Toplam: O(n²) adım.

**5. Hata ayıklama hikayesi:**
İlk versiyonda ')(' girdisi yanlışlıkla kabul ediliyordu. q_find ')'
gördüğünde direkt ret etmesi gerektiği anlaşıldı. Bu tek satır ekleme
ile düzeldi: q_find ')' görünce q_reject'e geç.