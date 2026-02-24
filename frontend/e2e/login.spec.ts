import { test, expect } from "@playwright/test";

function uniqueEmail(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8);
  return `e2e-${timestamp}-${random}@example.com`;
}

async function signupUser(
  page: import("@playwright/test").Page,
  email: string,
  password: string,
) {
  await page.goto("/signup");
  await page.getByLabel("メールアドレス").fill(email);
  await page.getByLabel("パスワード").fill(password);
  await page.getByRole("button", { name: "サインアップ" }).click();
  await expect(page).toHaveURL("/");
}

test.describe("ログインページ", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
  });

  test("ログインフォームが正しく表示される", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "ログイン" }),
    ).toBeVisible();
    await expect(page.getByLabel("メールアドレス")).toBeVisible();
    await expect(page.getByLabel("パスワード")).toBeVisible();
    await expect(
      page.getByRole("button", { name: "ログイン" }),
    ).toBeVisible();
  });

  test.describe("クライアントサイドバリデーション", () => {
    test("メールアドレス空で送信するとエラーが表示される", async ({
      page,
    }) => {
      await page.getByLabel("パスワード").fill("password123");
      await page.getByRole("button", { name: "ログイン" }).click();

      await expect(
        page.getByText("メールアドレスを入力してください"),
      ).toBeVisible();
    });

    test("パスワード空で送信するとエラーが表示される", async ({ page }) => {
      await page.getByLabel("メールアドレス").fill(uniqueEmail());
      await page.getByRole("button", { name: "ログイン" }).click();

      await expect(
        page.getByText("パスワードを入力してください"),
      ).toBeVisible();
    });
  });

  test("正常なログインでダッシュボードに遷移する", async ({ page }) => {
    const email = uniqueEmail();
    const password = "password123";

    // まずサインアップ
    await signupUser(page, email, password);

    // ログアウト
    await page.getByRole("button", { name: "ログアウト" }).click();
    await expect(page).toHaveURL("/login");

    // ログイン
    await page.getByLabel("メールアドレス").fill(email);
    await page.getByLabel("パスワード").fill(password);
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(page).toHaveURL("/");
    await expect(
      page.getByRole("heading", { name: "ダッシュボード" }),
    ).toBeVisible();
    await expect(page.getByText(email)).toBeVisible();
  });

  test("誤パスワードでエラーが表示される", async ({ page }) => {
    const email = uniqueEmail();
    const password = "password123";

    // まずサインアップ
    await signupUser(page, email, password);

    // ログアウト
    await page.getByRole("button", { name: "ログアウト" }).click();
    await expect(page).toHaveURL("/login");

    // 誤パスワードでログイン試行
    await page.getByLabel("メールアドレス").fill(email);
    await page.getByLabel("パスワード").fill("wrongpassword");
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(
      page.getByText("メールアドレスまたはパスワードが正しくありません"),
    ).toBeVisible();
  });

  test("ログアウトするとログインページにリダイレクトされる", async ({
    page,
  }) => {
    const email = uniqueEmail();
    const password = "password123";

    // サインアップ
    await signupUser(page, email, password);

    // ログアウト
    await page.getByRole("button", { name: "ログアウト" }).click();

    await expect(page).toHaveURL("/login");
  });
});
