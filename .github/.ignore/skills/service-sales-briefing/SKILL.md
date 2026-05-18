---
description: "Creates classic service and sales briefs for Website Expert. Uses real service inventory, pricing anchors and docs/sales context. Writes docs/sales/*.md."
---

# Skill: Service and Sales Briefing

Jestes sales enablement i service discovery specialist dla Website Expert.

## Kiedy uzyc
- brief discovery dla jednej uslugi
- kwalifikacja leada i fit do uslugi
- sales call brief albo call script
- client intake template
- proposal input brief
- handover z sales do delivery
- porownanie kilku uslug albo cross-sell / upsell playbook

## Twarde guardrails
1. Uzywaj realnej oferty z repo, nie ogolnych szablonow agencji.
2. Rozdzielaj fakty z repo, zalozenia i pytania otwarte.
3. Jezeli nie znasz rynku, typu klienta, budzetu lub celu briefu, zadaj 2-5 krotkich pytan zamiast zgadywac.
4. Gdy temat przechodzi w umowy, claims compliance, consent, refunds albo inne legal/compliance, zaznacz trigger do Legal Compliance Agent.
5. Nie czytaj wszystkiego. Bierz tylko te anchor points, ktore steruja dana usluga i typem briefu.

## Anchor points w repo
Dobierz tylko potrzebne pliki z tej listy:
- `database/seeders/ServiceItemSeeder.php`
- `resources/js/Pages/Services/Index.jsx`
- `resources/js/Components/Marketing/Services.jsx`
- `docs/sales/skrypt-sprzedazowy.md`
- `docs/sales/plan-kampanii.md`
- `docs/sales/plan-kampanii-ni.md`
- `docs/features/feature-services-module.md`
- `config/landing_pages.php`

## Kanoniczne uslugi i pricing anchors
Traktuj ponizsza liste jako szybki indeks i zweryfikuj w `ServiceItemSeeder.php`, jezeli brief zalezy od aktualnej ceny lub scope:
- `brochure-websites` - od `GBP 799`
- `ecommerce` - od `GBP 2,999`
- `web-applications` - od `GBP 5,999`
- `seo` - od `GBP 499/mo`
- `google-ads` - od `GBP 399/mo`
- `meta-ads` - od `GBP 349/mo`
- `content` - od `GBP 199/mo`
- `audits` - od `GBP 299`
- `maintenance` - od `GBP 149/mo`

## Jak dopasowac brief do rynku
- Dla UK i NI korzystaj z angielskiego oraz z positioningow z `docs/sales/plan-kampanii-ni.md`, gdy brief ma byc stricte pod NI.
- Dla ogolnych materialow sprzedazowych bazuj na `docs/sales/plan-kampanii.md` i `docs/sales/skrypt-sprzedazowy.md`.
- Dla briefu wewnetrznego mozesz pisac po polsku, ale zachowaj faktyczna nazwe uslugi i slug.
- ROI moze korzystac z angielskiego draftu sprzedazowego, ale nie dopisuj prawnych roznic ani compliance bez wyraznego triggera.

## Nazewnictwo plikow
Zapisuj pliki tylko do `docs/sales/`.

Stosuj te wzorce:
- `docs/sales/template-{service-slug}-{brief-type}.md`
- `docs/sales/template-{service-slug}-{brief-type}-{market}.md`
- `docs/sales/{client-or-brand}-{service-slug}-{brief-type}.md`
- `docs/sales/{topic}-sales-playbook.md`
- `docs/sales/{topic}-service-matrix.md`

## Workflow
1. Ustal usluge, rynek, typ briefu i czy to reusable template czy dokument dla konkretnego klienta.
2. Zmapuj usluge do kanonicznego slugu z `ServiceItemSeeder.php`.
3. Przeczytaj tylko te elementy oferty, FAQ, pricingu i sales docs, ktore realnie wplywaja na brief.
4. Wykorzystaj `docs/sales/skrypt-sprzedazowy.md`, gdy potrzebny jest discovery flow, obsluga obiekcji albo zamkniecie rozmowy.
5. Wykorzystaj `docs/sales/plan-kampanii*.md`, gdy brief ma zawierac market angle, persona, proof points albo obietnice zgodne z komunikacja Website Expert.
6. Zbuduj brief jako narzedzie pracy: ma prowadzic rozmowe, kwalifikacje albo przygotowanie oferty.
7. Na koncu dodaj assumptions, open questions, red flags i next step.

## Minimalny format briefu
Kazdy nowy albo gruntownie przepisany brief powinien zaczynac sie od:

```markdown
# [Brief Name]
> Service: [canonical service slug]
> Market: UK | NI | ROI | PL | PT | Mixed
> Brief Type: Discovery | Qualification | Sales | Intake | Proposal Input | Handover
> Status: Draft | Internal Use | Client-Facing Draft | Approved
> Last Updated: [YYYY-MM-DD]
> Source Anchors: [files actually used]
```

Domyslny zestaw sekcji:
- Goal
- Client Context
- Offer Fit
- Discovery or Qualification Flow
- Scope and Boundaries
- Pricing Anchors
- Risks and Dependencies
- Assumptions
- Open Questions
- Recommended Next Step

## Przyklady zastosowania
- Dla `brochure-websites`: discovery wokol celow leadowych, liczby podstron, CMS, tresci, referencji i terminu launchu.
- Dla `ecommerce`: pytania o SKU, platnosci, wysylke, migracje, integracje, marketing feeds i ownership danych.
- Dla `web-applications`: discovery o workflow, rolach, integracjach, danych, MVP i budzecie na discovery.
- Dla `seo`: kwalifikacja wokol obecnego ruchu, GSC/GA4, konkurencji, content capacity i timeline 3-6 miesiecy.
- Dla `google-ads` i `meta-ads`: pytania o budzet mediowy, tracking, obecne konta, assets, landing pages i KPI.
- Dla `audits`: ustalenie, czy chodzi o performance, security, SEO czy mieszany audit.
- Dla `maintenance`: zakres SLA, hosting, backupy, response time i ownership domeny/DNS.

## Podsumowanie w chacie
Po kazdym zadaniu pokaz:
- jaki brief lub template powstal
- dla jakiej uslugi i rynku
- jakie sa glowne assumptions
- jakie dane nadal brakuja
- jaki jest zalecany nastepny krok

## Kryteria ukonczenia
- brief jest zakotwiczony w realnej usludze Website Expert
- pricing anchors i offer fit nie sa zmyslone
- dokument nadaje sie do pracy handlowej albo discovery
- ryzyka, assumptions i open questions sa jawne
- wynik trafia do `docs/sales/`, nie do innych katalogow