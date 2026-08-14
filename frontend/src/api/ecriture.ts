/** Appels d'écriture : réservés au staff côté serveur, protégés par CSRF.
 *  Voir docs/decisions/0001-saisie-par-formulaires-front.md. */

function jetonCsrf(): string {
  const trouve = document.cookie
    .split(";")
    .map((c) => c.trim())
    .find((c) => c.startsWith("csrftoken="));
  return trouve ? decodeURIComponent(trouve.slice("csrftoken=".length)) : "";
}

export class ErreurValidation extends Error {
  champs: Record<string, string[]>;

  constructor(champs: Record<string, string[]>) {
    super("Validation refusée");
    this.champs = champs;
  }
}

async function envoyer(url: string, methode: string, corps: unknown) {
  const reponse = await fetch(url, {
    method: methode,
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "X-CSRFToken": jetonCsrf(),
    },
    body: JSON.stringify(corps),
  });

  if (reponse.status === 400) {
    throw new ErreurValidation(await reponse.json());
  }
  if (reponse.status === 403) {
    throw new Error("Saisie réservée aux comptes administrateurs.");
  }
  if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
  return reponse.status === 204 ? null : await reponse.json();
}

export const creerProfil = (donnees: unknown) => envoyer("/api/profils/", "POST", donnees);

export const modifierProfil = (id: number, donnees: unknown) =>
  envoyer(`/api/profils/${id}/`, "PATCH", donnees);

export const supprimerProfil = (id: number) => envoyer(`/api/profils/${id}/`, "DELETE", null);

/** Photos : multipart, donc pas de JSON ici. */
export async function televerserPhoto(profil: number, type: string, fichier: File) {
  const corps = new FormData();
  corps.append("profil", String(profil));
  corps.append("type", type);
  corps.append("image", fichier);

  const reponse = await fetch("/api/photos/", {
    method: "POST",
    credentials: "same-origin",
    headers: { "X-CSRFToken": jetonCsrf() },
    body: corps,
  });
  if (reponse.status === 400) throw new ErreurValidation(await reponse.json());
  if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
  return await reponse.json();
}

export type Session = { utilisateur: string | null; peut_saisir: boolean };

/** Toujours accessible : c'est ce GET qui pose le cookie CSRF, y compris en anonyme. */
export async function chargerSession(): Promise<Session | null> {
  const reponse = await fetch("/api/session/", {
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  if (!reponse.ok) return null;
  const etat = (await reponse.json()) as Session;
  return etat.utilisateur ? etat : null;
}

export async function seConnecter(identifiant: string, motDePasse: string) {
  const reponse = await fetch("/api/connexion/", {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "X-CSRFToken": jetonCsrf(),
    },
    body: JSON.stringify({ identifiant, mot_de_passe: motDePasse }),
  });
  if (reponse.status === 401) {
    const corps = await reponse.json().catch(() => null);
    throw new Error(corps?.detail ?? "Identifiant ou mot de passe incorrect.");
  }
  if (!reponse.ok) throw new Error(`Connexion impossible (erreur ${reponse.status}).`);
  return (await reponse.json()) as Session;
}

export async function seDeconnecter() {
  await fetch("/api/deconnexion/", {
    method: "POST",
    credentials: "same-origin",
    headers: { "X-CSRFToken": jetonCsrf() },
  });
}
