import { Link } from "react-router-dom";
import { CompCard } from "../../components/CompCard";
import { lienConnexion } from "../../hooks/useSession";
import styles from "./ResultatsRecherche.module.css";
import type { useRecherche } from "./useRecherche";

type Recherche = ReturnType<typeof useRecherche>;
const PAR_PAGE = 24;

export function ResultatsRecherche({
  recherche,
  selects,
  onSelect,
  peutSaisir,
}: {
  recherche: Recherche;
  selects: Set<number>;
  onSelect: (id: number) => void;
  peutSaisir: boolean;
}) {
  const { query, page, allerPage } = recherche;
  const donnees = query.data;
  const total = donnees?.count ?? 0;
  const dernierePage = Math.max(1, Math.ceil(total / PAR_PAGE));

  return (
    <main className={styles.planche}>
      <div className={styles.entete}>
        <h1 className={styles.titre}>Planche</h1>
        <div className={styles.compte}>
          {query.isFetching && <span className={styles.chargement} aria-hidden="true" />}
          {query.isPending ? "Lecture de la base…" : `${total} profil${total > 1 ? "s" : ""}`}
          {selects.size > 0 && <span className={styles.selects}>· {selects.size} select(s)</span>}
        </div>
      </div>
      <div className={styles.perforations} aria-hidden="true" />

      {query.isPending && (
        <div className={styles.squelettes}>
          {Array.from({ length: 8 }, (_, i) => (
            <div key={i} className={styles.squelette} style={{ ["--index" as string]: i }} />
          ))}
        </div>
      )}

      {query.isError && (
        <div className={styles.etat}>
          {(query.error as Error).message === "NON_AUTHENTIFIE" ? (
            <>
              <strong>Session requise</strong>
              L'API ne sert pas de données personnelles à un visiteur anonyme.
              <br />
              <Link to={lienConnexion("/recherche")}>Se connecter</Link> pour afficher la planche.
            </>
          ) : (
            <>
              <strong>Erreur</strong>
              {(query.error as Error).message}
            </>
          )}
        </div>
      )}

      {!query.isError && donnees && donnees.results.length === 0 && (
        <div className={styles.etat}>
          <strong>Planche vide</strong>
          Aucun profil ne correspond. Retire un filtre dans la feuille de casting.
        </div>
      )}

      {/* `keepPreviousData` conserve la planche précédente pendant un refetch :
          en cas d'erreur (session perdue), il faut donc l'écarter explicitement,
          sinon des cartes périmées restent affichées sous le message d'erreur. */}
      {!query.isError && donnees && donnees.results.length > 0 && (
        <>
          <div className={styles.grille}>
            {donnees.results.map((profil, position) => (
              <CompCard
                key={profil.id}
                profil={profil}
                index={(page - 1) * PAR_PAGE + position}
                select={selects.has(profil.id)}
                onSelect={onSelect}
                peutSaisir={peutSaisir}
              />
            ))}
          </div>

          {dernierePage > 1 && (
            <nav className={styles.pagination}>
              <button type="button" disabled={page <= 1} onClick={() => allerPage(page - 1)}>
                ← Planche précédente
              </button>
              <span>
                {page} / {dernierePage}
              </span>
              <button
                type="button"
                disabled={page >= dernierePage}
                onClick={() => allerPage(page + 1)}
              >
                Planche suivante →
              </button>
            </nav>
          )}
        </>
      )}
    </main>
  );
}
