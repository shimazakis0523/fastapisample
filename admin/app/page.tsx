import Link from "next/link";
import { listItems } from "@/lib/api";
import { deleteItemAction } from "./actions";

export const dynamic = "force-dynamic";

export default async function ItemsPage() {
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
                    <button type="submit" className="ml-2 text-red-600 underline">
                      Delete
                    </button>
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
