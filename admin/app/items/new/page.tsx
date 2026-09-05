import { createItemAction } from "../../actions";

export default function NewItemPage() {
  return (
    <main className="mx-auto max-w-md p-8">
      <h1 className="mb-6 text-2xl font-semibold">New item</h1>
      <form action={createItemAction} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Name
          <input
            name="name"
            required
            maxLength={200}
            className="rounded border px-2 py-1"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Description
          <input name="description" className="rounded border px-2 py-1" />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Price
          <input
            name="price"
            type="number"
            step="0.01"
            min="0"
            required
            className="rounded border px-2 py-1"
          />
        </label>
        <button
          type="submit"
          className="mt-2 rounded bg-black px-3 py-1.5 text-sm text-white dark:bg-white dark:text-black"
        >
          Create
        </button>
      </form>
    </main>
  );
}
