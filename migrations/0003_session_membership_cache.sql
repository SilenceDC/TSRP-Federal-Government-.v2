ALTER TABLE sessions ADD COLUMN member_roles_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE sessions ADD COLUMN member_verified_at INTEGER NOT NULL DEFAULT 0;
ALTER TABLE sessions ADD COLUMN member_guild_id TEXT NOT NULL DEFAULT '';
