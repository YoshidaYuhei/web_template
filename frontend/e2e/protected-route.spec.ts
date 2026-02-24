import { test, expect } from "@playwright/test";

test.describe("保護されたルート", () => {
  test("未ログインでダッシュボードにアクセスするとログインページにリダイレクトされる", async ({
    page,
  }) => {
    // localStorageをクリアした状態でダッシュボードにアクセス
    await page.goto("/");

    await expect(page).toHaveURL("/login");
    await expect(
      page.getByRole("heading", { name: "ログイン" }),
    ).toBeVisible();
  });
});
