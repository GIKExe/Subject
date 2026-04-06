-- 1. Таблица исполнителей
CREATE TABLE artists (
	artist_id SERIAL PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	country VARCHAR(100),
	genre VARCHAR(100)
);

-- 2. Таблица альбомов
CREATE TABLE albums (
	album_id SERIAL PRIMARY KEY,
	artist_id INTEGER NOT NULL REFERENCES artists(artist_id) ON DELETE CASCADE,
	title VARCHAR(255) NOT NULL,
	release_year INTEGER NOT NULL CHECK (release_year BETWEEN 1900 AND 2026)
);

-- 3. Таблица треков
CREATE TABLE tracks (
	track_id SERIAL PRIMARY KEY,
	album_id INTEGER NOT NULL REFERENCES albums(album_id) ON DELETE CASCADE,
	title VARCHAR(255) NOT NULL,
	duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0)
);

-- 4. Таблица пользователей
CREATE TABLE users (
	user_id SERIAL PRIMARY KEY,
	login VARCHAR(50) NOT NULL UNIQUE,
	email VARCHAR(255) NOT NULL UNIQUE,
	registration_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- 5. Таблица плейлистов
CREATE TABLE playlists (
	playlist_id SERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
	title VARCHAR(255) NOT NULL,
	creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Связующая таблица: Треки в плейлистах (Many-to-Many)
CREATE TABLE playlist_tracks (
	playlist_id INTEGER NOT NULL REFERENCES playlists(playlist_id) ON DELETE CASCADE,
	track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
	added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (playlist_id, track_id)
);

-- 7. Таблица истории прослушиваний
CREATE TABLE listening_history (
	history_id BIGSERIAL PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE SET NULL,
	track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
	listened_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации аналитики
CREATE INDEX idx_history_user_id ON listening_history(user_id);
CREATE INDEX idx_history_track_id ON listening_history(track_id);
CREATE INDEX idx_history_date ON listening_history(listened_at);