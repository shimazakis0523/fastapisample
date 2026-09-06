"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { requireSession } from "@/lib/auth0";
import { createItem, deleteItem, updateItem } from "@/lib/api";

function readItemInput(formData: FormData) {
  const description = String(formData.get("description") ?? "").trim();
  return {
    name: String(formData.get("name") ?? "").trim(),
    description: description === "" ? null : description,
    price: Number(formData.get("price")),
  };
}

export async function createItemAction(formData: FormData): Promise<void> {
  // Server Actions are POST endpoints reachable by anyone who knows the action
  // ID, not just users who saw the form — the page render check alone isn't
  // a security boundary, so every action re-checks the session itself.
  await requireSession();
  await createItem(readItemInput(formData));
  revalidatePath("/");
  redirect("/");
}

export async function updateItemAction(formData: FormData): Promise<void> {
  await requireSession();
  const id = Number(formData.get("id"));
  await updateItem(id, readItemInput(formData));
  revalidatePath("/");
  redirect("/");
}

export async function deleteItemAction(formData: FormData): Promise<void> {
  await requireSession();
  const id = Number(formData.get("id"));
  await deleteItem(id);
  revalidatePath("/");
}
