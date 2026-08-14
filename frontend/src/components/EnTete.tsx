import { useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { seDeconnecter } from "../api/ecriture";
import { lienConnexion, useSession } from "../hooks/useSession";
import styles from "./EnTete.module.css";

/** Barre commune à tous les écrans : identité de l'outil, état de session, action. */
export function EnTete({ contexte }: { contexte?: string }) {
  const session = useSession();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const connecte = Boolean(session.data);

  async function deconnexion() {
    await seDeconnecter();
    queryClient.clear();
    navigate("/connexion", { replace: true });
  }

  return (
    <header className={styles.barre}>
      <Link className={styles.marque} to="/recherche">
        <span className={styles.pastille} aria-hidden="true" />
        <span className={styles.titre}>Casting</span>
      </Link>

      {contexte && (
        <>
          <span className={styles.separateur} aria-hidden="true" />
          <span className={styles.contexte}>{contexte}</span>
        </>
      )}

      <span className={styles.espace} />

      <span className={styles.compte}>
        <span className={styles.temoin} data-hors-ligne={!connecte} aria-hidden="true" />
        {connecte ? session.data?.utilisateur : "hors session"}
      </span>

      {connecte ? (
        <button type="button" className={styles.lien} onClick={deconnexion}>
          Déconnexion
        </button>
      ) : (
        <Link className={styles.lien} to={lienConnexion("/recherche")}>
          Connexion
        </Link>
      )}

      <Link className={styles.action} to="/profils/nouveau">
        Nouveau profil
      </Link>
    </header>
  );
}
