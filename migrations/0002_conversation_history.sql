CREATE TABLE IF NOT EXISTS conversations (
  conversation_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL DEFAULT 'New conversation',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
  ON conversations(user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS messages (
  message_id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created
  ON messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_messages_user
  ON messages(user_id);
