import Link from "next/link";
import { auth0 } from "@/lib/auth0";
import { listItems } from "@/lib/api";
import { SubmitButton } from "@/components/submit-button";
import { deleteItemAction } from "./actions";

export const dynamic = "force-dynamic";

export default async function ItemsPage(props: PageProps<"/">) {
  const session = await auth0.getSession();
  const { error } = await props.searchParams;

  // Unlike the other pages, the root page must not hard-redirect to
  // /auth/login: doing so would skip rendering this page's own login
  // buttons entirely.
  if (!session) {
    const enterpriseConnection = process.env.AUTH0_ENTERPRISE_CONNECTION;
    return (
      <main className="mx-auto flex max-w-md flex-col items-center gap-6 p-8 text-center">
        <h1 className="text-2xl font-semibold">fastapisample admin</h1>
        <p className="text-sm text-neutral-500">Please log in to continue.</p>
        <div className="flex w-full flex-col gap-3">
          <a
            href="/auth/login"
            className="rounded bg-black px-4 py-2 text-sm text-white dark:bg-white dark:text-black"
          >
            Log in
          </a>
          {enterpriseConnection && (
            <a
              href={`/auth/login?connection=${encodeURIComponent(enterpriseConnection)}`}
              className="rounded border border-black px-4 py-2 text-sm dark:border-white"
            >
              Log in with Entra ID
            </a>
          )}
        </div>
      </main>
    );
  }

  const items = await listItems();

  return (
    <main className="mx-auto max-w-3xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Items</h1>
        <Link
          href="/items/new"
          className="rounded bg-black px-3 py-1.5 text-sm text-white dark:bg-white dark:text-black"
        >
          + New item
        </Link>
      </div>

      {error === "forbidden" && (
        <p className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">
          You don&apos;t have permission to delete this item.
        </p>
      )}

      {items.length === 0 ? (
        <p className="text-sm text-neutral-500">No items yet.</p>
      ) : (
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="p-2">ID</th>
              <th className="p-2">Name</th>
              <th className="p-2">Description</th>
              <th className="p-2">Price</th>
              <th className="p-2" />
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className="border-b">
                <td className="p-2">{item.id}</td>
                <td className="p-2">{item.name}</td>
                <td className="p-2 text-neutral-500">{item.description ?? "-"}</td>
                <td className="p-2">{item.price}</td>
                <td className="p-2 whitespace-nowrap">
                  <Link href={`/items/${item.id}/edit`} className="underline">
                    Edit
                  </Link>{" "}
                  <form action={deleteItemAction} className="inline">
                    <input type="hidden" name="id" value={item.id} />
                    <SubmitButton
                      pendingText="Deleting…"
                      className="ml-2 text-red-600 underline disabled:opacity-50"
                    >
                      Delete
                    </SubmitButton>
                  </form>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
