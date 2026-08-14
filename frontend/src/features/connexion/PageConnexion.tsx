import { useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { seConnecter } from "../../api/ecriture";
import { useSession } from "../../hooks/useSession";
import styles from "./PageConnexion.module.css";

export function PageConnexion() {
  // Monte la session avant tout envoi : c'est ce GET qui pose le cookie CSRF.
  const session = useSession();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [identifiant, setIdentifiant] = useState("");
  const [motDePasse, setMotDePasse] = useState("");
  const [erreur, setErreur] = useState<string | null>(null);
  const [envoi, setEnvoi] = useState(false);

  const retour = params.get("next") ?? "/recherche";
  const dejaConnecte = Boolean(session.data?.utilisateur);

  async function soumettre(evenement: FormEvent) {
    evenement.preventDefault();
    setEnvoi(true);
    setErreur(null);
    try {
      await seConnecter(identifiant, motDePasse);
      await queryClient.invalidateQueries({ queryKey: ["session"] });
      queryClient.clear();
      navigate(retour, { replace: true });
    } catch (e) {
      setErreur((e as Error).message);
      setMotDePasse("");
    } finally {
      setEnvoi(false);
    }
  }

  return (
    <div className={styles.page} data-erreur={Boolean(erreur)}>
      <div className={styles.panneau}>
        <div className={styles.perforations} aria-hidden="true" />

        <div className={styles.marque}>
          <span className={styles.pastille} aria-hidden="true" />
          <span className={styles.titre}>Casting</span>
        </div>
        <p className={styles.accroche}>Base de profils — accès réservé</p>

        {dejaConnecte && (
          <p className={styles.deja}>
            Session déjà ouverte : {session.data?.utilisateur}.{" "}
            <Link to={retour}>Continuer →</Link>
          </p>
        )}

        {erreur && (
          <div className={styles.erreur} role="alert">
            {erreur}
          </div>
        )}

        <form onSubmit={soumettre}>
          <div className={styles.champ}>
            <label htmlFor="identifiant">Identifiant</label>
            <input
              id="identifiant"
              name="username"
              autoComplete="username"
              value={identifiant}
              onChange={(e) => setIdentifiant(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className={styles.champ}>
            <label htmlFor="mot_de_passe">Mot de passe</label>
            <input
              id="mot_de_passe"
              name="password"
              type="password"
              autoComplete="current-password"
              value={motDePasse}
              onChange={(e) => setMotDePasse(e.target.value)}
              required
            />
          </div>

          <button type="submit" className={styles.bouton} disabled={envoi}>
            {envoi ? "Connexion…" : "Entrer"}
          </button>
        </form>

        <div className={styles.pied}>
          <span>Back-office</span>
          <a href="/admin/">Admin Django →</a>
        </div>
      </div>
    </div>
  );
}
