import { notFound } from "next/navigation";
import { requireSession } from "@/lib/auth0";
import { getItem } from "@/lib/api";
import { SubmitButton } from "@/components/submit-button";
import { updateItemAction } from "../../../actions";

export default async function EditItemPage(props: PageProps<"/items/[id]/edit">) {
  await requireSession();
  const { id } = await props.params;

  const item = await getItem(Number(id)).catch(() => null);
  if (!item) notFound();

  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="mb-6 text-2xl font-semibold">Edit item #{item.id}</h1>
      <form action={updateItemAction} className="flex flex-col gap-4">
        <input type="hidden" name="id" value={item.id} />
        <label className="flex flex-col gap-1 text-sm">
          Name
          <input
            name="name"
            required
            maxLength={200}
            defaultValue={item.name}
            className="rounded border px-2 py-1"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Description
          <input
            name="description"
            defaultValue={item.description ?? ""}
            className="rounded border px-2 py-1"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Price
          <input
            name="price"
            type="number"
            step="0.01"
            min="0"
            required
            defaultValue={item.price}
            className="rounded border px-2 py-1"
          />
        </label>
        <SubmitButton
          pendingText="Saving…"
          className="mt-2 rounded bg-black px-3 py-1.5 text-sm text-white disabled:opacity-50 dark:bg-white dark:text-black"
        >
          Save
        </SubmitButton>
      </form>
    </main>
  );
}
