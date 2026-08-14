import { useQuery } from "@tanstack/react-query";
import type React from "react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { EnTete } from "../../components/EnTete";
import { lienConnexion, useSession } from "../../hooks/useSession";
import styles from "./FicheProfil.module.css";

const couleur = (famille: string) =>
  ({ ["--famille"]: `var(--famille-${famille})` }) as React.CSSProperties;

type Photo = { id: number; type: string; type_libelle: string; url: string; prise_le: string | null };
type LienNiveau = { niveau: string; niveau_libelle: string } & Record<string, string | null>;

// Ordre de lecture d'une planche : portrait d'abord, plans de travail ensuite.
const ORDRE_PLANS = ["portrait", "pied", "profil", "avec_barbe", "sans_barbe", "recente"];

/** Nombre de crans de l'échelle, pour dessiner la jauge au bon format. */
const CRANS: Record<string, number> = { sports: 5, langues: 6 };

const NIVEAUX_CECRL = ["A1", "A2", "B1", "B2", "C1", "C2", "LM"];

function positionNiveau(cle: string, niveau: string): number {
  if (cle === "langues") return Math.min(NIVEAUX_CECRL.indexOf(niveau) + 1, 6);
  return Number(niveau) || 0;
}

function BlocEtiquettes({
  legende,
  valeurs,
  famille,
}: {
  legende: string;
  valeurs: string[];
  famille: string;
}) {
  if (!valeurs.length) return null;
  return (
    <section className={styles.section} style={couleur(famille)}>
      <div className={styles.legende}>{legende}</div>
      <div className={styles.etiquettes}>
        {valeurs.map((v) => (
          <span key={v} className={styles.etiquette}>
            {v}
          </span>
        ))}
      </div>
    </section>
  );
}

function BlocNiveaux({
  legende,
  cle,
  champ,
  liens,
  famille,
}: {
  legende: string;
  cle: string;
  champ: string;
  liens: LienNiveau[];
  famille: string;
}) {
  if (!liens.length) return null;
  const total = CRANS[cle] ?? 4;
  return (
    <section className={styles.section} style={couleur(famille)}>
      <div className={styles.legende}>{legende}</div>
      <div className={styles.niveaux}>
        {liens.map((lien, i) => {
          const atteint = positionNiveau(cle, lien.niveau);
          return (
            <div key={i} className={styles.niveau}>
              <span className={styles.niveauNom}>
                {lien[champ]}
                {lien.accent ? ` · accent ${lien.accent}` : ""}
              </span>
              <span className={styles.niveauLibelle}>{lien.niveau_libelle}</span>
              <span className={styles.jauge} aria-hidden="true">
                {Array.from({ length: total }, (_, c) => (
                  <span key={c} className={styles.cran} data-plein={c < atteint} />
                ))}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function FicheProfil() {
  const { id } = useParams();
  const session = useSession();
  const [planActif, setPlanActif] = useState(0);

  const profil = useQuery({
    queryKey: ["profil", id],
    queryFn: async () => {
      const reponse = await fetch(`/api/profils/${id}/`, { credentials: "same-origin" });
      if (reponse.status === 403 || reponse.status === 401) throw new Error("NON_AUTHENTIFIE");
      if (reponse.status === 404) throw new Error("INTROUVABLE");
      if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
      return await reponse.json();
    },
  });

  const d = profil.data;
  const photos: Photo[] = [...((d?.photos ?? []) as Photo[])].sort(
    (a, b) => ORDRE_PLANS.indexOf(a.type) - ORDRE_PLANS.indexOf(b.type),
  );
  const photo = photos[planActif] ?? photos[0] ?? null;

  const vitals: [string, string | number | null | undefined][] = d
    ? [
        ["Âge", d.age],
        ["Paraît", d.age_apparent_min ? `${d.age_apparent_min}–${d.age_apparent_max} ans` : null],
        ["Taille", d.taille_cm ? `${d.taille_cm} cm` : null],
        ["Poids", d.poids_kg ? `${d.poids_kg} kg` : null],
        ["Pointure", d.pointure],
        ["Vêtement", d.taille_vetement],
        ["Poitrine", d.tour_poitrine_cm ? `${d.tour_poitrine_cm} cm` : null],
        ["Taille (tour)", d.tour_taille_cm ? `${d.tour_taille_cm} cm` : null],
        ["Hanches", d.tour_hanches_cm ? `${d.tour_hanches_cm} cm` : null],
        ["Yeux", d.couleur_yeux],
        ["Cheveux", d.couleur_cheveux],
        ["Tournages", d.nombre_tournages],
      ]
    : [];

  const signes = d
    ? (
        [
          [d.barbe, "Barbe"],
          [d.moustache, "Moustache"],
          [d.lunettes, "Lunettes"],
          [d.lentilles, "Lentilles"],
          [d.tatouages_visibles, "Tatouages visibles"],
          [d.piercings, "Piercings"],
          [d.cheveux_colores, "Cheveux colorés"],
          [d.profil_multiculturel, "Profil multiculturel"],
        ] as [boolean, string][]
      )
        .filter(([actif]) => actif)
        .map(([, libelle]) => libelle)
    : [];

  return (
    <>
      <EnTete contexte="Fiche profil" />
      <div className={styles.page}>
        {profil.isPending && <div className={styles.etat}>Chargement de la fiche…</div>}

        {profil.isError && (
          <div className={styles.etat}>
            {(profil.error as Error).message === "NON_AUTHENTIFIE" ? (
              <>
                <strong>Session requise</strong>
                <Link to={lienConnexion(`/profils/${id}`)}>Se connecter</Link> pour consulter cette
                fiche.
              </>
            ) : (profil.error as Error).message === "INTROUVABLE" ? (
              <>
                <strong>Profil introuvable</strong>
                Ce profil n'existe pas ou a été supprimé.{" "}
                <Link to="/recherche">Retour à la planche</Link>
              </>
            ) : (
              <>
                <strong>Erreur</strong>
                {(profil.error as Error).message}
              </>
            )}
          </div>
        )}

        {d && (
          <>
            <nav className={styles.filAriane}>
              <Link to="/recherche">← Planche</Link>
              <span>·</span>
              <span>{d.reference ?? `#${d.id}`}</span>
            </nav>

            <div className={styles.colonnes}>
              <div className={styles.galerie}>
                <div className={styles.planPrincipal}>
                  {photo ? (
                    <>
                      <img key={photo.id} src={photo.url} alt={photo.type_libelle} />
                      <div className={styles.etiquettePlan}>
                        {photo.type_libelle}
                        {photo.prise_le ? ` · ${photo.prise_le}` : ""}
                      </div>
                    </>
                  ) : (
                    <div className={styles.sansPhoto}>Aucune photo</div>
                  )}
                </div>

                {photos.length > 1 && (
                  <div className={styles.vignettes}>
                    {photos.map((p, i) => (
                      <button
                        key={p.id}
                        type="button"
                        className={styles.vignette}
                        data-actif={i === planActif}
                        onClick={() => setPlanActif(i)}
                        title={p.type_libelle}
                      >
                        <img src={p.url} alt={p.type_libelle} loading="lazy" />
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <div className={styles.identite}>
                  <h1 className={styles.nom}>
                    {d.prenom} {d.nom}
                  </h1>
                  <div className={styles.sousTitre}>
                    {d.est_mineur && <span className={styles.badgeMineur}>Mineur</span>}
                    {d.nom_artiste && <span>« {d.nom_artiste} »</span>}
                    {d.sexe && <span>{d.sexe === "F" ? "Femme" : d.sexe === "H" ? "Homme" : "Autre"}</span>}
                    {d.ville && (
                      <span>
                        {d.ville}
                        {d.departement ? ` (${d.departement.code})` : ""}
                      </span>
                    )}
                    {d.departement?.region && <span>{d.departement.region}</span>}
                    {!d.actif && <span>Archivé</span>}
                  </div>
                </div>

                <div className={styles.actions}>
                  {session.data?.peut_saisir && (
                    <Link className={styles.actionPrincipale} to={`/profils/${d.id}/modifier`}>
                      Modifier
                    </Link>
                  )}
                  <Link className={styles.actionSecondaire} to="/recherche">
                    Retour à la planche
                  </Link>
                </div>

                {d.est_mineur && (
                  <div className={styles.alerteMineur}>
                    <strong>Profil mineur</strong>
                    Autorisation parentale{" "}
                    {d.mineur?.autorisation_parentale_signee ? "signée" : "non signée"}, autorisation
                    de travail {d.mineur?.autorisation_travail_obtenue ? "obtenue" : "non obtenue"}.
                    Le détail du responsable légal se consulte dans l'admin.
                  </div>
                )}

                <dl className={styles.vitals}>
                  {vitals
                    .filter(([, v]) => v !== null && v !== undefined && v !== "")
                    .map(([libelle, valeur]) => (
                      <div key={libelle} className={styles.vital}>
                        <dt>{libelle}</dt>
                        <dd>{valeur}</dd>
                      </div>
                    ))}
                </dl>

                <section className={styles.section} style={couleur("identite")}>
                  <div className={styles.legende}>Contact & disponibilité</div>
                  <dl className={styles.paires}>
                    {d.telephone && (
                      <div className={styles.paire}>
                        <dt>Téléphone</dt>
                        <dd>
                          <a href={`tel:${d.telephone}`}>{d.telephone}</a>
                        </dd>
                      </div>
                    )}
                    {d.email && (
                      <div className={styles.paire}>
                        <dt>E-mail</dt>
                        <dd>
                          <a href={`mailto:${d.email}`}>{d.email}</a>
                        </dd>
                      </div>
                    )}
                    {d.disponibilite && (
                      <div className={styles.paire}>
                        <dt>Disponibilité</dt>
                        <dd>{d.disponibilite}</dd>
                      </div>
                    )}
                    {d.composition && (
                      <div className={styles.paire}>
                        <dt>Composition</dt>
                        <dd>{d.composition}</dd>
                      </div>
                    )}
                    {d.distance_max_km != null && (
                      <div className={styles.paire}>
                        <dt>Déplacement max</dt>
                        <dd>{d.distance_max_km} km</dd>
                      </div>
                    )}
                    <div className={styles.paire}>
                      <dt>Mobilité</dt>
                      <dd>
                        {[
                          d.peut_dormir_sur_place && "dort sur place",
                          d.vehicule_personnel_disponible && "véhicule personnel",
                          d.besoin_transport && "besoin d'un transport",
                        ]
                          .filter(Boolean)
                          .join(", ") || "—"}
                      </dd>
                    </div>
                  </dl>
                </section>

                <BlocEtiquettes legende="Apparence" valeurs={d.apparences} famille="apparence" />
                <BlocEtiquettes legende="Registres" valeurs={d.registres} famille="apparence" />
                {signes.length > 0 && (
                  <BlocEtiquettes legende="Signes particuliers" valeurs={signes} famille="physique" />
                )}

                <BlocNiveaux
                  legende="Sports"
                  cle="sports"
                  champ="sport"
                  liens={d.sports}
                  famille="sport"
                />
                <BlocNiveaux
                  legende="Langues"
                  cle="langues"
                  champ="langue"
                  liens={d.langues}
                  famille="langue"
                />
                <BlocNiveaux
                  legende="Compétences artistiques"
                  cle="artistiques"
                  champ="competence"
                  liens={d.competences_artistiques}
                  famille="experience"
                />
                <BlocNiveaux
                  legende="Instruments"
                  cle="instruments"
                  champ="instrument"
                  liens={d.instruments}
                  famille="experience"
                />

                <BlocEtiquettes legende="Métiers" valeurs={d.metiers} famille="metier" />
                <BlocEtiquettes
                  legende="Compétences particulières"
                  valeurs={d.competences_particulieres}
                  famille="metier"
                />
                <BlocEtiquettes legende="Costumes" valeurs={d.costumes} famille="apparence" />
                <BlocEtiquettes
                  legende="Permis"
                  valeurs={d.permis}
                  famille="mobilite"
                />
                <BlocEtiquettes
                  legende="Conduite"
                  valeurs={d.competences_conduite}
                  famille="mobilite"
                />
                <BlocEtiquettes
                  legende="Zones de mobilité"
                  valeurs={d.zones_mobilite}
                  famille="mobilite"
                />
                <BlocEtiquettes
                  legende="Expérience de tournage"
                  valeurs={d.types_experience}
                  famille="experience"
                />
                <BlocEtiquettes
                  legende="Prestations acceptées"
                  valeurs={d.prestations_acceptees}
                  famille="experience"
                />

                {d.vehicules?.length > 0 && (
                  <BlocEtiquettes
                    legende="Véhicules"
                    valeurs={d.vehicules.map(
                      (v: { type_vehicule: string; marque: string; modele: string; annee: number | null }) =>
                        [v.type_vehicule, v.marque, v.modele, v.annee].filter(Boolean).join(" "),
                    )}
                    famille="mobilite"
                  />
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
