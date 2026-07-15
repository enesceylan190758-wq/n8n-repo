-- Sosyal post caption şablonları: güncel iletişim bilgileri
UPDATE social_post_templates
SET caption_template = replace(replace(caption_template, 'nefalixai@gmail.com', 'info@nefalix.com'), 'nefalixai.com', 'nefalix.com')
WHERE caption_template LIKE '%nefalixai%';

-- Mevcut pending/ready post caption'ları
UPDATE social_posts
SET caption = replace(replace(caption, 'nefalixai@gmail.com', 'info@nefalix.com'), 'nefalixai.com', 'nefalix.com')
WHERE caption LIKE '%nefalixai%';
