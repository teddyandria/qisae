import { useState } from "react";
import { EnTete } from "../../components/EnTete";
import { useSession } from "../../hooks/useSession";
import { PanneauFiltres } from "./PanneauFiltres";
import { ResultatsRecherche } from "./ResultatsRecherche";
import { useRecherche } from "./useRecherche";

export function PageRecherche() {
  const recherche = useRecherche();
  const session = useSession();
  // Les selects sont un marquage de travail : pas d'écriture API en Phase 1.
  const [selects, setSelects] = useState<Set<number>>(new Set());

  // Une 403 sur la recherche signifie que la session est tombée : on retire les
  // actions de saisie sans attendre que l'état de session mis en cache expire.
  const sessionPerdue =
    recherche.query.isError && (recherche.query.error as Error).message === "NON_AUTHENTIFIE";
  const peutSaisir = Boolean(session.data?.peut_saisir) && !sessionPerdue;

  function basculerSelect(id: number) {
    setSelects((precedents) => {
      const suivants = new Set(precedents);
      if (suivants.has(id)) suivants.delete(id);
      else suivants.add(id);
      return suivants;
    });
  }

  return (
    <>
      <EnTete contexte="Recherche" />
      <div style={{ display: "flex", alignItems: "flex-start" }}>
        <PanneauFiltres recherche={recherche} />
        <ResultatsRecherche
          recherche={recherche}
          selects={selects}
          onSelect={basculerSelect}
          peutSaisir={peutSaisir}
        />
      </div>
    </>
  );
}
