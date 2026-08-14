import { type ReactNode, useRef } from "react";
import { Link, useLocation } from "react-router-dom";
import { lienConnexion, useSession } from "../hooks/useSession";
import styles from "./GardeSaisie.module.css";

/** Garde d'affichage pour les écrans de saisie.
 *
 *  Purement ergonomique : la vraie protection est côté serveur (écriture réservée
 *  au staff + CSRF). Elle évite d'afficher un formulaire qui échouerait à l'envoi.
 */
export function GardeSaisie({ children }: { children: ReactNode }) {
  const session = useSession();
  const emplacement = useLocation();
  const retour = emplacement.pathname + emplacement.search;

  // On n'ouvre pas la saisie sur un état de session mis en cache : tant que le
  // serveur n'a pas répondu depuis l'arrivée sur cet écran, on attend. Sans ça,
  // naviguer depuis la planche affichait le formulaire avec une session périmée.
  const arrivee = useRef(Date.now());
  const confirmee =
    session.dataUpdatedAt >= arrivee.current || session.errorUpdatedAt >= arrivee.current;

  if (session.isPending || !confirmee) {
    return <div className={styles.attente}>Vérification de la session…</div>;
  }

  if (session.isError || !session.data) {
    return (
      <div className={styles.page}>
        <div className={styles.carte}>
          <div className={styles.legende}>Accès réservé</div>
          <h1 className={styles.titre}>Connexion requise</h1>
          <p className={styles.texte}>
            La saisie des profils est réservée aux comptes administrateurs. Connecte-toi pour
            continuer : tu reviendras directement sur cet écran.
          </p>
          <div className={styles.actions}>
            <Link className={styles.connexion} to={lienConnexion(retour)}>
              Se connecter
            </Link>
            <Link className={styles.retour} to="/recherche">
              ← Retour à la planche
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!session.data.peut_saisir) {
    return (
      <div className={styles.page}>
        <div className={styles.carte} data-refus="true">
          <div className={styles.legende}>Droits insuffisants</div>
          <h1 className={styles.titre}>Saisie non autorisée</h1>
          <p className={styles.texte}>
            Ce compte peut consulter la base, mais pas la modifier. Demande un accès
            administrateur, ou connecte-toi avec un autre compte.
          </p>
          <div className={styles.actions}>
            <Link className={styles.connexion} to={lienConnexion(retour)}>
              Changer de compte
            </Link>
            <Link className={styles.retour} to="/recherche">
              ← Retour à la planche
            </Link>
          </div>
          <p className={styles.compte} style={{ marginTop: 14 }}>
            Connecté en tant que {session.data.utilisateur}
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
