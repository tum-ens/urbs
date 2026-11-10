# Cost assumptions

Unit costs and rules used by `analyze_expansion.py` for the reinforcement cost in the MSc thesis (Lee, 2026), Section 3.7 and Tables 3.12 to 3.15. All costs are in EUR at 2026 prices.

## 1. Reinforcement criteria

|Component|Quantity compared|Limit|Source|
|-|-|-|-|
|Cables|annual maximum current / permissible current|100% (cases A1, B1) or 60% (cases A2, B2)|100%: Wintzek et al. (2021); 60%: Spalthoff et al. (2022)|
|MV/LV transformer|annual maximum apparent power / rated power|100%|Wintzek et al. (2021), based on DIN EN 60076-1|
|Voltage|bus voltage|0.9 to 1.1 pu|flagged in the results, not priced|

The cable limit is set with the environment variable `LOAD_THRESHOLD` (1.0 or 0.6).

## 2. Price indices (Table 3.13)

|Item|Index|2021 = 100|Factor|
|-|-|-|-|
|Cables and civil works|Destatis construction price index, civil engineering, local sewers (Ortskanäle)|138.4|×1.384|
|Transformers|Destatis producer price index GP19-27114, electrical transformers|152.1|×1.521|
|Substations|Destatis producer price index GP19-27114, electrical transformers|152.1|×1.521|

## 3. Cables (Tables 3.12 and 3.14)

Standard cable types are assigned to the three cross-section classes of Wintzek et al. (2021): cables below 150 mm² use the 150 mm² cost, cables above 240 mm² use the 240 mm² cost.

|Cable|Parallel laying, 2021 (EUR/km)|Parallel laying, 2026 (EUR/km)|Separate laying, 2021 (EUR/km)|Separate laying, 2026 (EUR/km)|
|-|-:|-:|-:|-:|
|NAYY 4x150|20,000|27,680|150,000|207,600|
|NAYY 4x185|40,000|55,360|175,000|242,200|
|NAYY 4x240|60,000|83,040|200,000|276,800|

Source: Wintzek et al. (2021).

Number of additional cables in a section: `ceil(peak current / (permissible current × limit)) − existing cables`.

|Method|Cost of a section with n additional cables|
|-|-|
|A (parallel laying)|n × parallel cost × length|
|B (separate laying)|(separate cost + (n − 1) × parallel cost) × length|

Method A assumes that a spare conduit is available for every additional cable. Method B lays the first additional cable in a new trench.

## 4. Transformers (Table 3.15)

Voltage-regulated transformers (rONT) are used for every replacement.

|Rating|2021 (EUR)|2026 (EUR)|Source|
|-|-:|-:|-|
|400 kVA|18,054|27,460|linear fit to the five ratings of Wintzek et al. (2021)|
|630 kVA|21,200|32,245|Wintzek et al. (2021)|
|800 kVA|24,200|36,808|Wintzek et al. (2021)|
|1,000 kVA|27,500|41,828|Wintzek et al. (2021)|
|1,200 kVA|30,000|45,630|Wintzek et al. (2021)|
|1,600 kVA|36,000|54,756|Wintzek et al. (2021)|

Selection rule:

* Required capacity up to 1,600 kVA: the smallest single unit that covers the required capacity.
* Required capacity above 1,600 kVA: as many 1,600 kVA units as fit, plus the smallest unit that covers the remainder, installed in parallel at the existing supply point.
* A grid split is not modelled (Sections 5.3 and 5.4).

## 5. Substations

|Measure|2021 (EUR)|2026 (EUR)|Applied when|Source|
|-|-:|-:|-|-|
|Substation replacement|55,000|83,655|the first transformer unit is 1,000 kVA or above|Wintzek et al. (2021); threshold following Candas (2024)|
|New substation|45,000|68,445|for each additional parallel transformer unit|Wintzek et al. (2021)|

## 6. Total cost per grid

```
cost A = cable cost (method A) + transformer cost + substation cost
cost B = cable cost (method B) + transformer cost + substation cost
```

The four cost cases of the thesis are:

|Case|Cable laying|Cable limit|Result column, file|
|-|-|-|-|
|A1|parallel|100%|`total_cost_A`, `*_TH100.csv`|
|B1|separate|100%|`total_cost_B`, `*_TH100.csv`|
|A2|parallel|60%|`total_cost_A`, `*_TH60.csv`|
|B2|separate|60%|`total_cost_B`, `*_TH60.csv`|

## References

* Candas, S. (2024). *Optimization and data acquisition framework for low-voltage distribution systems in transformation* (Dissertation). Technische Universität München. https://mediatum.ub.tum.de/doc/1728543/1728543.pdf
* Destatis (2026a). *Bau- und Immobilienpreisindex*. Statistisches Bundesamt. https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Baupreise-Immobilienpreisindex/_inhalt.html
* Destatis (2026b). *Index der Erzeugerpreise gewerblicher Produkte (Tabelle 61241-0006)*. Statistisches Bundesamt, GENESIS-Online. https://genesis.destatis.de/datenbank/online/statistic/61241/table/61241-0006
* Spalthoff, C., Ulffers, J., Prade, E., Kneiske, T., Lenz, M., & Braun, M. (2022). *Flexible Wärmepumpen im Verteilnetz*. Fraunhofer IEE. https://www.waermepumpe.de/fileadmin/user_upload/Kurzstudie_FlexWP.pdf
* Wintzek, P., Alsayed Ali, S., Monscheidt, J., Gemsjäger, B., Slupinski, A., & Zdrallek, M. (2021). *Planungs- und Betriebsgrundsätze für städtische Verteilnetze: Leitfaden zur Ausrichtung der Netze an ihren zukünftigen Anforderungen* (Neue Energie aus Wuppertal, Band 35). Bergische Universität Wuppertal.

