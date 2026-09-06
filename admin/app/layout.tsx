import type { Metadata } from "next";
import { auth0 } from "@/lib/auth0";
import "./globals.css";

export const metadata: Metadata = {
  title: "fastapisample admin",
  description: "Item management admin panel",
};

export default async function RootLayout({ children }: LayoutProps<"/">) {
  const session = await auth0.getSession();
  const enterpriseConnection = process.env.AUTH0_ENTERPRISE_CONNECTION;

  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <header className="flex items-center justify-end gap-3 border-b p-3 text-sm">
          {session ? (
            <>
              <span className="text-neutral-500">{session.user.email}</span>
              <a href="/auth/logout" className="underline">
                Log out
              </a>
            </>
          ) : (
            <>
              <a href="/auth/login" className="underline">
                Log in
              </a>
              {enterpriseConnection && (
                <a
                  href={`/auth/login?connection=${encodeURIComponent(enterpriseConnection)}`}
                  className="underline"
                >
                  Log in with Entra ID
                </a>
              )}
            </>
          )}
        </header>
        {children}
      </body>
    </html>
  );
}
