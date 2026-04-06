-- 1. Наполнение исполнителей (Artists)
INSERT INTO artists (name, country, genre) VALUES 
('Linkin Park', 'USA', 'Alternative Rock'),
('Daft Punk', 'France', 'Electronic'),
('The Weeknd', 'Canada', 'R&B');

-- 2. Наполнение альбомов (Albums)
-- Предполагаем ID: 1 - Linkin Park, 2 - Daft Punk, 3 - The Weeknd
INSERT INTO albums (artist_id, title, release_year) VALUES 
(1, 'Hybrid Theory', 2000),
(1, 'Meteora', 2003),
(2, 'Discovery', 2001),
(2, 'Random Access Memories', 2013),
(3, 'After Hours', 2020),
(3, 'Starboy', 2016);

-- 3. Наполнение треков (Tracks)
-- Hybrid Theory (Album 1)
INSERT INTO tracks (album_id, title, duration_seconds) VALUES 
(1, 'Papercut', 184),
(1, 'One Step Closer', 155),
(1, 'Crawling', 209),
(1, 'In the End', 216);

-- Meteora (Album 2)
INSERT INTO tracks (album_id, title, duration_seconds) VALUES 
(2, 'Faint', 162),
(2, 'Numb', 185),
(2, 'Breaking the Habit', 196);

-- Discovery (Album 3)
INSERT INTO tracks (album_id, title, duration_seconds) VALUES 
(3, 'One More Time', 320),
(3, 'Digital Love', 298),
(3, 'Harder, Better, Faster, Stronger', 224);

-- Random Access Memories (Album 4)
INSERT INTO tracks (album_id, title, duration_seconds) VALUES 
(4, 'Give Life Back to Music', 274),
(4, 'Get Lucky', 369),
(4, 'Instant Crush', 337);

-- After Hours (Album 5)
INSERT INTO tracks (album_id, title, duration_seconds) VALUES 
(5, 'Blinding Lights', 200),
(5, 'Save Your Tears', 215),
(5, 'In Your Eyes', 237);

-- Starboy (Album 6)
INSERT INTO tracks (album_id, title, duration_seconds) VALUES 
(6, 'Starboy', 230),
(6, 'I Feel It Coming', 269),
(6, 'Reminder', 218);

-- 4. Пользователи (Users)
INSERT INTO users (login, email, registration_date) VALUES 
('music_fan_99', 'fan@example.com', '2023-01-15'),
('johndoe_dev', 'john@provider.net', '2024-03-10');

-- 5. Плейлисты (Playlists)
-- User 1 (ID 1), User 2 (ID 2)
INSERT INTO playlists (user_id, title) VALUES 
(1, 'Morning Energy'),
(2, 'Late Night Vibes');

-- 6. Добавление треков в плейлисты (Playlist_Tracks)
INSERT INTO playlist_tracks (playlist_id, track_id) VALUES 
(1, 4), -- In the End
(1, 9), -- Harder, Better, Faster, Stronger
(1, 14), -- Blinding Lights
(2, 12), -- Instant Crush
(2, 18); -- Reminder

-- 7. История прослушиваний (Listening_History)
INSERT INTO listening_history (user_id, track_id, listened_at) VALUES 
(1, 4, '2026-04-01 08:30:00'),
(1, 14, '2026-04-01 08:35:00'),
(2, 12, '2026-04-02 23:15:00'),
(2, 18, '2026-04-02 23:20:00'),
(1, 9, '2026-04-03 10:00:00'),
(2, 12, '2026-04-03 23:45:00'),
(1, 4, '2026-04-04 09:15:00');