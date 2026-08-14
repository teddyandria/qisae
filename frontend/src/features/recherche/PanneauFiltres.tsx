import type React from "react";
import { useEffect, useState } from "react";
import type { Reference, Sport } from "../../api/client";
import styles from "./PanneauFiltres.module.css";
import { useRecherche, useReferentiel } from "./useRecherche";

type Recherche = ReturnType<typeof useRecherche>;

/** Injecte l'encre de la famille de facettes dans la variable CSS locale. */
const couleur = (famille: string) =>
  ({ ["--famille"]: `var(--famille-${famille})` }) as React.CSSProperties;

const NIVEAUX_SPORT = [
  ["", "Tous"],
  ["2", "≥ Amateur"],
  ["3", "≥ Confirmé"],
  ["4", "≥ Compétition"],
  ["5", "Pro"],
];

const NIVEAUX_LANGUE = [
  ["", "Tous"],
  ["B1", "≥ B1"],
  ["B2", "≥ B2"],
  ["C1", "≥ C1"],
  ["LM", "Langue maternelle"],
];

const BOOLEENS: [string, string][] = [
  ["barbe", "Barbe"],
  ["moustache", "Moustache"],
  ["lunettes", "Lunettes"],
  ["tatouages_visibles", "Tatouages"],
  ["piercings", "Piercings"],
  ["deja_figurant", "Déjà figurant"],
  ["peut_dormir_sur_place", "Dort sur place"],
  ["vehicule_personnel_disponible", "Véhicule perso"],
];

/** Champ texte débounçé : ne pas requêter à chaque frappe. */
function ChampTexte({
  valeur,
  onChange,
  placeholder,
}: {
  valeur: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  const [saisie, setSaisie] = useState(valeur);

  useEffect(() => setSaisie(valeur), [valeur]);
  useEffect(() => {
    if (saisie === valeur) return;
    const minuteur = setTimeout(() => onChange(saisie), 300);
    return () => clearTimeout(minuteur);
  }, [saisie, valeur, onChange]);

  return (
    <input
      className={styles.champ}
      value={saisie}
      placeholder={placeholder}
      onChange={(e) => setSaisie(e.target.value)}
    />
  );
}

/** Facette à niveau : les chips écrivent `Valeur:niveau_min` dans l'URL. */
function FacetteNiveau({
  cle,
  legende,
  options,
  niveaux,
  recherche,
  famille,
}: {
  cle: string;
  legende: string;
  options: string[];
  niveaux: string[][];
  recherche: Recherche;
  famille: string;
}) {
  const [niveau, setNiveau] = useState("");
  const actives = recherche.valeurs(cle);
  const nomsActifs = actives.map((v) => v.split(":")[0]);

  return (
    <section className={styles.bloc} style={couleur(famille)}>
      <div className={styles.legende}>{legende}</div>
      <div className={styles.niveau}>
        <select
          className={styles.select}
          value={niveau}
          onChange={(e) => setNiveau(e.target.value)}
          aria-label={`Niveau minimum — ${legende}`}
        >
          {niveaux.map(([valeur, libelle]) => (
            <option key={valeur} value={valeur}>
              {libelle}
            </option>
          ))}
        </select>
      </div>
      <div className={styles.chips} style={{ marginTop: 6 }}>
        {options.slice(0, 14).map((nom) => {
          const actif = nomsActifs.includes(nom);
          return (
            <button
              key={nom}
              type="button"
              className={styles.chip}
              data-actif={actif}
              onClick={() => {
                if (actif) {
                  const existante = actives.find((v) => v.split(":")[0] === nom);
                  if (existante) recherche.retirer(cle, existante);
                } else {
                  recherche.basculer(cle, niveau ? `${nom}:${niveau}` : nom);
                }
              }}
            >
              {nom}
            </button>
          );
        })}
      </div>
    </section>
  );
}

function FacetteSimple({
  cle,
  legende,
  options,
  recherche,
  famille,
  limite = 12,
}: {
  cle: string;
  legende: string;
  options: string[];
  recherche: Recherche;
  famille: string;
  limite?: number;
}) {
  const actives = recherche.valeurs(cle);
  return (
    <section className={styles.bloc} style={couleur(famille)}>
      <div className={styles.legende}>{legende}</div>
      <div className={styles.chips}>
        {options.slice(0, limite).map((nom) => (
          <button
            key={nom}
            type="button"
            className={styles.chip}
            data-actif={actives.includes(nom)}
            onClick={() => recherche.basculer(cle, nom)}
          >
            {nom}
          </button>
        ))}
      </div>
    </section>
  );
}

export function PanneauFiltres({ recherche }: { recherche: Recherche }) {
  const sports = useReferentiel<Sport>("/sports/");
  const langues = useReferentiel<Reference>("/langues/");
  const apparences = useReferentiel<Reference>("/apparences/");
  const registres = useReferentiel<Reference>("/registres/");
  const metiers = useReferentiel<Reference>("/metiers/");

  const params = recherche.params;
  const chipsActives: [string, string][] = [];
  params.forEach((valeur, cle) => {
    if (cle !== "page") chipsActives.push([cle, valeur]);
  });

  return (
    <aside className={styles.rail}>
      <div className={styles.titre}>Qisae</div>

      {chipsActives.length > 0 && (
        <>
          <div className={styles.actifs}>
            {chipsActives.map(([cle, valeur]) => (
              <button
                key={`${cle}-${valeur}`}
                type="button"
                className={styles.actif}
                onClick={() => recherche.retirer(cle, valeur)}
                title="Retirer ce filtre"
              >
                {cle}: {valeur} ✕
              </button>
            ))}
          </div>
          <button type="button" className={styles.effacer} onClick={recherche.toutEffacer}>
            Tout effacer
          </button>
        </>
      )}

      <section className={styles.bloc} style={couleur("identite")}>
        <div className={styles.legende}>Nom / référence</div>
        <ChampTexte
          valeur={params.get("q") ?? ""}
          placeholder="Rechercher…"
          onChange={(v) => recherche.definir("q", v || null)}
        />
      </section>

      <section className={styles.bloc} style={couleur("identite")}>
        <div className={styles.legende}>Sexe</div>
        <div className={styles.chips}>
          {[
            ["", "Tous"],
            ["F", "Femme"],
            ["H", "Homme"],
            ["A", "Autre"],
          ].map(([valeur, libelle]) => (
            <button
              key={libelle}
              type="button"
              className={styles.chip}
              data-actif={(params.get("sexe") ?? "") === valeur}
              onClick={() => recherche.definir("sexe", valeur || null)}
            >
              {libelle}
            </button>
          ))}
        </div>
      </section>

      <section className={styles.bloc} style={couleur("identite")}>
        <div className={styles.legende}>Âge</div>
        <div className={styles.ligne}>
          <ChampTexte
            valeur={params.get("age_min") ?? ""}
            placeholder="min"
            onChange={(v) => recherche.definir("age_min", v || null)}
          />
          <ChampTexte
            valeur={params.get("age_max") ?? ""}
            placeholder="max"
            onChange={(v) => recherche.definir("age_max", v || null)}
          />
        </div>
      </section>

      <section className={styles.bloc} style={couleur("physique")}>
        <div className={styles.legende}>Taille (cm)</div>
        <div className={styles.ligne}>
          <ChampTexte
            valeur={params.get("taille_min") ?? ""}
            placeholder="min"
            onChange={(v) => recherche.definir("taille_min", v || null)}
          />
          <ChampTexte
            valeur={params.get("taille_max") ?? ""}
            placeholder="max"
            onChange={(v) => recherche.definir("taille_max", v || null)}
          />
        </div>
      </section>

      <section className={styles.bloc} style={couleur("mobilite")}>
        <div className={styles.legende}>Département</div>
        <ChampTexte
          valeur={params.get("departement") ?? ""}
          placeholder="ex. 75"
          onChange={(v) => recherche.definir("departement", v || null)}
        />
      </section>

      <FacetteNiveau
        cle="sport"
        famille="sport"
        legende="Sport + niveau"
        options={(sports.data ?? []).map((s) => s.nom)}
        niveaux={NIVEAUX_SPORT}
        recherche={recherche}
      />

      <FacetteNiveau
        cle="langue"
        famille="langue"
        legende="Langue + niveau"
        options={(langues.data ?? []).map((l) => l.nom)}
        niveaux={NIVEAUX_LANGUE}
        recherche={recherche}
      />

      <FacetteSimple
        cle="apparence"
        famille="apparence"
        legende="Apparence"
        options={(apparences.data ?? []).map((a) => a.nom)}
        recherche={recherche}
      />

      <FacetteSimple
        cle="registre"
        famille="apparence"
        legende="Registre"
        options={(registres.data ?? []).map((r) => r.nom)}
        recherche={recherche}
      />

      <FacetteSimple
        cle="metier"
        famille="metier"
        legende="Métier"
        options={(metiers.data ?? []).map((m) => m.nom)}
        recherche={recherche}
      />

      <section className={styles.bloc} style={couleur("physique")}>
        <div className={styles.legende}>Signes particuliers</div>
        <div className={styles.casesLigne}>
          {BOOLEENS.map(([cle, libelle]) => (
            <label key={cle} className={styles.case}>
              <input
                type="checkbox"
                checked={params.get(cle) === "true"}
                onChange={(e) => recherche.definir(cle, e.target.checked ? "true" : null)}
              />
              {libelle}
            </label>
          ))}
        </div>
      </section>
    </aside>
  );
}
