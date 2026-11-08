CREATE TABLE IF NOT EXISTS announcements (
  announcement_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  author_id TEXT NOT NULL,
  author_name TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  published_at INTEGER NOT NULL,
  is_published INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_announcements_published
  ON announcements(is_published, published_at DESC);
