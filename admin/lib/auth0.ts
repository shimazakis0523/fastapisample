import { redirect } from "next/navigation";
import { Auth0Client } from "@auth0/nextjs-auth0/server";

export const auth0 = new Auth0Client({
  authorizationParameters: {
    audience: process.env.AUTH0_AUDIENCE,
  },
});

export async function requireSession() {
  const session = await auth0.getSession();
  if (!session) {
    redirect("/auth/login");
  }
  return session;
}
