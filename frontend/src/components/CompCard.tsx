import { Link } from "react-router-dom";
import type { ProfilListe } from "../api/client";
import styles from "./CompCard.module.css";

type Props = {
  profil: ProfilListe;
  index: number;
  select: boolean;
  onSelect: (id: number) => void;
  peutSaisir: boolean;
};

const LIBELLE_SEXE: Record<string, string> = { H: "H", F: "F", A: "A" };

export function CompCard({ profil, index, select, onSelect, peutSaisir }: Props) {
  const portrait =
    profil.photos.find((p) => p.type === "portrait") ?? profil.photos[0] ?? null;
  const alternatifs = profil.photos.filter((p) => p !== portrait).slice(0, 3);
  const numero = String(index + 1).padStart(3, "0");

  return (
    <article
      className={styles.carte}
      data-select={select}
      // Position dans la planche : sert au décalage d'apparition en cascade.
      style={{ ["--index" as string]: index % 24 }}
    >
      <button
        type="button"
        className={styles.zoneSelect}
        aria-pressed={select}
        onClick={() => onSelect(profil.id)}
        title="Marquer comme select"
      >
        <span className={styles.cadre}>
        {portrait ? (
          <img src={portrait.url} alt="" loading="lazy" />
        ) : (
          <span className={styles.sansPhoto}>Sans photo</span>
        )}
        <span className={styles.index}>{numero}</span>
        {profil.age != null && profil.age < 18 && (
          <span className={styles.badgeMineur}>Mineur</span>
        )}
        {profil.apparences.length > 0 && (
          <span className={styles.apparence}>{profil.apparences.join(" · ")}</span>
        )}
        {select && (
          <svg className={styles.cercle} viewBox="0 0 200 250" aria-hidden="true">
            <ellipse cx="100" cy="125" rx="88" ry="112" transform="rotate(-4 100 125)" />
          </svg>
        )}
        </span>
      </button>

      <div className={styles.identite}>
        <Link className={styles.nom} to={`/profils/${profil.id}`}>
          {profil.prenom} {profil.nom}
        </Link>
        {profil.nom_artiste && <div className={styles.nomArtiste}>« {profil.nom_artiste} »</div>}
      </div>

      <dl className={styles.vitals}>
        <div>
          <dt>Âge</dt>
          <dd>{profil.age ?? "—"}</dd>
        </div>
        <div>
          <dt>Taille</dt>
          <dd>{profil.taille_cm ? `${profil.taille_cm}` : "—"}</dd>
        </div>
        <div>
          <dt>Sexe</dt>
          <dd>{profil.sexe ? (LIBELLE_SEXE[profil.sexe] ?? profil.sexe) : "—"}</dd>
        </div>
        <div>
          <dt>Dépt</dt>
          <dd>{profil.departement ?? "—"}</dd>
        </div>
        <div>
          <dt>Yeux</dt>
          <dd>{profil.couleur_yeux || "—"}</dd>
        </div>
        <div>
          <dt>Réf</dt>
          <dd>{profil.reference ?? "—"}</dd>
        </div>
      </dl>

      <div className={styles.pied}>
        <div className={styles.plans}>
          {alternatifs.map((photo) => (
            <img key={photo.id} src={photo.url} alt="" loading="lazy" title={photo.type_libelle} />
          ))}
        </div>
        <span className={styles.liensPied}>
          <Link className={styles.modifier} to={`/profils/${profil.id}`}>
            Voir la fiche
          </Link>
          {peutSaisir && (
            <Link className={styles.modifier} to={`/profils/${profil.id}/modifier`}>
              Modifier
            </Link>
          )}
        </span>
      </div>
    </article>
  );
}
