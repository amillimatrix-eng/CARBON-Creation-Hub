# CARBON° Search — Simple Discovery UX V1

Date: 2026-10-09
Owner direction: ACCEPTED
Classification recommendation: PRODUCT / UX TUNING
Boundary: does not change the frozen CARBON° Search 35/35 gate count. This is implementation calibration / public-surface tuning unless Governance determines otherwise.

## Product rule

CARBON° Search must be understandable immediately.

A first-time user should be able to type, adjust one or two obvious controls if needed, and understand what the product does without learning a marketplace taxonomy.

**SIMPLE FIRST. INTELLIGENCE UNDERNEATH.**

## Search behavior

The main search box must accept:

- broad brand: `Samsung`
- brand + model: `Samsung Galaxy S26`
- model only: `Galaxy S26`
- model / code only where resolvable
- product type: `laptop`, `notebook`, `phone`, `monitor`, etc.
- brand + type: `Samsung laptop`
- natural-language need: `Samsung notebook around R15,000`
- mixed / incomplete wording.

Search must use canonical identity/entity resolution to determine whether a term is:
- brand;
- model;
- product family;
- product type/category;
- attribute/specification;
- ambiguous/unknown.

If the exact model is confidently resolved, show that result first and allow nearby alternatives only as secondary pivots.

If only a model name/code is supplied, Search should infer the likely product class from evidence, not force the user to manually choose a category first.

## Minimal filters

Do not recreate Facebook Marketplace.

Visible filters must stay minimal and decision-relevant.

Default filter set:

1. **Type / category** — only when ambiguity remains or multiple materially different product classes are present.
2. **Price range** — slider.
3. **Condition** — New / Used / Refurbished, where relevant.
4. **Location / distance** — only where the marketplace result is location-sensitive and permission/context exists.
5. **Availability** — optional when materially useful.

Everything else should normally be handled by:
- natural-language intent;
- inferred constraints;
- smart ranking;
- Intent Pivots;
- inline chips only when a hidden variable materially changes the result.

Do not expose large advanced-filter panels by default.

## Filter law

**IF A CONSTRAINT CAN BE EXPRESSED NATURALLY OR WITH A SIMPLE SLIDER/CHIP, DO NOT TURN IT INTO A COMPLEX FILTER FORM.**

Filters refine; they do not replace intent resolution.

## First-use experience

The default surface should show:

- one obvious search field;
- a compact placeholder/example;
- at most a few lightweight filter controls;
- clear result cards;
- one concise explanation of why the top result matches;
- optional 0–2 Intent Pivots.

No onboarding wall.
No dashboard overload.
No marketplace-style filter maze.

## Example

Query:
`Samsung 940X5N`

Desired behavior:
- resolve `940X5N` as a model/model-family identifier if evidence supports it;
- infer notebook/laptop class;
- return matching canonical entity/results;
- expose ambiguity only if the identifier maps to multiple materially different entities;
- do not force the user to select "Electronics → Computers → Laptops → Brand → Model" manually.

## Acceptance examples

PASS:
- `Samsung` returns relevant Samsung product families/results with minimal refinement.
- `Samsung Galaxy S26` prioritizes exact Galaxy S26 identity.
- `Galaxy S26` works without brand repetition where identity is defensible.
- model code alone can resolve to product class when evidence supports it.
- `Samsung laptop under R15000` uses intent + price range without demanding a large form.
- ambiguous terms trigger one small clarification or useful pivot rather than a filter wall.

FAIL:
- exact model query is treated only as generic keyword search;
- user must know category hierarchy before searching;
- dozens of filters appear by default;
- filters silently invent preference;
- Search cannot distinguish brand, model and product type;
- interface looks like a generic classifieds marketplace rather than CARBON° Search.
