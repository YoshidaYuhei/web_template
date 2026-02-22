import { test, expect } from "@playwright/test";

function uniqueEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `e2e-${timestamp}-${random}@example.com`;
}

test.describe("サインアップページ", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/signup");
  });

  test("サインアップフォームが正しく表示される", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "アカウント作成" }),
    ).toBeVisible();
    await expect(page.getByLabel("メールアドレス")).toBeVisible();
    await expect(page.getByLabel("パスワード")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "サインアップ" }),
    ).toBeVisible();
  });

  test.describe("クライアントサイドバリデーション", () => {
    test("メールアドレス空で送信するとエラーが表示される", async ({
      page,
    }) => {
      await page.getByLabel("パスワード").fill("password123");
      await page.getByRole("button", { name: "サインアップ" }).click();

      await expect(
        page.getByText("メールアドレスを入力してください"),
      ).toBeVisible();
    });

    test("メール形式が不正だとエラーが表示される", async ({ page }) => {
      await page.getByLabel("メールアドレス").fill("invalid-email");
      await page.getByLabel("パスワード").fill("password123");
      await page.getByRole("button", { name: "サインアップ" }).click();

      await expect(
        page.getByText("有効なメールアドレスを入力してください"),
      ).toBeVisible();
    });

    test("パスワード空で送信するとエラーが表示される", async ({ page }) => {
      await page.getByLabel("メールアドレス").fill(uniqueEmail());
      await page.getByRole("button", { name: "サインアップ" }).click();

      await expect(
        page.getByText("パスワードを入力してください"),
      ).toBeVisible();
    });

    test("パスワードが8文字未満だとエラーが表示される", async ({ page }) => {
      await page.getByLabel("メールアドレス").fill(uniqueEmail());
      await page.getByLabel("パスワード").fill("short");
      await page.getByRole("button", { name: "サインアップ" }).click();

      await expect(
        page.getByText("パスワードは8文字以上で入力してください"),
      ).toBeVisible();
    });
  });

  test("正常なサインアップでダッシュボードに遷移する", async ({ page }) => {
    await page.getByLabel("メールアドレス").fill(uniqueEmail());
    await page.getByLabel("パスワード").fill("password123");
    await page.getByRole("button", { name: "サインアップ" }).click();

    await expect(page).toHaveURL("/");
    await expect(
      page.getByRole("heading", { name: "ダッシュボード" }),
    ).toBeVisible();
  });

  test("重複メールアドレスでエラーが表示される", async ({ page }) => {
    const email = uniqueEmail();

    // 1回目: サインアップ成功
    await page.getByLabel("メールアドレス").fill(email);
    await page.getByLabel("パスワード").fill("password123");
    await page.getByRole("button", { name: "サインアップ" }).click();
    await expect(page).toHaveURL("/");

    // 2回目: 同じメールで再度サインアップ
    await page.goto("/signup");
    await page.getByLabel("メールアドレス").fill(email);
    await page.getByLabel("パスワード").fill("password123");
    await page.getByRole("button", { name: "サインアップ" }).click();

    await expect(
      page.getByText("このメールアドレスは既に登録されています"),
    ).toBeVisible();
  });
});
