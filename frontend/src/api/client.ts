import createClient from "openapi-fetch";
import type { components, paths } from "./types";

// Même origine que l'API grâce au proxy Vite : le cookie de session suit.
export const api = createClient<paths>({ baseUrl: "/api", credentials: "same-origin" });

export type ProfilListe = components["schemas"]["ProfilListe"];
export type ProfilDetail = components["schemas"]["ProfilDetail"];
export type Photo = components["schemas"]["Photo"];
export type Sport = components["schemas"]["Sport"];
export type Reference = components["schemas"]["Apparence"];
export type Departement = components["schemas"]["Departement"];
