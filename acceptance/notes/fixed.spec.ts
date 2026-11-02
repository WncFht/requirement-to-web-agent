// Independent notes-task assertions. Never supplied to the generating agent.
import { test as base, expect } from "@playwright/test";
import { randomUUID } from "node:crypto";
import { createDatabaseClient } from "../../../backend/src/db/client.js";
import { initializeDatabase } from "../../../backend/src/db/initialize.js";
function db() {
    return createDatabaseClient(process.env.ARC_E2E_DB_FILE!);
}
function snapshot() {
    const d = db();
    try {
        return d
            .prepare(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
            )
            .all()
            .map((r: any) => ({
                table: r.name,
                rows: d
                    .prepare(
                        'SELECT * FROM "' + r.name.replaceAll('"', '""') + '"',
                    )
                    .all(),
            }));
    } finally {
        d.close();
    }
}
const test = base.extend<{ resetState: void }>({
    resetState: [
        async ({}, use) => {
            const d = db();
            try {
                initializeDatabase(d);
                d.pragma("foreign_keys=OFF");
                for (const r of d
                    .prepare(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
                    )
                    .all() as any[])
                    d.exec(
                        'DELETE FROM "' + r.name.replaceAll('"', '""') + '"',
                    );
                d.pragma("foreign_keys=ON");
            } finally {
                d.close();
            }
            await use();
        },
        { auto: true },
    ],
});
async function save(page: any, title: string) {
    const input = page.getByRole("textbox", { name: "Title", exact: true });
    await expect(input).toBeVisible();
    await input.fill(title);
    await page.getByRole("button", { name: "Save", exact: true }).click();
}
test("N01 exact controls and read-only empty homepage", async ({ page }) => {
    const before = snapshot();
    await page.goto("/");
    await expect(
        page.getByRole("heading", { name: "Notes", exact: true }),
    ).toBeVisible();
    await expect(
        page.getByRole("textbox", { name: "Title", exact: true }),
    ).toBeVisible();
    await expect(
        page.getByRole("button", { name: "Save", exact: true }),
    ).toBeVisible();
    await page.reload();
    expect(snapshot()).toEqual(before);
});
test("N02 one real record and reload persistence", async ({ page }) => {
    const title = "note-" + randomUUID();
    await page.goto("/");
    await save(page, title);
    await expect(
        page.getByRole("listitem").filter({ hasText: title }),
    ).toHaveCount(1);
    const stored = snapshot();
    expect(
        stored
            .flatMap((r) => r.rows)
            .filter((r) => Object.values(r as any).includes(title)),
    ).toHaveLength(1);
    await page.reload();
    await expect(
        page.getByRole("listitem").filter({ hasText: title }),
    ).toHaveCount(1);
    expect(snapshot()).toEqual(stored);
});
test("N03 whitespace rejection leaves existing records unchanged", async ({
    page,
}) => {
    await page.goto("/");
    await save(page, "existing-" + randomUUID());
    await expect(page.getByRole("listitem")).toHaveCount(1);
    const before = snapshot();
    await save(page, "   ");
    await expect(page.getByRole("alert")).toBeVisible();
    await expect(page.getByRole("alert")).not.toHaveText("");
    expect(snapshot()).toEqual(before);
});
test("N04 duplicate titles create distinct records", async ({ page }) => {
    const title = "duplicate-" + randomUUID();
    await page.goto("/");
    await save(page, title);
    await expect(page.getByRole("listitem")).toHaveCount(1);
    await save(page, title);
    await expect(page.getByRole("listitem")).toHaveCount(2);
    expect(
        snapshot()
            .flatMap((r) => r.rows)
            .filter((r) => Object.values(r as any).includes(title)),
    ).toHaveLength(2);
    await page.reload();
    await expect(page.getByRole("listitem")).toHaveCount(2);
});
test("N05 Unicode and spaces survive in storage", async ({ page }) => {
    const title = "  中文 Café " + randomUUID() + "  ";
    await page.goto("/");
    await save(page, title);
    await expect(page.getByRole("listitem")).toHaveCount(1);
    expect(
        snapshot()
            .flatMap((r) => r.rows)
            .filter((r) => Object.values(r as any).includes(title)),
    ).toHaveLength(1);
    await page.reload();
    await expect(page.getByRole("listitem")).toContainText("中文 Café");
});
