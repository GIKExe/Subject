-- 1. Топ-5 самых популярных треков
SELECT 
	t.title AS track_title,
	a.name AS artist_name,
	COUNT(lh.history_id) AS play_count
FROM listening_history lh
JOIN tracks t ON lh.track_id = t.track_id
JOIN albums al ON t.album_id = al.album_id
JOIN artists a ON al.artist_id = a.artist_id
GROUP BY t.track_id, t.title, a.name
ORDER BY play_count DESC
LIMIT 5;


-- 2. Любимый жанр каждого пользователя
WITH user_genre_counts AS (
	-- Считаем количество прослушиваний каждого жанра для каждого пользователя
	SELECT 
		u.login,
		art.genre,
		COUNT(*) AS genre_plays
	FROM users u
	JOIN listening_history lh ON u.user_id = lh.user_id
	JOIN tracks t ON lh.track_id = t.track_id
	JOIN albums alb ON t.album_id = alb.album_id
	JOIN artists art ON alb.artist_id = art.artist_id
	GROUP BY u.user_id, u.login, art.genre
),
ranked_genres AS (
	-- Ранжируем жанры внутри каждого пользователя
	SELECT 
		login,
		genre,
		genre_plays,
		RANK() OVER (PARTITION BY login ORDER BY genre_plays DESC) as rnk
	FROM user_genre_counts
)
-- Выбираем только те, что на первом месте
SELECT login, genre, genre_plays
FROM ranked_genres
WHERE rnk = 1;


-- 3. Скользящее среднее прослушиваний за последние 7 дней
WITH daily_stats AS (
	-- Группируем прослушивания по дням за последние 30 дней (для наглядности окна)
	SELECT 
		listened_at::date AS day,
		COUNT(*) AS daily_plays
	FROM listening_history
	WHERE listened_at >= CURRENT_DATE - INTERVAL '30 days'
	GROUP BY listened_at::date
)
SELECT 
	day,
	daily_plays,
	-- Вычисляем скользящее среднее за 7 дней
	ROUND(AVG(daily_plays) OVER (
		ORDER BY day 
		ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
	), 2) AS moving_avg_7d
FROM daily_stats
ORDER BY day DESC;