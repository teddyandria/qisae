# Direction visuelle — « Studio »

Langage visuel du frontend. Pour les règles de code React, voir `conventions-frontend.md`.
Remplace la direction « Planche-contact » claire (voir `decisions/0003`).

## Thèse

L'app doit se lire comme un **outil professionnel de sélection**, pas comme un site
vitrine. On emprunte l'ambiance de la salle de visionnage : l'interface est sombre et
s'efface, **les portraits sont la seule source de lumière**. Le vocabulaire du casting
reste intact — comp card, planche, vitals, selects, chinagraphe.

Cette direction évite les trois looks « générés par IA » : crème + serif contrasté +
terracotta ; noir + accent acide fluo ; maquette journal à filets fins.

## La contrainte qui prime sur l'esthétique

> Un directeur de casting doit percevoir les **carnations justes**.

Conséquence non négociable : l'interface est sombre, mais **les comp cards restent sur
un support clair neutre** (`--tirage`). On ne teinte jamais la zone qui entoure une
photo, et aucun filtre (saturation, teinte, overlay coloré) n'est appliqué aux images.
Le contraste entre l'interface sombre et le support clair est précisément ce qui fait
ressortir les visages.

## Tokens

### Surfaces & encres

| Rôle | Hex | Usage |
|------|-----|-------|
| Studio | `#14151A` | fond général |
| Surface | `#1C1E25` | rail, panneaux, barres |
| Surface haute | `#232630` | champs, éléments surélevés |
| **Tirage** | `#FBFBFA` | **support des comp cards — jamais teinté** |
| Encre | `#EDEEF2` | texte sur fond sombre |
| Encre inverse | `#17171B` | texte sur support clair |
| Annotation | `#8E93A3` | texte secondaire, labels mono |
| Ligne | `#2E323C` | filets |

### Accent — un seul bleu, trois déclinaisons

L'accent ne sert **qu'**au select, à l'état actif et à l'action principale. Jamais en
décoration. Un ton unique ne pouvant pas être lisible sur tous les supports, il est
décliné selon le fond, chaque valeur étant calée sur un contraste vérifié :

| Token | Hex | Usage | Contraste |
|-------|-----|-------|-----------|
| `--chinagraphe` | `#4B6BFF` | bordures, cercle de select, fonds teintés | — |
| `--chinagraphe-texte` | `#6485FF` | texte sur fond sombre | 5.5:1 |
| `--chinagraphe-sombre` | `#2B45D4` | texte sur comp card claire | 7.0:1 |
| `--chinagraphe-plein` | `#3D5CE8` | fond de bouton (texte blanc) | 5.4:1 |

### Familles de facettes

Une encre par famille (identité, physique, apparence, sport, langue, métier, mobilité,
expérience), en versions lumineuses lisibles sur fond sombre (≥ 6:1). Elle porte le
filet et le libellé d'un bloc, **jamais un aplat de fond**. C'est un repère de lecture,
pas une décoration.

### Typographie — trois rôles assumés (jamais Inter)

- **Display / labels** : `Saira Condensed` — noms, titres, chips. Capitales, interlettrage serré.
- **Données / vitals** : `Space Mono` — chiffres tabulaires, méta, index de frame.
- **Corps** : `IBM Plex Sans` — texte courant, formulaires.

### Forme & matière

- **Angles nets** : `border-radius: 0` partout. Les comp cards sont des tirages.
- **Grain** : overlay de bruit à 3,5 % sur le fond sombre.
- **Élévation par l'ombre portée**, admise ici : sur fond sombre elle sépare les plans
  sans salir. Réservée aux cartes au survol et à l'état select.
- **Pas de** : glassmorphism, gradients décoratifs, coins arrondis mous, néons.
  Le seul dégradé toléré est le voile sous la ligne d'apparence d'une comp card.

## Système de layout

- **Barre d'en-tête** persistante : marque, contexte de l'écran, état de session
  (témoin vert/gris), action principale. C'est le repère « outil pro ».
- **Recherche = planche-contact** : grille de comp cards (4 colonnes, 3 puis 2), frames
  numérotées (`001`, `002`…), bande de perforations en tête.
- **Rail de filtres = feuille de casting** : labels mono capitales, filet de famille qui
  se révèle au survol, chips reflétant 1:1 les query params.
- **Comp card** : portrait 4/5 dominant, index de frame, ligne d'apparence en
  surimpression, bloc vitals mono tabulaire, bande de plans alternatifs en pied.

## Motion

Retenue, mais assumée. **Une seule courbe** (`cubic-bezier(.22,.61,.36,1)`) et **deux
durées** (160 ms / 320 ms) pour tout : c'est cette cohérence qui fait « pro », pas la
variété des effets. Trois primitives seulement — `arrivee`, `fondu`, `respiration` —
plus le tracé du cercle de select.

- **Cascade d'arrivée** des cartes : 22 ms de décalage par frame.
- **Survol** : la carte se soulève de 3 px, le portrait se rapproche de 3 %.
- **Signature** : le cercle au chinagraphe qui se trace en 0,5 s au marquage d'un select.
- **Chargement** : squelettes qui respirent, jamais d'écran vide qui saute.
- `prefers-reduced-motion` neutralise animations et déplacements.

## Écriture (copie)

Vocabulaire du métier, pas du système : « selects », « planche », « vitals », « dispo ».
Labels en capitales mono, phrases courtes, voix active. Les états vides et les erreurs
guident vers l'action, sans s'excuser.

## Plancher qualité

- Contraste **AA** vérifié pour chaque paire texte/fond, y compris les familles de facettes.
- Responsive jusqu'au mobile (rail au-dessus, grille 2 colonnes).
- Focus clavier visible (contour chinagraphe).
- `prefers-reduced-motion` respecté.
- **UI sombre = photos justes** : ne jamais teinter le support d'une image ni y appliquer
  de filtre. Contrainte métier, pas esthétique.

## À refuser

- Les trois looks IA par défaut.
- Inter, coins arrondis mous, glassmorphism, néons, gradients décoratifs.
- L'accent ailleurs que sur le select / l'état actif / l'action principale.
- Une durée ou une courbe d'animation ad hoc : tout passe par les tokens.
- Teinter le support d'une photo, ou filtrer une image de profil.
