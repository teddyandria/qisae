import { useQuery, useQueryClient } from "@tanstack/react-query";
import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import type { Accent, Departement, Reference, Sport } from "../../api/client";
import { EnTete } from "../../components/EnTete";
import {
  ErreurValidation,
  creerProfil,
  creerReference,
  modifierProfil,
  televerserPhoto,
} from "../../api/ecriture";
import { useReferentiel } from "../recherche/useRecherche";
import styles from "./FormulaireProfil.module.css";

const couleur = (famille: string) =>
  ({ ["--famille"]: `var(--famille-${famille})` }) as React.CSSProperties;

const NIVEAUX_SPORT = [
  ["1", "Débutant"],
  ["2", "Amateur"],
  ["3", "Confirmé"],
  ["4", "Compétition"],
  ["5", "Professionnel"],
];
const NIVEAUX_4 = [
  ["1", "Débutant"],
  ["2", "Intermédiaire / amateur"],
  ["3", "Avancé / confirmé"],
  ["4", "Professionnel"],
];
const NIVEAUX_LANGUE = [
  ["A1", "A1"],
  ["A2", "A2"],
  ["B1", "B1"],
  ["B2", "B2"],
  ["C1", "C1"],
  ["C2", "C2"],
  ["LM", "Langue maternelle"],
];

const SEXES = [
  ["", "—"],
  ["F", "Femme"],
  ["H", "Homme"],
  ["A", "Autre"],
];
const YEUX = ["", "marron", "bleu", "vert", "noisette", "gris", "noir"];
const CHEVEUX = ["", "blond", "chatain", "brun", "noir", "roux", "gris", "blanc", "colore"];
const TYPE_CHEVEUX = ["", "raides", "ondules", "boucles", "crepus"];
const LONGUEUR = ["", "courts", "mi_longs", "longs"];
const BOOLEENS: [string, string][] = [
  ["barbe", "Barbe"],
  ["moustache", "Moustache"],
  ["cheveux_colores", "Cheveux colorés"],
  ["tatouages_visibles", "Tatouages visibles"],
  ["piercings", "Piercings"],
  ["lunettes", "Lunettes"],
  ["lentilles", "Lentilles"],
  ["deja_figurant", "Déjà figurant"],
  ["peut_dormir_sur_place", "Peut dormir sur place"],
  ["vehicule_personnel_disponible", "Véhicule personnel"],
  ["besoin_transport", "Besoin d'un transport"],
  ["profil_multiculturel", "Profil multiculturel"],
];
const TYPES_PHOTO = [
  ["portrait", "Portrait"],
  ["pied", "En pied"],
  ["profil", "Profil"],
  ["avec_barbe", "Avec barbe"],
  ["sans_barbe", "Sans barbe"],
];

type Lien = Record<string, string | number | null>;

/** Un accent déclare les langues dans lesquelles il s'entend (type généré depuis
 *  le contrat OpenAPI). Liste vide = accent universel, proposé pour toute langue. */
type AccentAvecLangues = Accent;

/** Accents proposables pour une langue : ceux qui lui sont rattachés, plus les
 *  universels. Sans langue choisie, on ne propose rien — l'accent qualifie une
 *  langue précise, le demander avant serait sans objet. */
function accentsPour(
  accents: AccentAvecLangues[] | undefined,
  langueId: number | null,
): AccentAvecLangues[] {
  if (!accents || !langueId) return [];
  return accents.filter((a) => !a.langues?.length || a.langues.includes(langueId));
}
type Etat = Record<string, unknown>;

const ETAT_INITIAL: Etat = {
  nom: "",
  prenom: "",
  nom_artiste: "",
  reference: "",
  sexe: "",
  date_naissance: "",
  telephone: "",
  email: "",
  ville: "",
  apparences: [] as number[],
  registres: [] as number[],
  metiers: [] as number[],
  sports: [] as Lien[],
  langues: [] as Lien[],
  instruments: [] as Lien[],
  competences_artistiques: [] as Lien[],
};

function calculerAge(iso: unknown): number | null {
  if (typeof iso !== "string" || !iso) return null;
  const naissance = new Date(iso);
  if (Number.isNaN(naissance.getTime())) return null;
  const aujourdhui = new Date();
  let age = aujourdhui.getFullYear() - naissance.getFullYear();
  const avant =
    aujourdhui.getMonth() < naissance.getMonth() ||
    (aujourdhui.getMonth() === naissance.getMonth() && aujourdhui.getDate() < naissance.getDate());
  if (avant) age -= 1;
  return age;
}

/* Ces composants restent au niveau module : définis dans le corps du formulaire,
   ils changeraient d'identité à chaque frappe et React remonterait les champs,
   ce qui fait perdre le focus après chaque caractère saisi. */

function Champ({
  cle,
  libelle,
  valeur,
  erreur,
  onChange,
  type = "text",
  options,
}: {
  cle: string;
  libelle: string;
  valeur: unknown;
  erreur?: string[];
  onChange: (cle: string, valeur: unknown) => void;
  type?: string;
  options?: (string | string[])[];
}) {
  return (
    <div className={styles.champ} data-erreur={Boolean(erreur)}>
      <label htmlFor={cle}>{libelle}</label>
      {options ? (
        <select
          id={cle}
          value={String(valeur ?? "")}
          onChange={(e) => onChange(cle, e.target.value)}
        >
          {options.map((option) => {
            const [valeurOption, texte] = Array.isArray(option) ? option : [option, option || "—"];
            return (
              <option key={valeurOption} value={valeurOption}>
                {texte}
              </option>
            );
          })}
        </select>
      ) : (
        <input
          id={cle}
          type={type}
          value={String(valeur ?? "")}
          onChange={(e) =>
            onChange(cle, type === "number" ? e.target.value.replace(/\D/g, "") : e.target.value)
          }
        />
      )}
      {erreur && <span className={styles.erreurChamp}>{erreur.join(" ")}</span>}
    </div>
  );
}

/** Création d'une entrée de référentiel sans quitter la saisie.
 *
 *  Au niveau module, comme les autres composants de ce fichier : défini dans le
 *  corps du formulaire, il changerait d'identité à chaque frappe et React
 *  remonterait le champ, faisant perdre le focus après chaque caractère.
 */
function AjoutReference({
  chemin,
  libelle,
  avecCategorie = false,
  languesRattachees,
  onCree,
}: {
  chemin: string;
  libelle: string;
  avecCategorie?: boolean;
  languesRattachees?: number[];
  onCree: (cree: { id: number; nom: string }) => void;
}) {
  const [ouvert, setOuvert] = useState(false);
  const [nom, setNom] = useState("");
  const [categorie, setCategorie] = useState("individuel");
  const [erreur, setErreur] = useState<string | null>(null);
  const [envoi, setEnvoi] = useState(false);

  function fermer() {
    setOuvert(false);
    setNom("");
    setErreur(null);
  }

  async function valider() {
    const propre = nom.trim();
    if (!propre) return;
    setEnvoi(true);
    setErreur(null);
    try {
      const cree = await creerReference(chemin, {
        nom: propre,
        ...(avecCategorie && { categorie }),
        ...(languesRattachees?.length && { langues: languesRattachees }),
      });
      onCree(cree);
      fermer();
    } catch (e) {
      setErreur((e as Error).message);
    } finally {
      setEnvoi(false);
    }
  }

  if (!ouvert) {
    return (
      <button type="button" className={styles.ajouter} onClick={() => setOuvert(true)}>
        + {libelle}
      </button>
    );
  }

  return (
    <div className={styles.creation}>
      <div className={styles.creationLigne}>
        <input
          autoFocus
          value={nom}
          placeholder={libelle}
          onChange={(e) => setNom(e.target.value)}
          // Entrée valide, Échap annule : on ne soumet jamais le formulaire
          // profil depuis ce champ, d'où le preventDefault.
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              valider();
            } else if (e.key === "Escape") {
              e.preventDefault();
              fermer();
            }
          }}
        />
        {avecCategorie && (
          <select value={categorie} onChange={(e) => setCategorie(e.target.value)}>
            <option value="individuel">Individuel</option>
            <option value="collectif">Collectif</option>
          </select>
        )}
        <button type="button" className={styles.confirmer} onClick={valider} disabled={envoi}>
          {envoi ? "…" : "Créer"}
        </button>
        <button type="button" className={styles.retirer} onClick={fermer}>
          Annuler
        </button>
      </div>
      {erreur && <div className={styles.erreurChamp}>{erreur}</div>}
    </div>
  );
}

function BlocReferences({
  cle,
  legende,
  liste,
  famille,
  actifs,
  onBasculer,
  chemin,
  libelleAjout,
  onCree,
}: {
  cle: string;
  legende: string;
  liste: Reference[] | undefined;
  famille: string;
  actifs: number[];
  onBasculer: (cle: string, id: number) => void;
  chemin?: string;
  libelleAjout?: string;
  onCree?: (cle: string, cree: { id: number; nom: string }) => void;
}) {
  return (
    <section className={styles.section} style={couleur(famille)}>
      <div className={styles.legende}>{legende}</div>
      <div className={styles.chips}>
        {(liste ?? []).map((reference) => (
          <button
            key={reference.id}
            type="button"
            className={styles.chip}
            data-actif={actifs.includes(reference.id)}
            onClick={() => onBasculer(cle, reference.id)}
          >
            {reference.nom}
          </button>
        ))}
      </div>
      {chemin && onCree && (
        <div className={styles.zoneAjout}>
          <AjoutReference
            chemin={chemin}
            libelle={libelleAjout ?? "Ajouter"}
            onCree={(cree) => onCree(cle, cree)}
          />
        </div>
      )}
    </section>
  );
}

function BlocLiens({
  cle,
  legende,
  champ,
  liste,
  niveaux,
  famille,
  liens,
  erreur,
  onAjouter,
  onModifier,
  onRetirer,
  accents,
  avecAccent = false,
  chemin,
  libelleAjout,
  avecCategorie = false,
  onCree,
  cheminAccent,
  onAccentCree,
}: {
  cle: string;
  legende: string;
  champ: string;
  liste: { id: number; nom: string }[] | undefined;
  niveaux: string[][];
  famille: string;
  liens: Lien[];
  erreur?: string[];
  onAjouter: (cle: string, gabarit: Lien) => void;
  onModifier: (cle: string, index: number, champ: string, valeur: string | number | null) => void;
  onRetirer: (cle: string, index: number) => void;
  accents?: AccentAvecLangues[];
  avecAccent?: boolean;
  chemin?: string;
  libelleAjout?: string;
  avecCategorie?: boolean;
  onCree?: (cle: string, cree: { id: number; nom: string }) => void;
  cheminAccent?: string;
  onAccentCree?: (index: number, cree: { id: number; nom: string }) => void;
}) {
  return (
    <section className={styles.section} style={couleur(famille)}>
      <div className={styles.legende}>{legende}</div>
      {liens.map((lien, index) => (
        <div key={index} className={styles.lien}>
          <select
            value={String(lien[champ] ?? "")}
            onChange={(e) => onModifier(cle, index, champ, Number(e.target.value) || "")}
          >
            <option value="">— choisir —</option>
            {(liste ?? []).map((option) => (
              <option key={option.id} value={option.id}>
                {option.nom}
              </option>
            ))}
          </select>
          <select
            value={String(lien.niveau ?? "")}
            onChange={(e) => onModifier(cle, index, "niveau", e.target.value)}
          >
            {niveaux.map(([valeur, texte]) => (
              <option key={valeur} value={valeur}>
                {texte}
              </option>
            ))}
          </select>
          {avecAccent &&
            (() => {
              const langueId = Number(lien[champ]) || null;
              const proposables = accentsPour(accents, langueId);
              return (
                <select
                  value={String(lien.accent ?? "")}
                  disabled={!langueId}
                  title={langueId ? undefined : "Choisis d'abord une langue"}
                  onChange={(e) =>
                    onModifier(cle, index, "accent", Number(e.target.value) || null)
                  }
                >
                  <option value="">
                    {!langueId
                      ? "langue d'abord"
                      : proposables.length
                        ? "accent —"
                        : "aucun accent"}
                  </option>
                  {proposables.map((accent) => (
                    <option key={accent.id} value={accent.id}>
                      {accent.nom}
                    </option>
                  ))}
                </select>
              );
            })()}
          {avecAccent && cheminAccent && onAccentCree && Number(lien[champ]) > 0 && (
            <AjoutReference
              chemin={cheminAccent}
              libelle="Accent"
              // La langue de la ligne est transmise : sans elle, l'accent créé
              // serait universel et réapparaîtrait pour toutes les langues.
              languesRattachees={[Number(lien[champ])]}
              onCree={(cree) => onAccentCree(index, cree)}
            />
          )}
          <button type="button" className={styles.retirer} onClick={() => onRetirer(cle, index)}>
            Retirer
          </button>
        </div>
      ))}
      <div className={styles.zoneAjout}>
        <button
          type="button"
          className={styles.ajouter}
          onClick={() =>
            onAjouter(cle, {
              [champ]: "",
              niveau: niveaux[0][0],
              ...(avecAccent && { accent: null }),
            })
          }
        >
          + Ajouter une ligne
        </button>
        {chemin && onCree && (
          <AjoutReference
            chemin={chemin}
            libelle={libelleAjout ?? "Créer"}
            avecCategorie={avecCategorie}
            onCree={(cree) => onCree(cle, cree)}
          />
        )}
      </div>
      {erreur && <div className={styles.erreurChamp}>{erreur.join(" ")}</div>}
    </section>
  );
}

export function FormulaireProfil() {
  const { id } = useParams();
  const modification = Boolean(id);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [etat, setEtat] = useState<Etat>(ETAT_INITIAL);
  const [erreurs, setErreurs] = useState<Record<string, string[]>>({});
  const [message, setMessage] = useState<string | null>(null);
  const [envoi, setEnvoi] = useState(false);
  const [fichierPhoto, setFichierPhoto] = useState<File | null>(null);
  const [typePhoto, setTypePhoto] = useState("portrait");

  const sports = useReferentiel<Sport>("/sports/");
  const langues = useReferentiel<Reference>("/langues/");
  const accents = useReferentiel<AccentAvecLangues>("/accents/");
  const instruments = useReferentiel<Reference>("/instruments/");
  const artistiques = useReferentiel<Reference>("/competences-artistiques/");
  const apparences = useReferentiel<Reference>("/apparences/");
  const registres = useReferentiel<Reference>("/registres/");
  const metiers = useReferentiel<Reference>("/metiers/");
  const departements = useReferentiel<Departement>("/departements/");

  // En modification, on repart du détail existant.
  const detail = useQuery({
    queryKey: ["profil", id],
    enabled: modification,
    queryFn: async () => {
      const reponse = await fetch(`/api/profils/${id}/`, { credentials: "same-origin" });
      if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
      return await reponse.json();
    },
  });

  useEffect(() => {
    if (!detail.data) return;
    const d = detail.data;
    const parNom = (liste: Reference[] | undefined, noms: string[]) =>
      (liste ?? []).filter((r) => noms.includes(r.nom)).map((r) => r.id);
    setEtat({
      ...ETAT_INITIAL,
      ...d,
      departement: d.departement?.id ?? "",
      date_naissance: d.date_naissance ?? "",
      apparences: parNom(apparences.data, d.apparences ?? []),
      registres: parNom(registres.data, d.registres ?? []),
      metiers: parNom(metiers.data, d.metiers ?? []),
      sports: (d.sports ?? []).map((s: { sport: string; niveau: string }) => ({
        sport: sports.data?.find((r) => r.nom === s.sport)?.id ?? "",
        niveau: s.niveau,
      })),
      langues: (d.langues ?? []).map(
        (l: { langue: string; niveau: string; accent: string | null }) => ({
          langue: langues.data?.find((r) => r.nom === l.langue)?.id ?? "",
          niveau: l.niveau,
          accent: accents.data?.find((r) => r.nom === l.accent)?.id ?? null,
        }),
      ),
      instruments: (d.instruments ?? []).map((i: { instrument: string; niveau: string }) => ({
        instrument: instruments.data?.find((r) => r.nom === i.instrument)?.id ?? "",
        niveau: i.niveau,
      })),
      competences_artistiques: (d.competences_artistiques ?? []).map(
        (c: { competence: string; niveau: string }) => ({
          competence: artistiques.data?.find((r) => r.nom === c.competence)?.id ?? "",
          niveau: c.niveau,
        }),
      ),
    });
  }, [
    detail.data,
    apparences.data,
    registres.data,
    metiers.data,
    sports.data,
    langues.data,
    accents.data,
    instruments.data,
    artistiques.data,
  ]);

  const age = calculerAge(etat.date_naissance);
  const estMineur = age !== null && age < 18;

  const definir = useCallback((cle: string, valeur: unknown) => {
    setEtat((precedent) => ({ ...precedent, [cle]: valeur }));
  }, []);

  const basculerReference = useCallback((cle: string, identifiant: number) => {
    setEtat((precedent) => {
      const actuels = (precedent[cle] as number[]) ?? [];
      return {
        ...precedent,
        [cle]: actuels.includes(identifiant)
          ? actuels.filter((v) => v !== identifiant)
          : [...actuels, identifiant],
      };
    });
  }, []);

  /** Après création d'une entrée : rafraîchir la liste et sélectionner la valeur.
   *  Le référentiel est mis en cache une heure, sans invalidation la nouvelle
   *  entrée resterait invisible dans la liste déroulante. */
  const referenceCreee = useCallback(
    (cle: string, chemin: string, cree: { id: number; nom: string }) => {
      queryClient.invalidateQueries({ queryKey: ["referentiel", chemin] });
      setEtat((precedent) => {
        // Listes simples (chips) : on coche la nouvelle valeur.
        if (Array.isArray(precedent[cle]) && typeof (precedent[cle] as unknown[])[0] !== "object") {
          const actuels = (precedent[cle] as number[]) ?? [];
          return { ...precedent, [cle]: [...actuels, cree.id] };
        }
        return precedent;
      });
    },
    [queryClient],
  );

  /** Listes à niveau : on ajoute une ligne déjà renseignée avec la valeur créée. */
  const referenceLienCreee = useCallback(
    (cle: string, chemin: string, champ: string, niveau: string, cree: { id: number }) => {
      queryClient.invalidateQueries({ queryKey: ["referentiel", chemin] });
      setEtat((precedent) => ({
        ...precedent,
        [cle]: [...((precedent[cle] as Lien[]) ?? []), { [champ]: cree.id, niveau }],
      }));
    },
    [queryClient],
  );

  /** Accent créé depuis une ligne de langue : on rafraîchit la liste et on le
   *  sélectionne sur la ligne d'où il a été créé. */
  const accentCree = useCallback(
    (index: number, cree: { id: number }) => {
      queryClient.invalidateQueries({ queryKey: ["referentiel", "/accents/"] });
      setEtat((precedent) => {
        const liens = [...((precedent.langues as Lien[]) ?? [])];
        if (liens[index]) liens[index] = { ...liens[index], accent: cree.id };
        return { ...precedent, langues: liens };
      });
    },
    [queryClient],
  );

  const ajouterLien = useCallback((cle: string, gabarit: Lien) => {
    setEtat((precedent) => ({
      ...precedent,
      [cle]: [...((precedent[cle] as Lien[]) ?? []), gabarit],
    }));
  }, []);

  const modifierLien = useCallback(
    (cle: string, index: number, champ: string, valeur: string | number | null) => {
      setEtat((precedent) => {
        const liens = [...((precedent[cle] as Lien[]) ?? [])];
        liens[index] = { ...liens[index], [champ]: valeur };
        // Changer la langue peut rendre l'accent déjà choisi incohérent : il
        // disparaîtrait de la liste tout en restant enregistré. On le vide.
        if (champ === "langue") liens[index].accent = null;
        return { ...precedent, [cle]: liens };
      });
    },
    [],
  );

  const retirerLien = useCallback((cle: string, index: number) => {
    setEtat((precedent) => ({
      ...precedent,
      [cle]: ((precedent[cle] as Lien[]) ?? []).filter((_, i) => i !== index),
    }));
  }, []);

  function nettoyer(valeurs: Etat) {
    const charge: Etat = {};
    for (const [cle, valeur] of Object.entries(valeurs)) {
      if (valeur === "" || valeur === null || valeur === undefined) continue;
      if (["id", "age", "est_mineur", "photos", "vehicules", "mineur"].includes(cle)) continue;
      charge[cle] = valeur;
    }
    // Les lignes incomplètes ne partent pas au serveur.
    for (const [cle, champ] of [
      ["sports", "sport"],
      ["langues", "langue"],
      ["instruments", "instrument"],
      ["competences_artistiques", "competence"],
    ] as [string, string][]) {
      if (Array.isArray(charge[cle])) {
        charge[cle] = (charge[cle] as Lien[]).filter((l) => l[champ] !== "" && l[champ] != null);
      }
    }
    return charge;
  }

  async function soumettre(evenement: React.FormEvent) {
    evenement.preventDefault();
    setEnvoi(true);
    setErreurs({});
    setMessage(null);
    try {
      const charge = nettoyer(etat);
      const resultat = modification
        ? await modifierProfil(Number(id), charge)
        : await creerProfil(charge);
      const identifiant = resultat?.id ?? Number(id);

      if (fichierPhoto) {
        await televerserPhoto(identifiant, typePhoto, fichierPhoto);
        setFichierPhoto(null);
      }
      queryClient.invalidateQueries({ queryKey: ["profils"] });
      queryClient.invalidateQueries({ queryKey: ["profil", String(identifiant)] });
      setMessage("Profil enregistré.");
      if (!modification) navigate(`/profils/${identifiant}/modifier`, { replace: true });
    } catch (erreur) {
      if (erreur instanceof ErreurValidation) {
        setErreurs(erreur.champs);
        setMessage("Le formulaire contient des erreurs.");
      } else {
        setMessage((erreur as Error).message);
      }
    } finally {
      setEnvoi(false);
    }
  }

  const champ = (cle: string) => ({
    cle,
    valeur: etat[cle],
    erreur: erreurs[cle],
    onChange: definir,
  });

  const liensDe = (cle: string) => ({
    cle,
    liens: (etat[cle] as Lien[]) ?? [],
    erreur: erreurs[cle],
    onAjouter: ajouterLien,
    onModifier: modifierLien,
    onRetirer: retirerLien,
  });

  return (
    <>
      <EnTete contexte={modification ? "Modification" : "Nouveau profil"} />
      <div className={styles.page}>
      <div className={styles.entete}>
        <h1 className={styles.titre}>{modification ? "Modifier le profil" : "Nouveau profil"}</h1>
        <Link className={styles.retour} to="/recherche">
          ← Retour à la planche
        </Link>
      </div>
      <div className={styles.perforations} aria-hidden="true" />

      {estMineur && (
        <div className={styles.alerteMineur}>
          <strong>Profil mineur — {age} ans</strong>
          Le dossier mineur (responsable légal, autorisations) est obligatoire. Il se saisit dans
          l'admin Django, sur la fiche du profil.
        </div>
      )}

      <form onSubmit={soumettre}>
        <section className={styles.section} style={couleur("identite")}>
          <div className={styles.legende}>Identité</div>
          <div className={styles.grille}>
            <Champ {...champ("prenom")} libelle="Prénom" />
            <Champ {...champ("nom")} libelle="Nom" />
            <Champ {...champ("nom_artiste")} libelle="Nom d'artiste" />
            <Champ {...champ("reference")} libelle="Référence" />
            <Champ {...champ("sexe")} libelle="Sexe" options={SEXES} />
            <Champ {...champ("date_naissance")} libelle="Date de naissance" type="date" />
            <Champ {...champ("age_apparent_min")} libelle="Âge apparent min" type="number" />
            <Champ {...champ("age_apparent_max")} libelle="Âge apparent max" type="number" />
          </div>
        </section>

        <section className={styles.section} style={couleur("identite")}>
          <div className={styles.legende}>Contact</div>
          <div className={styles.grille}>
            <Champ {...champ("telephone")} libelle="Téléphone" />
            <Champ {...champ("email")} libelle="E-mail" type="email" />
          </div>
        </section>

        <section className={styles.section} style={couleur("mobilite")}>
          <div className={styles.legende}>Géographie & mobilité</div>
          <div className={styles.grille}>
            <Champ {...champ("ville")} libelle="Ville" />
            <Champ
              {...champ("departement")}
              libelle="Département"
              options={[
                ["", "—"],
                ...(departements.data ?? [])
                  .slice()
                  .sort((a, b) => a.code.localeCompare(b.code))
                  .map((d) => [String(d.id), `${d.code} — ${d.nom}`]),
              ]}
            />
            <Champ {...champ("distance_max_km")} libelle="Distance max (km)" type="number" />
          </div>
        </section>

        <section className={styles.section} style={couleur("physique")}>
          <div className={styles.legende}>Physique</div>
          <div className={styles.grille}>
            <Champ {...champ("taille_cm")} libelle="Taille (cm)" type="number" />
            <Champ {...champ("poids_kg")} libelle="Poids (kg)" type="number" />
            <Champ {...champ("pointure")} libelle="Pointure" type="number" />
            <Champ {...champ("tour_poitrine_cm")} libelle="Tour de poitrine" type="number" />
            <Champ {...champ("tour_taille_cm")} libelle="Tour de taille" type="number" />
            <Champ {...champ("tour_hanches_cm")} libelle="Tour de hanches" type="number" />
            <Champ {...champ("couleur_yeux")} libelle="Couleur des yeux" options={YEUX} />
            <Champ {...champ("couleur_cheveux")} libelle="Couleur des cheveux" options={CHEVEUX} />
            <Champ {...champ("type_cheveux")} libelle="Type de cheveux" options={TYPE_CHEVEUX} />
            <Champ {...champ("longueur_cheveux")} libelle="Longueur" options={LONGUEUR} />
          </div>
          <div className={styles.cases} style={{ marginTop: 10 }}>
            {BOOLEENS.map(([cle, libelle]) => (
              <label key={cle} className={styles.case}>
                <input
                  type="checkbox"
                  checked={Boolean(etat[cle])}
                  onChange={(e) => definir(cle, e.target.checked)}
                />
                {libelle}
              </label>
            ))}
          </div>
        </section>

        <BlocReferences
          cle="apparences"
          legende="Apparence"
          liste={apparences.data}
          famille="apparence"
          actifs={(etat.apparences as number[]) ?? []}
          onBasculer={basculerReference}
        />
        <BlocReferences
          cle="registres"
          legende="Registres"
          liste={registres.data}
          famille="apparence"
          actifs={(etat.registres as number[]) ?? []}
          onBasculer={basculerReference}
          chemin="/registres/"
          libelleAjout="Nouveau registre"
          onCree={(cle, cree) => referenceCreee(cle, "/registres/", cree)}
        />
        <BlocReferences
          cle="metiers"
          legende="Métiers"
          liste={metiers.data}
          famille="metier"
          actifs={(etat.metiers as number[]) ?? []}
          onBasculer={basculerReference}
          chemin="/metiers/"
          libelleAjout="Nouveau métier"
          onCree={(cle, cree) => referenceCreee(cle, "/metiers/", cree)}
        />

        <BlocLiens
          {...liensDe("sports")}
          legende="Sports + niveau"
          champ="sport"
          liste={sports.data}
          niveaux={NIVEAUX_SPORT}
          famille="sport"
        
          chemin="/sports/"
          libelleAjout="Nouveau sport"
          avecCategorie
          onCree={(cle, cree) =>
            referenceLienCreee(cle, "/sports/", "sport", NIVEAUX_SPORT[0][0], cree)
          }
        />
        <BlocLiens
          {...liensDe("langues")}
          legende="Langues + niveau + accent"
          champ="langue"
          liste={langues.data}
          niveaux={NIVEAUX_LANGUE}
          famille="langue"
          accents={accents.data}
          avecAccent
        
          chemin="/langues/"
          libelleAjout="Nouvelle langue"
          cheminAccent="/accents/"
          onAccentCree={accentCree}
          onCree={(cle, cree) =>
            referenceLienCreee(cle, "/langues/", "langue", NIVEAUX_LANGUE[0][0], cree)
          }
        />
        <BlocLiens
          {...liensDe("instruments")}
          legende="Instruments + niveau"
          champ="instrument"
          liste={instruments.data}
          niveaux={NIVEAUX_4}
          famille="experience"
        
          chemin="/instruments/"
          libelleAjout="Nouvel instrument"
          onCree={(cle, cree) =>
            referenceLienCreee(cle, "/instruments/", "instrument", NIVEAUX_4[0][0], cree)
          }
        />
        <BlocLiens
          {...liensDe("competences_artistiques")}
          legende="Compétences artistiques + niveau"
          champ="competence"
          liste={artistiques.data}
          niveaux={NIVEAUX_4}
          famille="experience"
        
          chemin="/competences-artistiques/"
          libelleAjout="Nouvelle compétence"
          onCree={(cle, cree) =>
            referenceLienCreee(cle, "/competences-artistiques/", "competence", NIVEAUX_4[0][0], cree)
          }
        />

        <section className={styles.section} style={couleur("apparence")}>
          <div className={styles.legende}>Photo</div>
          <div className={styles.grille}>
            <div className={styles.champ}>
              <label htmlFor="type_photo">Type de plan</label>
              <select
                id="type_photo"
                value={typePhoto}
                onChange={(e) => setTypePhoto(e.target.value)}
              >
                {TYPES_PHOTO.map(([valeur, texte]) => (
                  <option key={valeur} value={valeur}>
                    {texte}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.champ}>
              <label htmlFor="fichier">Fichier</label>
              <input
                id="fichier"
                type="file"
                accept="image/*"
                onChange={(e) => setFichierPhoto(e.target.files?.[0] ?? null)}
              />
            </div>
          </div>
        </section>

        <div className={styles.barre}>
          <button type="submit" className={styles.enregistrer} disabled={envoi}>
            {envoi ? "Enregistrement…" : "Enregistrer"}
          </button>
          {message && (
            <span
              className={`${styles.message} ${
                Object.keys(erreurs).length > 0 || message.includes("erreur")
                  ? styles.messageErreur
                  : styles.messageSucces
              }`}
            >
              {message}
            </span>
          )}
        </div>
      </form>
      </div>
    </>
  );
}
