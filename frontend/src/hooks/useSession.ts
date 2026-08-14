import { useQuery } from "@tanstack/react-query";
import { chargerSession } from "../api/ecriture";

/** État de connexion partagé par la planche et les écrans de saisie.
 *  `null` = personne n'est connecté ; `peut_saisir` = compte staff. */
export function useSession() {
  return useQuery({
    queryKey: ["session"],
    queryFn: chargerSession,
    retry: false,
    // Une session peut tomber à tout moment et l'accès à la saisie en dépend :
    // on revalide à chaque montage d'écran et au retour sur l'onglet.
    staleTime: 30 * 1000,
    refetchOnMount: "always",
    refetchOnWindowFocus: true,
  });
}

/** Page de connexion du front, avec retour à l'endroit d'où l'on vient. */
export function lienConnexion(retour: string) {
  return `/connexion?next=${encodeURIComponent(retour)}`;
}
