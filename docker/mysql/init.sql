-- テスト用データベースを作成
CREATE DATABASE IF NOT EXISTS warry_about_test;

-- warry ユーザーにテスト用DBへのアクセス権限を付与
GRANT ALL PRIVILEGES ON warry_about_test.* TO 'warry'@'%';
FLUSH PRIVILEGES;
